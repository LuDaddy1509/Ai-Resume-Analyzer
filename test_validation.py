"""
Quick test script to verify CV validation logic works correctly
"""

from backend.app.services.resume_validation_service import ResumeValidator

def test_cv_validation():
    validator = ResumeValidator()

    # Test 1: Valid CV text (English)
    valid_cv = """
    John Doe
    Email: john.doe@example.com
    Phone: +84 123 456 789

    PROFESSIONAL SUMMARY
    Experienced software engineer with 5 years in web development

    WORK EXPERIENCE
    Senior Developer at Tech Company
    01/2020 - Present
    - Developed microservices using Python and FastAPI
    - Led team of 5 developers

    EDUCATION
    Bachelor of Computer Science
    XYZ University
    2015 - 2019

    SKILLS
    Python, JavaScript, React, FastAPI, Docker, AWS
    """

    result = validator.validate(valid_cv)
    print("Test 1 - Valid English CV:")
    print(f"  Is Resume: {result.is_resume}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reason: {result.reason}")
    print()

    # Test 2: Valid CV text (Vietnamese)
    valid_cv_vn = """
    NGUYỄN VĂN A
    Email: nguyenvana@example.com
    Điện thoại: 0123456789

    MỤC TIÊU NGHỀ NGHIỆP
    Tìm kiếm vị trí lập trình viên Python

    KINH NGHIỆM LÀM VIỆC
    Lập trình viên - Công ty ABC
    01/2020 - Hiện tại
    - Phát triển ứng dụng web bằng Python
    - Quản lý cơ sở dữ liệu PostgreSQL

    HỌC VẤN
    Đại học Bách Khoa
    Cử nhân Công nghệ Thông tin
    2015 - 2019

    KỸ NĂNG
    Python, Java, SQL, Docker, Git
    """

    result = validator.validate(valid_cv_vn)
    print("Test 2 - Valid Vietnamese CV:")
    print(f"  Is Resume: {result.is_resume}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reason: {result.reason}")
    print()

    # Test 3: Invoice (should be rejected)
    invoice_text = """
    INVOICE
    Invoice Number: INV-2024-001
    Date: January 15, 2024

    Bill To:
    Company XYZ
    123 Street Address

    Item Description          Quantity    Price
    Consulting Services       10 hours    $100.00

    Subtotal: $1,000.00
    Tax: $100.00
    Total: $1,100.00

    Payment Terms: Net 30
    """

    result = validator.validate(invoice_text)
    print("Test 3 - Invoice (should reject):")
    print(f"  Is Resume: {result.is_resume}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reason: {result.reason}")
    print(f"  Error Code: {result.error_code}")
    print()

    # Test 4: Job Description (should be rejected)
    jd_text = """
    JOB DESCRIPTION

    Position: Senior Software Engineer
    Location: Ho Chi Minh City

    We are looking for a talented software engineer to join our team.

    Responsibilities:
    - Develop web applications
    - Write clean code
    - Collaborate with team

    Requirements:
    - 3+ years of experience
    - Strong Python skills
    - Knowledge of FastAPI

    We are seeking candidates who are passionate about technology.
    """

    result = validator.validate(jd_text)
    print("Test 4 - Job Description (should reject):")
    print(f"  Is Resume: {result.is_resume}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reason: {result.reason}")
    print(f"  Error Code: {result.error_code}")
    print()

    # Test 5: Empty document
    result = validator.validate("")
    print("Test 5 - Empty document (should reject):")
    print(f"  Is Resume: {result.is_resume}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reason: {result.reason}")
    print(f"  Error Code: {result.error_code}")
    print()

    # Test 6: Minimal CV (edge case)
    minimal_cv = """
    Jane Smith
    jane@email.com

    Experience
    Developer - 2020-2023

    Education
    Computer Science Degree

    Skills: Python, SQL
    """

    result = validator.validate(minimal_cv)
    print("Test 6 - Minimal CV (edge case):")
    print(f"  Is Resume: {result.is_resume}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reason: {result.reason}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("CV Validation Service Test")
    print("=" * 60)
    print()

    try:
        test_cv_validation()
        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
