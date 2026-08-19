import fitz
import re
import io
import docx
import os

# Thêm poppler path vào environment để pdf2image/OCR hoạt động
poppler_path = r"C:\Users\lhnhan\PycharmProjects\Ai_Resume_Analyzer\poppler-26.02.0\Library\bin"
if poppler_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] = poppler_path + ";" + os.environ.get("PATH", "")

from app.schemas.resume_schema import Resume, Experience, ResumeAnalysis

# Thư viện tùy chọn phục vụ cho OCR fallback của scanned PDF
try:
    from pdf2image import convert_from_bytes
except ImportError:
    convert_from_bytes = None

try:
    import pytesseract
except ImportError:
    pytesseract = None


# ─── Danh sách kỹ năng phổ biến để nhận diện ────────────────────────────────
KNOWN_SKILLS = [
    # Ngôn ngữ lập trình
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go",
    "Rust", "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    "Perl", "Dart", "Lua",
    # Web Frontend
    "React", "Vue", "Angular", "Next.js", "Nuxt.js", "HTML", "CSS",
    "Sass", "Tailwind", "Bootstrap", "jQuery", "Redux", "Webpack", "Vite",
    # Web Backend
    "FastAPI", "Django", "Flask", "Express", "NestJS", "Spring", "Laravel",
    "Rails", "ASP.NET", "Node.js", "GraphQL", "REST", "gRPC",
    # Database
    "SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Elasticsearch",
    "Cassandra", "DynamoDB", "Firebase", "Oracle", "MSSQL",
    # DevOps / Cloud
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Jenkins",
    "GitHub Actions", "Terraform", "Ansible", "Nginx", "Linux", "Bash",
    # Data / AI / ML
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras",
    "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Spark", "Hadoop",
    "Tableau", "Power BI", "Data Analysis", "NLP", "Computer Vision",
    # Tools
    "Git", "GitHub", "GitLab", "Jira", "Confluence", "Figma", "Postman",
    "VS Code", "IntelliJ", "PyCharm", "Excel", "Agile", "Scrum",
]

# ─── Từ khoá section Kỹ năng ─────────────────────────────────────────────────
SKILLS_HEADERS = [
    r"k[yỹ]\s*n[aă]ng", r"skills?", r"technical\s*skills?",
    r"technologies", r"competencies", r"expertise",
    r"công\s*ngh[eệ]", r"n[aă]ng\s*l[uự]c",
]

# ─── Từ khoá section Kinh nghiệm ─────────────────────────────────────────────
EXP_HEADERS = [
    r"kinh\s*nghi[eệ]m", r"experience", r"work\s*experience",
    r"employment", r"professional\s*experience",
    r"qu[aá]\s*tr[iì]nh\s*l[aà]m\s*vi[eệ]c",
]

# ─── Từ khoá section kết thúc kinh nghiệm ────────────────────────────────────
SECTION_BREAKERS = [
    r"gi[aá]o\s*d[uụ]c", r"education", r"k[yỹ]\s*n[aă]ng", r"skills?",
    r"d[uự]\s*[aá]n", r"projects?", r"ch[uứ]ng\s*ch[ỉi]", r"certifications?",
    r"gi[aả]i\s*th[uư][oở]ng", r"awards?", r"ho[aạ]t\s*[dđ][oộ]ng",
    r"references?", r"tham\s*kh[aả]o",
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    """Chuẩn hoá khoảng trắng, bỏ ký tự thừa."""
    return re.sub(r"\s+", " ", text).strip()


def _extract_text(file_bytes: bytes, filename: str) -> str:
    """Đọc text từ PDF (có hỗ trợ OCR) hoặc DOCX."""
    text = ""
    file_ext = filename.lower().split('.')[-1]

    if file_ext == "pdf":
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")

            # 1. Kiểm tra PDF có mật khẩu không (bao gồm cả mã hóa mật khẩu)
            if doc.is_encrypted:
                # Thử mở bằng mật khẩu rỗng, nếu thất bại nghĩa là file thực sự yêu cầu mật khẩu
                if doc.needs_pass or not doc.authenticate(""):
                    raise ValueError("File PDF này được bảo vệ bằng mật khẩu. Vui lòng gỡ bỏ mật khẩu trước khi tải lên.")

            for page in doc:
                text += page.get_text("text")

            # 2. Xử lý PDF dạng Scan (OCR Fallback)
            # Nếu bóc tách được quá ít chữ (dưới 50 ký tự), khả năng cao đây là ảnh scan
            if len(text.strip()) < 50:
                print("Phát hiện PDF dạng scan, đang khởi động OCR...")
                if convert_from_bytes is None or pytesseract is None:
                    raise ValueError("Không thể chạy OCR vì thiếu thư viện phụ thuộc (pdf2image hoặc pytesseract). Vui lòng chuyển đổi PDF sang dạng văn bản thông thường.")
                try:
                    # Chuyển PDF thành danh sách hình ảnh
                    images = convert_from_bytes(file_bytes)
                    text = ""
                    for img in images:
                        # Nhận diện cả tiếng Anh và tiếng Việt
                        text += pytesseract.image_to_string(img, lang="eng+vie")
                except Exception as e:
                    print(f"Lỗi khi chạy OCR: {e}")
                    raise ValueError("Không thể đọc được chữ từ file PDF scan này. Vui lòng kiểm tra lại chất lượng file.")

        except fitz.FileDataError:
            raise ValueError("File PDF bị hỏng hoặc không đúng định dạng.")

    elif file_ext == "docx":
        try:
            # Đọc file Word từ bytes
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise ValueError("Lỗi khi đọc file DOCX. Đảm bảo file không bị hỏng.")

    elif file_ext == "txt":
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            raise ValueError("Lỗi khi đọc file TXT. Đảm bảo file không bị hỏng.")

    elif file_ext in ("png", "jpg", "jpeg"):
        # OCR ảnh CV (ảnh chụp / scan ảnh trực tiếp)
        if pytesseract is None:
            raise ValueError("Không thể chạy OCR vì thiếu thư viện pytesseract. Vui lòng cài đặt tesseract.")
        try:
            from PIL import Image
            with Image.open(io.BytesIO(file_bytes)) as img:
                text = pytesseract.image_to_string(img, lang="eng+vie")
            if not text.strip():
                raise ValueError("Không đọc được chữ từ ảnh. Vui lòng kiểm tra lại chất lượng ảnh.")
        except ValueError as ve:
            raise ve
        except Exception:
            raise ValueError("Không thể đọc được file ảnh. Đảm bảo file là ảnh PNG hoặc JPG rõ nét.")

    else:
        raise ValueError("Định dạng file không được hỗ trợ.")

    return text


# ─── Trích xuất thông tin cá nhân ────────────────────────────────────────────

def _extract_email(text: str) -> str:
    """Extract email - lenient, handles OCR artifacts."""
    # Chuẩn pattern
    match = re.search(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", text)
    if match:
        return match.group(0).strip()

    # Fallback: OCR artifacts (@ -> a/at, . -> space/dot)
    match = re.search(r"([\w\-+]+\s*(?:a|at)\s*[\w\-]+\s*(?:\.|dot)\s*\w{2,})", text, re.IGNORECASE)
    if match:
        email = match.group(1)
        email = re.sub(r"\s*(?:a|at)\s*", "@", email, flags=re.IGNORECASE)
        email = re.sub(r"\s*(?:\.|dot)\s*", ".", email, flags=re.IGNORECASE)
        email = re.sub(r"\s+", "", email)
        if re.match(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", email):
            return email.lower()
    return ""


def _extract_phone(text: str) -> str:
    """Extract phone - supports VN and international formats (E.164)."""
    patterns = [
        # Việt Nam: +84, 84, 0
        r"(?:\+84|84|0)\s*[-.]?\s*\d{1,2}\s*[-.]?\s*\d{3}\s*[-.]?\s*\d{3,4}",
        r"(?:\+84|84|0)\s*[-.]?\s*\d{2}\s*[-.]?\s*\d{3}\s*[-.]?\s*\d{4}",
        # Quốc tế chung
        r"\+\d{1,3}\s*[-.]?\s*\(\d{1,4}\)\s*\d[\d\s\-\.]{5,12}",
        r"\+\d{1,3}\s*[-.]?\s*\d{1,4}\s*[-.]?\s*\d{3,4}\s*[-.]?\s*\d{4}",
        r"\b\d{3}\s*[-.]?\s*\d{3}\s*[-.]?\s*\d{4}\b",
        r"\b\d{10,11}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group(0)
            normalized = _normalize_phone(phone)
            if normalized:
                return normalized
    return ""


def _normalize_phone(phone: str) -> str:
    """Normalize phone to E.164 format (+country-code + number)."""
    digits = re.sub(r"\D", "", phone)
    
    if not digits:
        return ""
    
    # Việt Nam: 84xxxxxxxxx hoặc 0xxxxxxxxx
    if digits.startswith("84") and len(digits) in [11, 12]:
        return "+" + digits
    if digits.startswith("0") and len(digits) in [10, 11]:
        return "+84" + digits[1:]
    
    # US/Canada: 1xxxxxxxxxx
    if digits.startswith("1") and len(digits) == 11:
        return "+" + digits
    if len(digits) == 10:
        return "+1" + digits
    
    # Quốc tế: detect popular country codes
    if len(digits) >= 10 and len(digits) <= 15:
        country_codes = ["84", "1", "44", "33", "49", "86", "81", "82", "65", "60", "62", "63", "66", "886", "852", "853", "856", "855"]
        for cc in country_codes:
            if digits.startswith(cc) and len(digits) >= len(cc) + 7:
                return "+" + digits
    
    # Fallback: assume VN nếu 10-11 số bắt đầu bằng 0
    if len(digits) in [10, 11] and digits.startswith("0"):
        return "+84" + digits[1:]
    
    return ""


def _extract_full_name(text: str) -> str:
    """
    Extract full name - lenient, supports multiple formats:
    - Title Case: Nguyen Van A
    - UPPERCASE: NGUYEN VAN A
    - lowercase: nguyen van a (OCR reads all lower)
    - Compound names, middle names
    - With label: "Họ tên: Nguyen Van A"
    """
    lines = [_clean(l) for l in text.splitlines() if _clean(l)]
    
    if not lines:
        return ""
    
    # Skip patterns
    skip_patterns = [
        r"^(summary|objective|experience|education|skills?|profile|about|kinh nghi|h[oọ]c v[aấ]n|k[yỹ] n[aă]ng|contact|li[eê]n h[eệ]|address|[eé]mail|phone|tel|github|linkedin|portfolio|website)$",
        r"(date of birth|ng[aà]y sinh|gender|gi[oó]i t[ií]nh|nationality|qu[oô]c t[ií]ch|marital status|t[îi]nh tr[aạ]ng h[oọ]n)",
        r"[@:/\\]|http|www",
        r"\d{5,}",
    ]
    skip_regex = re.compile("|".join(skip_patterns), re.IGNORECASE)
    
    candidates = []
    
    # Heuristic 1: Scan first 12 lines (header area)
    for i, line in enumerate(lines[:12]):
        if len(line) < 2 or len(line) > 80:
            continue
        if skip_regex.search(line):
            continue
        
        words = line.split()
        if not (1 <= len(words) <= 8):
            continue
        
        score = 0
        # Position: first line highest score
        score += max(0, 12 - i) * 2
        
        # Format check
        if _is_likely_name(line, words):
            score += 15
        
        # Penalty for job titles
        if re.search(r"(?i)(engineer|developer|manager|director|analyst|designer|architect|intern|fresher|gi[aá]m [dđ][oố]c|tr[uo]?ng ph[oô]ng|team lead|tech lead)", line):
            score -= 8
        
        candidates.append((score, line.strip()))
    
    # Heuristic 2: Look for "Name:", "Họ tên:", "Tên:" label
    for line in lines[:20]:
        label_match = re.match(r"(?i)(full name|h[oọ]\s*t[eê]n|name|t[eê]n)\s*[:：]\s*(.+)", line)
        if label_match:
            name = label_match.group(2).strip()
            if 1 <= len(name.split()) <= 6:
                return _clean(name)
    
    # Pick best candidate
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return _clean(candidates[0][1])
    
    # Fallback: first line without skip patterns
    for line in lines[:5]:
        if not skip_regex.search(line) and 1 <= len(line.split()) <= 6:
            return _clean(line)
    
    return ""


def _is_likely_name(line: str, words: list) -> bool:
    """Check if line looks like a person's name."""
    if not words:
        return False
    
    # Pattern 1: Each word starts with uppercase (Title Case) - Latin + Vietnam
    title_case = all(re.match(r"^[A-ZÀ-Ỹ\u00C0-\u024F]", w) for w in words)
    
    # Pattern 2: ALL CAPS
    all_upper = all(w.isupper() for w in words) and len(words) >= 2
    
    # Pattern 3: Has Vietnamese diacritics (supports VN names)
    has_vietnamese = any(re.search(r"[À-Ỹà-ỹ]", w) for w in words)
    
    # Pattern 4: Compound names (Van, Thi, Duc, etc. in middle)
    has_compound = any(re.match(r"^(Van|Thi|Duc|Huynh|Ngoc|Minh|Bao|Quoc|Tuan|Anh|Hoang|Gia|Khanh|Duy|Thien|Phuc|Nhat|Trong|Chi|My|Lan|Hoa|Lien|Loan|Oanh|Phuong|Thao|Trang|Yen|Ngoc)$", w, re.IGNORECASE) for w in words[1:-1])
    
    return title_case or all_upper or (has_vietnamese and len(words) >= 2) or has_compound



def _extract_skills(text: str) -> list[str]:
    found = set()

    # 1. Tìm trong section "Kỹ năng / Skills"
    skills_section = _get_section(text, SKILLS_HEADERS, SECTION_BREAKERS + EXP_HEADERS)
    search_text = skills_section if skills_section else text

    text_upper = search_text.upper()
    for skill in KNOWN_SKILLS:
        # So khớp toàn từ, không phân biệt hoa thường
        pattern = r"(?<![A-Z0-9])" + re.escape(skill.upper()) + r"(?![A-Z0-9])"
        if re.search(pattern, text_upper):
            found.add(skill)

    # 2. Nếu không tìm được gì → quét toàn bộ văn bản
    if not found:
        text_upper_all = text.upper()
        for skill in KNOWN_SKILLS:
            pattern = r"(?<![A-Z0-9])" + re.escape(skill.upper()) + r"(?![A-Z0-9])"
            if re.search(pattern, text_upper_all):
                found.add(skill)

    return sorted(found)


# ─── Trích xuất kinh nghiệm ───────────────────────────────────────────────────

def _get_section(text: str, headers: list[str], breakers: list[str]) -> str:
    """Cắt đoạn văn bản từ header đến section tiếp theo."""
    header_pat = r"(?im)^[\s\•\-]*(?:" + "|".join(headers) + r")[:\s]*$"
    breaker_pat = r"(?im)^[\s\•\-]*(?:" + "|".join(breakers) + r")[:\s]*$"

    m_start = re.search(header_pat, text)
    if not m_start:
        return ""

    start = m_start.end()
    m_end = re.search(breaker_pat, text[start:])
    end = start + m_end.start() if m_end else len(text)

    return text[start:end].strip()


def _parse_date_range(line: str) -> str:
    """Trích chuỗi ngày tháng kiểu '01/2022 - 06/2023' hoặc 'Jan 2020 – Present'."""
    pattern = (
        r"(?:"
        r"\d{1,2}[/\-]\d{4}"          # 01/2022
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}"
        r"|(?:T\d{1,2}|Q\d)[/\-]\d{4}"
        r")"
        r"(?:\s*[-–—]\s*"
        r"(?:\d{1,2}[/\-]\d{4}"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}"
        r"|T\d{1,2}[/\-]\d{4}"
        r"|(?:present|now|nay|hiện tại|current))"
        r")?"
    )
    m = re.search(pattern, line, re.IGNORECASE)
    return _clean(m.group(0)) if m else ""


def _extract_experiences(text: str) -> list[Experience]:
    exp_section = _get_section(text, EXP_HEADERS, SECTION_BREAKERS)
    if not exp_section:
        return []

    lines = [_clean(l) for l in exp_section.splitlines()]
    lines = [l for l in lines if l]

    experiences: list[Experience] = []
    current: dict | None = None
    bullets: list[str] = []

    date_line_pat = re.compile(
        r"\d{1,2}[/\-]\d{4}"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}",
        re.IGNORECASE,
    )
    bullet_pat = re.compile(r"^[\-\•\*\+✓✔►▸→]\s+(.+)")
    company_keywords = re.compile(
        r"(?i)(company|corp|ltd|co\.|inc\.|llc|group|công\s*ty|tập\s*đoàn|"
        r"technology|tech|solutions?|systems?|software|services?|joint)",
    )

    def _save():
        if current:
            current["bullets"] = bullets[:]
            try:
                experiences.append(Experience(**current))
            except Exception:
                pass

    for line in lines:
        date_str = _parse_date_range(line)
        b_match = bullet_pat.match(line)

        if date_str:
            # Dòng chứa ngày → có thể là header của một entry mới
            _save()
            current = {
                "company": "",
                "position": _clean(re.sub(re.escape(date_str), "", line)),
                "dates": date_str,
                "bullets": [],
            }
            bullets = []
        elif current is not None and b_match:
            bullets.append(b_match.group(1))
        elif current is not None and company_keywords.search(line):
            if not current["company"]:
                current["company"] = line
            else:
                # Dòng mới không có ngày, không phải bullet → position / company
                if not current["position"]:
                    current["position"] = line
        elif current is not None and not current["position"] and len(line) < 80:
            current["position"] = line
        elif current is not None and not current["company"] and len(line) < 80:
            current["company"] = line

    _save()
    return experiences


# ─── Hàm chính ────────────────────────────────────────────────────────────────

def parse_resume_file(file_bytes: bytes, filename: str) -> Resume:
    """Truyền thêm filename để hàm nhận diện được định dạng"""
    # Gọi hàm _extract_text đã được nâng cấp
    text = _extract_text(file_bytes, filename)

    full_name = _extract_full_name(text)
    email = _extract_email(text)
    phone = _extract_phone(text)
    skills = _extract_skills(text)
    experiences = _extract_experiences(text)

    return Resume(
        full_name=full_name or "Không xác định",
        email=email or "",
        phone=phone or None,
        skills=skills,
        experiences=experiences,
    )


def analyze_resume_against_job(resume: Resume, job_description: str) -> ResumeAnalysis:
    """So sánh kỹ năng CV với JD để tính điểm match, kỹ năng thiếu và gợi ý."""
    if not job_description or not job_description.strip():
        # Nếu không có JD, trả về mặc định
        return ResumeAnalysis(
            match_score=100,
            matched_skills=resume.skills,
            missing_skills=[],
            suggestions=["Hãy bổ sung Job Description để nhận được gợi ý chi tiết và tính điểm tối ưu."]
        )

    # 1. Tìm các kỹ năng yêu cầu có trong JD
    required_skills = set()
    jd_upper = job_description.upper()
    for skill in KNOWN_SKILLS:
        pattern = r"(?<![A-Z0-9])" + re.escape(skill.upper()) + r"(?![A-Z0-9])"
        if re.search(pattern, jd_upper):
            required_skills.add(skill)

    if not required_skills:
        # Nếu không tìm thấy kỹ năng nào cụ thể trong JD, dùng danh sách kỹ năng của resume làm matched
        return ResumeAnalysis(
            match_score=50,
            matched_skills=[],
            missing_skills=[],
            suggestions=["Không nhận diện được từ khóa kỹ năng kỹ thuật cụ thể nào trong Job Description. Hãy thử viết chi tiết hơn."]
        )

    # 2. Phân loại kỹ năng
    resume_skills_set = set(resume.skills)
    matched = required_skills.intersection(resume_skills_set)
    missing = required_skills.difference(resume_skills_set)

    # 3. Tính điểm
    match_score = int((len(matched) / len(required_skills)) * 100)

    # 4. Tạo các gợi ý cụ thể
    suggestions = []
    if match_score == 100:
        suggestions.append("Tuyệt vời! Bạn có đầy đủ tất cả kỹ năng yêu cầu trong Job Description này.")
    else:
        suggestions.append(f"Điểm số của bạn là {match_score}%. Bạn cần bổ sung thêm kỹ năng phù hợp.")
        if missing:
            suggestions.append(f"Cân nhắc bổ sung các kỹ năng sau vào CV của bạn: {', '.join(list(missing)[:5])}.")

    if not resume.experiences:
        suggestions.append("CV của bạn hiện thiếu phần Kinh nghiệm làm việc chi tiết. Hãy mô tả rõ các dự án đã làm.")

    if not resume.phone:
        suggestions.append("Thiếu số điện thoại liên lạc. Hãy thêm số điện thoại để nhà tuyển dụng dễ liên hệ.")

    return ResumeAnalysis(
        match_score=match_score,
        matched_skills=sorted(list(matched)),
        missing_skills=sorted(list(missing)),
        suggestions=suggestions
    )




