from app import validate_person_payload

def test_first_name_length_invalid():
    data = {"first_name":"a","last_name":"Doe","email":"a@a.com","salary":50000,"birth_date":"2000-01-01","personal_code":"abcd1234"}
    errors = validate_person_payload(data, require_all=True)
    assert any(e["field"]=="first_name" for e in errors)

def test_personal_code_format_invalid():
    data = {"first_name":"John","last_name":"Doe","email":"a@a.com","salary":50000,"birth_date":"2000-01-01","personal_code":"!bad"}
    errors = validate_person_payload(data, require_all=True)
    assert any(e["field"]=="personal_code" for e in errors)