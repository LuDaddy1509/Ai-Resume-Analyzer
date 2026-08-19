from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
import os
import glob
import logging
import tiktoken

logger = logging.getLogger(__name__)


class ResumeRAG:
    DEFAULT_MAX_CONTEXT_TOKENS = 3000
    RESERVED_TOKENS = 500
    
    def __init__(self):
        self.embeddings = None
        self._semantic_available = False
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if api_key and api_key != "your_key_here" and "placeholder" not in api_key.lower():
            try:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=api_key
                )
                self._semantic_available = True
            except Exception as e:
                logger.warning("Embeddings init failed, using BM25 only: %s", e)
        else:
            logger.warning("GEMINI_API_KEY missing/placeholder, using BM25-only retrieval")

        self.vector_store = None
        self.bm25_retriever = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self._knowledge_dir = "./backend/app/rag/knowledge"
        self._persist_dir = "./chroma_db"
        self._initialized = False
        self._all_documents = []
        
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None

    def _count_tokens(self, text: str) -> int:
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text) // 4

    def load_knowledge_base(self, force_reload=False):
        if self._initialized and not force_reload:
            logger.info("Knowledge base already loaded, skipping...")
            return self.vector_store
            
        logger.info("Loading knowledge base from %s", self._knowledge_dir)
        
        doc_files = glob.glob(os.path.join(self._knowledge_dir, "**/*.md"), recursive=True)
        
        if not doc_files:
            logger.warning("No markdown files found, using default documents")
            return self._load_default_documents()
            
        documents = []
        for file_path in doc_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                metadata = {"source": file_path}
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        import yaml
                        try:
                            fm = yaml.safe_load(parts[1])
                            if fm:
                                metadata.update(fm)
                            content = parts[2].strip()
                        except Exception as e:
                            logger.warning("Failed to parse frontmatter in %s: %s", file_path, e)
                            
                metadata.setdefault("category", "general")
                metadata.setdefault("tags", [])
                metadata.setdefault("priority", "medium")
                
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
                
            except Exception as e:
                logger.error("Error loading %s: %s", file_path, e)
                
        if not documents:
            logger.warning("No valid documents loaded, using defaults")
            return self._load_default_documents()
            
        split_docs = self.text_splitter.split_documents(documents)
        self._all_documents = split_docs
        
        logger.info("Loaded %d documents, split into %d chunks", len(documents), len(split_docs))
        
        if self._semantic_available:
            self.vector_store = Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                persist_directory=self._persist_dir
            )
        
        # Create BM25 retriever for keyword search
        self.bm25_retriever = BM25Retriever.from_documents(split_docs)
        self.bm25_retriever.k = 5
        
        self._initialized = True
        logger.info("Knowledge base initialized successfully")
        return self.vector_store

    def _load_default_documents(self):
        documents = [
            "Best practices cho CV IT: Su dung bullet points, quantifiable achievements (tang 30%, giam 40%), tu khoa JD.",
            "ATS friendly: Trai table, header/footer phuc tap, dung font chuan (Arial, Calibri).",
            "Skill trends 2026: AI/ML, Cloud (AWS/Azure), Cybersecurity, Generative AI, System Design.",
            "STAR method: Situation, Task, Action, Result cho bullet points kinh nghiem.",
        ]
        
        split_docs = self.text_splitter.create_documents(documents)
        self._all_documents = split_docs
        
        if self._semantic_available:
            self.vector_store = Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                persist_directory=self._persist_dir
            )
        
        self.bm25_retriever = BM25Retriever.from_documents(split_docs)
        self.bm25_retriever.k = 5
        
        self._initialized = True
        return self.vector_store

    def _hybrid_retrieve(self, query: str, k: int) -> list:
        """Merge results from semantic search and BM25, deduplicated by content."""
        seen = set()
        merged = []

        if self._semantic_available and self.vector_store is not None:
            try:
                semantic_docs = self.vector_store.similarity_search(query, k=k)
            except Exception as e:
                logger.warning("Semantic search failed: %s", e)
                semantic_docs = []
        else:
            semantic_docs = []

        try:
            bm25_docs = self.bm25_retriever.get_relevant_documents(query)[:k]
        except Exception as e:
            logger.warning("BM25 search failed: %s", e)
            bm25_docs = []

        for doc in semantic_docs + bm25_docs:
            key = doc.page_content[:256]
            if key not in seen:
                seen.add(key)
                merged.append(doc)

        return merged[: max(k, 5)]

    def retrieve(self, query: str, k=3, use_hybrid=True):
        if not self._initialized:
            self.load_knowledge_base()
            
        if use_hybrid:
            return self._hybrid_retrieve(query, k)
        elif self._semantic_available and self.vector_store is not None:
            return self.vector_store.similarity_search(query, k=k)
        else:
            try:
                return self.bm25_retriever.get_relevant_documents(query)[:k]
            except Exception:
                return self._all_documents[:k]

    def get_context(self, query: str, resume_text: str = "", job_description: str = "", 
                   max_context_tokens: int = None, use_hybrid: bool = True) -> str:
        if max_context_tokens is None:
            max_context_tokens = self.DEFAULT_MAX_CONTEXT_TOKENS
            
        resume_tokens = self._count_tokens(resume_text)
        jd_tokens = self._count_tokens(job_description)
        available_tokens = max_context_tokens - resume_tokens - jd_tokens - self.RESERVED_TOKENS
        available_tokens = max(available_tokens, 500)
        
        logger.info("Token budget: %d for RAG context (resume: %d, JD: %d)", 
                   available_tokens, resume_tokens, jd_tokens)
        
        docs = self.retrieve(query, k=10, use_hybrid=use_hybrid)
        
        context_parts = []
        current_tokens = 0
        
        for doc in docs:
            doc_tokens = self._count_tokens(doc.page_content)
            if current_tokens + doc_tokens > available_tokens:
                remaining = available_tokens - current_tokens
                if remaining > 100:
                    truncated = self._truncate_to_tokens(doc.page_content, remaining)
                    context_parts.append(truncated)
                break
            context_parts.append(doc.page_content)
            current_tokens += doc_tokens
            
        context = "\n\n---\n\n".join(context_parts)
        logger.info("Built context: %d tokens from %d docs", current_tokens, len(context_parts))
        
        return context

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        if not self.tokenizer:
            return text[:max_tokens * 4] + "... [truncated]"
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= max_tokens:
            return text
        truncated_tokens = tokens[:max_tokens]
        return self.tokenizer.decode(truncated_tokens) + "... [truncated]"

    def rebuild_index(self):
        self.vector_store = None
        self.bm25_retriever = None
        self._all_documents = []
        self._initialized = False
        return self.load_knowledge_base(force_reload=True)

    def get_stats(self) -> dict:
        if not self._initialized:
            self.load_knowledge_base()
            
        categories = {}
        for doc in self._all_documents:
            cat = doc.metadata.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            
        return {
            "total_documents": len(self._all_documents),
            "categories": categories,
            "persist_directory": self._persist_dir,
            "embedding_model": "models/embedding-001",
        }