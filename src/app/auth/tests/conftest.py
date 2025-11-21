"""Pytest configuration and shared fixtures for auth tests."""
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from auth
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from datetime import datetime, timezone
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from auth.models import User
from auth.schema import SecurityQuestionsSchema, AccountStatusSchema, RoleChoicesSchema


@pytest.fixture(name="engine")
def engine_fixture():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a database session for testing."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_user_data():
    """Fixture providing sample user data for tests."""
    return {
        "username": "testuser123",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "id_no": 12345,
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$test",
        "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
        "security_answer": "Smith"
    }


@pytest.fixture
def create_test_user(session):
    """Factory fixture to create test users."""
    def _create_user(**kwargs):
        default_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$test",
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith"
        }
        default_data.update(kwargs)
        user = User(**default_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    return _create_user


@pytest.fixture
def customer_user(create_test_user):
    """Fixture providing a customer user."""
    return create_test_user(
        email="customer@example.com",
        username="customer123",
        role=RoleChoicesSchema.CUSTOMER,
        account_status=AccountStatusSchema.ACTIVE,
        is_active=True
    )


@pytest.fixture
def admin_user(create_test_user):
    """Fixture providing an admin user."""
    return create_test_user(
        email="admin@example.com",
        username="admin123",
        role=RoleChoicesSchema.ADMIN,
        account_status=AccountStatusSchema.ACTIVE,
        is_active=True,
        is_superuser=True
    )


@pytest.fixture
def inactive_user(create_test_user):
    """Fixture providing an inactive user."""
    return create_test_user(
        email="inactive@example.com",
        username="inactive123",
        account_status=AccountStatusSchema.INACTIVE,
        is_active=False
    )


@pytest.fixture
def locked_user(create_test_user):
    """Fixture providing a locked user."""
    return create_test_user(
        email="locked@example.com",
        username="locked123",
        account_status=AccountStatusSchema.LOCKED,
        is_active=False,
        failed_login_attempts=5
    )


@pytest.fixture
def deleted_user(create_test_user):
    """Fixture providing a soft-deleted user."""
    user = create_test_user(
        email="deleted@example.com",
        username="deleted123"
    )
    # Manually set deleted_at since it might not be in the constructor
    user.deleted_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def user_with_otp(create_test_user):
    """Fixture providing a user with OTP set."""
    from datetime import timedelta
    from auth.utils import generate_random_otp
    
    otp = generate_random_otp()
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    return create_test_user(
        email="otp@example.com",
        username="otpuser123",
        otp=otp,
        otp_expiry_at=otp_expiry
    )


@pytest.fixture
def multiple_role_users(create_test_user):
    """Fixture providing users with different roles."""
    roles = [
        RoleChoicesSchema.CUSTOMER,
        RoleChoicesSchema.ACCOUNT_EXECUTIVE,
        RoleChoicesSchema.BRANCH_MANAGER,
        RoleChoicesSchema.ADMIN,
        RoleChoicesSchema.SUPER_ADMIN,
        RoleChoicesSchema.TELLER
    ]
    
    users = []
    for i, role in enumerate(roles):
        user = create_test_user(
            email=f"{role.value}@example.com",
            username=f"{role.value}_{i}",
            role=role,
            id_no=10000 + i
        )
        users.append(user)
    
    return users


@pytest.fixture
def user_with_middle_name(create_test_user):
    """Fixture providing a user with middle name."""
    return create_test_user(
        email="middlename@example.com",
        username="middle123",
        first_name="John",
        middle_name="Michael",
        last_name="Doe"
    )
