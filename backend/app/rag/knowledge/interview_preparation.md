---
category: interview_preparation
tags: [interview, behavioral, technical, system_design, star_method, preparation]
source: hiring_manager_guides
priority: medium
---

# Interview Preparation Guide

## Behavioral Questions - STAR Method

### Cấu trúc trả lời STAR
- **S**ituation: Bối cảnh (1-2 câu)
- **T**ask: Nhiệm vụ/Thách thức (1 câu)
- **A**ction: Hành động CỤ THỂ bạn làm (3-5 câu) - PHẦN QUAN TRỌNG NHẤT
- **R**esult: Kết quả ĐỊNH LƯỢNG (metrics, impact)

### Top 10 Behavioral Questions
1. "Tell me about a challenging project you worked on"
2. "Describe a time you disagreed with a manager/peer"
3. "Tell me about a time you failed"
4. "Describe a situation where you had to learn something quickly"
5. "Tell me about a time you improved a process/system"
6. "Give an example of leading a project/team"
7. "Describe handling a difficult stakeholder"
8. "Tell me about a technical debt you resolved"
9. "Describe a time you had to make a trade-off decision"
10. "Why do you want to leave your current role?"

### Sample STAR Answer (Challenge Project)
**S**: "At Company X, our payment processing system handled 10k transactions/day but latency was 2.3s avg, causing 15% timeout rate during peak."
**T**: "As lead backend engineer, I was tasked to reduce latency to <200ms and timeout <1%."
**A**: "I profiled the system, found 3 bottlenecks: (1) synchronous external API calls, (2) N+1 database queries, (3) no caching. I: refactored to async/await with circuit breaker, implemented batch queries using UNION, added Redis caching layer with TTL strategy, set up distributed tracing with Jaeger."
**R**: "Latency dropped to 180ms p99, timeout rate to 0.3%, saved $40k/month in infrastructure costs. Pattern adopted by 3 other teams."

## Technical Interview Categories

### 1. Data Structures & Algorithms
- **Must know**: Arrays, Hash Maps, Two Pointers, Sliding Window, Binary Search, Trees/Graphs (BFS/DFS), Heaps, Dynamic Programming basics
- **Pattern recognition**: Learn 15-20 patterns, not 200 problems
- **Communication**: Think out loud, clarify constraints, discuss trade-offs before coding

### 2. System Design (Senior+)
**Framework**: Requirements → API Design → Data Model → High-level Arch → Deep Dive → Scale/Bottlenecks
**Key concepts**: CAP theorem, Consistency models, Sharding, Replication, Caching strategies, Load balancing, Message queues, CDN, Rate limiting, Circuit breaker
**Practice**: Design URL Shortener, Rate Limiter, Notification System, Feed/Timeline, Chat App, Search Engine

### 3. Domain-Specific (Backend/Frontend/ML/DevOps)
- **Backend**: Database design, API design, Concurrency, Distributed systems, Microservices patterns
- **Frontend**: React internals, Performance, State management, Accessibility, Testing
- **ML**: Model deployment, Feature stores, Monitoring, A/B testing, Data pipelines
- **DevOps**: CI/CD, Kubernetes, Observability, Security, Cost optimization

## Questions to Ask Interviewer
**About Role**: "What does success look like in first 90 days?" "Biggest challenge team facing?"
**About Tech**: "Tech debt priorities?" "How do you handle on-call?" "Deployment process?"
**About Culture**: "How are decisions made?" "Learning budget?" "Recent failure and what learned?"
**About Growth**: "Promotion path?" "Mentorship program?" "Cross-team collaboration?"

## Red Flags từ Employer
- Không mô tả rõ tech stack / архитектура
- "We move fast and break things" tanpa quy trình
- Không có code review / CI / testing
- On-call burden cao, không compensation
- High turnover trong team
- Không cho hỏi về challenges/failures
