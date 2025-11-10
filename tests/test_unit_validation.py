from app import validate_product_payload

def test_name_length_invalid():
    data = {"name":"ab","email":"a@a.com","price":10,"birthDate":"2000-01-01","code":"abcd"}
    errors = validate_product_payload(data, require_all=True)
    assert any(e["field"]=="name" for e in errors)

def test_code_format_invalid():
    data = {"name":"John Doe","email":"a@a.com","price":10,"birthDate":"2000-01-01","code":"!bad"}
    errors = validate_product_payload(data, require_all=True)
    assert any(e["field"]=="code" for e in errors)
