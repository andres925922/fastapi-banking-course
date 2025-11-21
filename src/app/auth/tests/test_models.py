"""Tests for authentication models."""
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from auth
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import uuid
import pytest
from datetime import datetime, timezone, timedelta
from sqlmodel import Field, Session, create_engine, SQLModel

from auth.models import User
from auth.schema import (
    SecurityQuestionsSchema,
    AccountStatusSchema,
    RoleChoicesSchema
)


class TestUserModel:
    """Tests for User model."""

    @pytest.fixture
    def sample_user_data(self):
        """Fixture providing sample user data."""
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

    def test_user_model_creation(self, sample_user_data):
        """Test creating a User model instance."""
        user = User(**sample_user_data)
        
        assert user.username == "testuser123"
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.id_no == 12345
        assert user.hashed_password == "$argon2id$v=19$m=65536,t=3,p=4$test"
        assert user.security_question == SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME
        assert user.security_answer == "Smith"

    def test_user_model_defaults(self, sample_user_data):
        """Test User model default values."""
        user = User(**sample_user_data)
        
        assert user.failed_login_attempts == 0
        assert user.last_failed_login is None
        assert user.otp == ""
        assert user.otp_expiry_at is None
        assert user.is_active is False
        assert user.is_superuser is False
        assert user.account_status == AccountStatusSchema.INACTIVE
        assert user.role == RoleChoicesSchema.CUSTOMER
        assert user.deleted_at is None

    def test_user_model_with_middle_name(self, sample_user_data):
        """Test User model with middle name."""
        sample_user_data["middle_name"] = "Michael"
        user = User(**sample_user_data)
        
        assert user.middle_name == "Michael"

    def test_user_model_failed_login_attempts(self, sample_user_data):
        """Test setting failed login attempts."""
        sample_user_data["failed_login_attempts"] = 3
        user = User(**sample_user_data)
        
        assert user.failed_login_attempts == 3

    def test_user_model_last_failed_login(self, sample_user_data):
        """Test setting last failed login timestamp."""
        now = datetime.now(timezone.utc)
        sample_user_data["last_failed_login"] = now
        user = User(**sample_user_data)
        
        assert user.last_failed_login == now

    def test_user_model_otp_fields(self, sample_user_data):
        """Test OTP fields."""
        otp = "123456"
        otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        sample_user_data["otp"] = otp
        sample_user_data["otp_expiry_at"] = otp_expiry
        user = User(**sample_user_data)
        
        assert user.otp == otp
        assert user.otp_expiry_at == otp_expiry

    def test_user_id_is_uuid(self, sample_user_data):
        """Test that user ID is automatically generated as UUID."""
        user = User(**sample_user_data)
        
        assert isinstance(user.id, uuid.UUID)

    def test_user_timestamp_fields(self, sample_user_data):
        """Test that timestamp fields are automatically set."""
        user = User(**sample_user_data)
        
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.created_at.tzinfo is not None  # Has timezone
        assert user.updated_at.tzinfo is not None


class TestUserFullNameProperty:
    """Tests for User.full_name computed property."""

    def test_full_name_without_middle_name(self):
        """Test full_name property without middle name."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith"
        )
        
        assert user.full_name == "John  Doe"

    def test_full_name_with_middle_name(self):
        """Test full_name property with middle name."""
        user = User(
            email="test@example.com",
            first_name="John",
            middle_name="Michael",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith"
        )
        
        assert user.full_name == "John Michael Doe"

    def test_full_name_with_empty_middle_name(self):
        """Test full_name property with empty string middle name."""
        user = User(
            email="test@example.com",
            first_name="John",
            middle_name="",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith"
        )
        
        # Empty string is falsy, so it won't be included
        assert user.full_name == "John  Doe"

    def test_full_name_is_computed_field(self):
        """Test that full_name is a computed field and not stored."""
        user = User(
            email="test@example.com",
            first_name="Jane",
            middle_name="Marie",
            last_name="Smith",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.FIRST_PET_NAME,
            security_answer="Fluffy"
        )
        
        # Verify the computed field returns the correct value
        assert user.full_name == "Jane Marie Smith"
        
        # Change first name and verify full_name updates
        user.first_name = "Jennifer"
        assert user.full_name == "Jennifer Marie Smith"


class TestUserIsDeletedProperty:
    """Tests for User.is_deleted computed property."""

    def test_is_deleted_when_deleted_at_is_none(self):
        """Test is_deleted returns False when deleted_at is None."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith"
        )
        
        assert user.is_deleted is False

    def test_is_deleted_when_deleted_at_is_set(self):
        """Test is_deleted returns True when deleted_at is set."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith",
            deleted_at=datetime.now(timezone.utc) #type: ignore
        )
        
        assert user.is_deleted is True

    def test_is_deleted_changes_with_deleted_at(self):
        """Test is_deleted updates when deleted_at changes."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith"
        )
        
        assert user.is_deleted is False
        
        # Soft delete the user
        user.deleted_at = datetime.now(timezone.utc)
        assert user.is_deleted is True
        
        # Restore the user
        user.deleted_at = None
        assert user.is_deleted is False


class TestUserHasRoleMethod:
    """Tests for User.has_role method."""

    def test_has_role_customer(self):
        """Test has_role returns True for matching customer role."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith",
            role=RoleChoicesSchema.CUSTOMER
        )
        
        assert user.has_role(RoleChoicesSchema.CUSTOMER) is True
        assert user.has_role(RoleChoicesSchema.ADMIN) is False

    def test_has_role_admin(self):
        """Test has_role returns True for matching admin role."""
        user = User(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            id_no=54321,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith",
            role=RoleChoicesSchema.ADMIN
        )
        
        assert user.has_role(RoleChoicesSchema.ADMIN) is True
        assert user.has_role(RoleChoicesSchema.CUSTOMER) is False

    def test_has_role_all_roles(self):
        """Test has_role with all available roles."""
        roles = [
            RoleChoicesSchema.CUSTOMER,
            RoleChoicesSchema.ACCOUNT_EXECUTIVE,
            RoleChoicesSchema.BRANCH_MANAGER,
            RoleChoicesSchema.ADMIN,
            RoleChoicesSchema.SUPER_ADMIN,
            RoleChoicesSchema.TELLER
        ]
        
        for role in roles:
            user = User(
                email=f"{role.value}@example.com",
                first_name="Test",
                last_name="User",
                id_no=12345,
                hashed_password="hashed",
                security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
                security_answer="Smith",
                role=role
            )
            
            # Should match the assigned role
            assert user.has_role(role) is True
            
            # Should not match other roles
            for other_role in roles:
                if other_role != role:
                    assert user.has_role(other_role) is False

    def test_has_role_compares_values(self):
        """Test that has_role compares enum values correctly."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith",
            role=RoleChoicesSchema.TELLER
        )
        
        # Verify it compares the actual values
        assert user.role.value == RoleChoicesSchema.TELLER.value
        assert user.has_role(RoleChoicesSchema.TELLER) is True


class TestUserModelConstraints:
    """Tests for User model field constraints and validations."""

    def test_failed_login_attempts_non_negative(self):
        """Test that failed_login_attempts must be non-negative."""
        # This should work (0 is valid)
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith",
            failed_login_attempts=0
        )
        assert user.failed_login_attempts == 0

    def test_hashed_password_max_length(self):
        """Test hashed_password max length."""
        long_hash = "a" * 256
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            id_no=12345,
            hashed_password=long_hash,
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith"
        )
        assert len(user.hashed_password) == 256

    def test_otp_max_length(self):
        """Test OTP max length of 6."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            id_no=12345,
            hashed_password="hashed",
            security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            security_answer="Smith",
            otp="123456"
        )
        assert user.otp == "123456"

    def test_all_security_questions(self):
        """Test user creation with all security questions."""
        questions = list(SecurityQuestionsSchema)
        
        for question in questions:
            user = User(
                email=f"{question.value}@example.com",
                first_name="John",
                last_name="Doe",
                id_no=12345,
                hashed_password="hashed",
                security_question=question,
                security_answer="answer"
            )
            assert user.security_question == question

    def test_all_account_statuses(self):
        """Test user creation with all account statuses."""
        statuses = list(AccountStatusSchema)
        
        for status in statuses:
            user = User(
                email=f"{status.value}@example.com",
                first_name="John",
                last_name="Doe",
                id_no=12345,
                hashed_password="hashed",
                security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
                security_answer="Smith",
                account_status=status
            )
            assert user.account_status == status
