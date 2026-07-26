from app.services.parser_service import _extract_email, _extract_phone, _extract_full_name, _normalize_phone

# Test email
tests = [
    'Email: nguyen.van.a@gmail.com',
    'Email: nguyen van a @ gmail . com',
    'Email: nguyen van a at gmail dot com',
]
for t in tests:
    print(f"Email: {_extract_email(t)}")

# Test phone
tests = [
    'Phone: 0901234567',
    'Phone: +84 90 123 4567',
    'Phone: +84 28 1234 5678',
    'Phone: (028) 1234 5678',
]
for t in tests:
    print(f"Phone: {_extract_phone(t)}")

# Test name
tests = [
    'NGUYEN VAN A\nEmail: a@gmail.com',
    'Nguyen Van B\nExperience: 5 years',
    'Ho Ten: Tran Thi C\nPhone: 0901234567',
    'le van d\nskill: python',
]
for t in tests:
    print(f"Name: {_extract_full_name(t)}")
