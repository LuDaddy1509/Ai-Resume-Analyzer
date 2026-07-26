# ─── Trích xuất thông tin cá nhân ────────────────────────────────────────────

def _extract_email(text: str) -> str:
    \"\"\"Extract email - lenient, handles OCR artifacts.\"\"\"
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
    \"\"\"Extract phone - supports VN and international formats (E.164).\"\"\"
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
    \"\"\"Normalize phone to E.164 format (+country-code + number).\"\"\"
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
    \"\"\"
    Extract full name - lenient, supports multiple formats:
    - Title Case: Nguyen Van A
    - UPPERCASE: NGUYEN VAN A
    - lowercase: nguyen van a (OCR reads all lower)
    - Compound names, middle names
    - With label: "Họ tên: Nguyen Van A"
    \"\"\"
    lines = [_clean(l) for l in text.splitlines() if _clean(l)]
    
    if not lines:
        return ""
    
    # Skip patterns
    skip_patterns = [
        r"(?i)^(summary|objective|experience|education|skills?|profile|about|kinh nghi|h[oọ]c v[aấ]n|k[yỹ] n[aă]ng|contact|li[eê]n h[eệ]|address|[eé]mail|phone|tel|github|linkedin|portfolio|website)$",
        r"(?i)(date of birth|ng[aà]y sinh|gender|gi[oó]i t[ií]nh|nationality|qu[oô]c t[ií]ch|marital status|t[îi]nh tr[aạ]ng h[oọ]n)",
        r"[@:/\\]|http|www",
        r"\d{5,}",
    ]
    skip_regex = re.compile("|".join(skip_patterns))
    
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
    \"\"\"Check if line looks like a person's name.\"\"\"
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
