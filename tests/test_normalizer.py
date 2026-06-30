import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.normalizer import normalize_phone, normalize_email, normalize_country, normalize_skill, normalize_date

def test_normalize_phone():
    assert normalize_phone("(415) 555-0123")[0] == "+14155550123"
    assert normalize_phone("+1-650-555-0198")[0] == "+16505550198"
    assert normalize_phone("4085550167")[0] == "+14085550167"
    assert normalize_phone("N/A")[0] is None
    print("✓ Phone normalization tests passed")

def test_normalize_email():
    assert normalize_email("Alice.Johnson@Email.com")[0] == "alice.johnson@email.com"
    assert normalize_email("test@example.com")[0] == "test@example.com"
    assert normalize_email("")[0] is None
    print("✓ Email normalization tests passed")

def test_normalize_country():
    assert normalize_country("United States")[0] == "US"
    assert normalize_country("USA")[0] == "US"
    assert normalize_country("India")[0] == "IN"
    assert normalize_country("")[0] is None
    print("✓ Country normalization tests passed")

def test_normalize_skill():
    assert normalize_skill("javascript")[0] == "JavaScript"
    assert normalize_skill("react.js")[0] == "React"
    assert normalize_skill("Python")[0] == "Python"
    assert normalize_skill("k8s")[0] == "Kubernetes"
    print("✓ Skill normalization tests passed")

def test_normalize_date():
    assert normalize_date("2020-01")[0] == "2020-01"
    assert normalize_date("Jan 2020")[0] == "2020-01"
    assert normalize_date("2020")[0] == "2020-01"
    assert normalize_date("present")[0] == "present"
    print("✓ Date normalization tests passed")

if __name__ == '__main__':
    test_normalize_phone()
    test_normalize_email()
    test_normalize_country()
    test_normalize_skill()
    test_normalize_date()
    print("\n✅ All normalizer tests passed!")
