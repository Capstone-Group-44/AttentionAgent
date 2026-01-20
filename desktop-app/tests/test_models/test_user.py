from model.user import User

def test_user_creation():
    user = User(
        uid="123",
        username="testuser",
        email="test@example.com",
        display_name="Test User",
        created_at="2023-01-01T00:00:00"
    )
    
    assert user.uid == "123"
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.display_name == "Test User"
    assert user.created_at == "2023-01-01T00:00:00"

def test_user_creation_optional_fields():
    user = User(
        uid="456",
        username="diffuser",
        email="diff@example.com"
    )
    
    assert user.uid == "456"
    assert user.username == "diffuser"
    assert user.display_name is None
    assert user.created_at is None
