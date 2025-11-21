"""Tests for authentication schemas."""
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from auth
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import uuid
import pytest
from pydantic import ValidationError

from auth.schema import (
    SecurityQuestionsSchema,
    AccountStatusSchema,
    RoleChoicesSchema,
    BaseUserSchema,
    UserCreateSchema,
    UserReadSchema
)
from core.domain.exceptions import InvalidPasswordException


class TestSecurityQuestionsSchema:
    """Tests for SecurityQuestionsSchema enum."""

    def test_enum_values(self):
        """Test that all expected enum values exist."""
        expected_values = [
            "mothers_maiden_name",
            "first_pet_name",
            "favorite_teacher",
            "birth_city",
            "favorite_book"
        ]
        
        actual_values = [item.value for item in SecurityQuestionsSchema]
        assert set(actual_values) == set(expected_values)

    def test_get_description_valid_values(self):
        """Test get_description returns correct descriptions."""
        test_cases = [
            (SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME, "What is your mother's maiden name?"),
            (SecurityQuestionsSchema.FIRST_PET_NAME, "What was the name of your first pet?"),
            (SecurityQuestionsSchema.FAVORITE_TEACHER, "Who was your favorite teacher?"),
            (SecurityQuestionsSchema.BIRTH_CITY, "In which city were you born?"),
            (SecurityQuestionsSchema.FAVORITE_BOOK, "What is your favorite book?"),
        ]
        
        for question, expected_description in test_cases:
            assert SecurityQuestionsSchema.get_description(question) == expected_description

    def test_enum_members(self):
        """Test that enum members can be accessed by name."""
        assert SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME.value == "mothers_maiden_name"
        assert SecurityQuestionsSchema.FIRST_PET_NAME.value == "first_pet_name"
        assert SecurityQuestionsSchema.FAVORITE_TEACHER.value == "favorite_teacher"
        assert SecurityQuestionsSchema.BIRTH_CITY.value == "birth_city"
        assert SecurityQuestionsSchema.FAVORITE_BOOK.value == "favorite_book"


class TestAccountStatusSchema:
    """Tests for AccountStatusSchema enum."""

    def test_enum_values(self):
        """Test that all expected enum values exist."""
        expected_values = ["active", "inactive", "locked", "pending"]
        actual_values = [item.value for item in AccountStatusSchema]
        assert set(actual_values) == set(expected_values)

    def test_enum_members(self):
        """Test that enum members can be accessed by name."""
        assert AccountStatusSchema.ACTIVE.value == "active"
        assert AccountStatusSchema.INACTIVE.value == "inactive"
        assert AccountStatusSchema.LOCKED.value == "locked"
        assert AccountStatusSchema.PENDING.value == "pending"


class TestRoleChoicesSchema:
    """Tests for RoleChoicesSchema enum."""

    def test_enum_values(self):
        """Test that all expected enum values exist."""
        expected_values = [
            "customer",
            "account_executive",
            "branch_manager",
            "admin",
            "super_admin",
            "teller"
        ]
        actual_values = [item.value for item in RoleChoicesSchema]
        assert set(actual_values) == set(expected_values)

    def test_enum_members(self):
        """Test that enum members can be accessed by name."""
        assert RoleChoicesSchema.CUSTOMER.value == "customer"
        assert RoleChoicesSchema.ACCOUNT_EXECUTIVE.value == "account_executive"
        assert RoleChoicesSchema.BRANCH_MANAGER.value == "branch_manager"
        assert RoleChoicesSchema.ADMIN.value == "admin"
        assert RoleChoicesSchema.SUPER_ADMIN.value == "super_admin"
        assert RoleChoicesSchema.TELLER.value == "teller"


class TestBaseUserSchema:
    """Tests for BaseUserSchema."""

    def test_valid_base_user_creation(self):
        """Test creating a valid base user schema."""
        user_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith"
        }
        
        user = BaseUserSchema(**user_data)
        
        assert user.username == "testuser123"
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.id_no == 12345
        assert user.is_active is False
        assert user.is_superuser is False
        assert user.account_status == AccountStatusSchema.INACTIVE
        assert user.role == RoleChoicesSchema.CUSTOMER

    def test_base_user_with_middle_name(self):
        """Test creating user with middle name."""
        user_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "first_name": "John",
            "middle_name": "Michael",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.FIRST_PET_NAME,
            "security_answer": "Fluffy"
        }
        
        user = BaseUserSchema(**user_data)
        assert user.middle_name == "Michael"

    def test_base_user_without_username(self):
        """Test creating user without username (optional field)."""
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.BIRTH_CITY,
            "security_answer": "New York"
        }
        
        user = BaseUserSchema(**user_data)
        assert user.username is None

    def test_invalid_email(self):
        """Test that invalid email raises ValidationError."""
        user_data = {
            "email": "invalid-email",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith"
        }
        
        with pytest.raises(ValidationError):
            BaseUserSchema(**user_data)

    def test_id_no_must_be_positive(self):
        """Test that id_no must be greater than 0."""
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 0,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith"
        }
        
        with pytest.raises(ValidationError):
            BaseUserSchema(**user_data)

    def test_username_max_length(self):
        """Test username max length validation."""
        user_data = {
            "username": "a" * 13,  # More than 12 characters
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith"
        }
        
        with pytest.raises(ValidationError):
            BaseUserSchema(**user_data)

    def test_name_max_lengths(self):
        """Test first, middle, and last name max lengths."""
        # First name too long
        with pytest.raises(ValidationError):
            BaseUserSchema(
                email="test@example.com",
                first_name="a" * 31,
                last_name="Doe",
                id_no=12345,
                security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
                security_answer="Smith"
            )

        # Last name too long
        with pytest.raises(ValidationError):
            BaseUserSchema(
                email="test@example.com",
                first_name="John",
                last_name="a" * 31,
                id_no=12345,
                security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
                security_answer="Smith"
            )

        # Middle name too long
        with pytest.raises(ValidationError):
            BaseUserSchema(
                email="test@example.com",
                first_name="John",
                middle_name="a" * 31,
                last_name="Doe",
                id_no=12345,
                security_question=SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
                security_answer="Smith"
            )


class TestUserCreateSchema:
    """Tests for UserCreateSchema."""

    def test_valid_user_creation(self):
        """Test creating a valid user with matching passwords."""
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        
        user = UserCreateSchema(**user_data)
        assert user.password == "SecurePass123!"
        assert user.confirm_password == "SecurePass123!"

    def test_passwords_do_not_match(self):
        """Test that mismatched passwords raise InvalidPasswordException."""
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith",
            "password": "SecurePass123!",
            "confirm_password": "DifferentPass456!"
        }
        
        with pytest.raises(InvalidPasswordException) as exc_info:
            UserCreateSchema(**user_data)
        
        assert "Passwords do not match" in str(exc_info.value)

    def test_password_min_length(self):
        """Test password minimum length validation."""
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith",
            "password": "Short1!",  # Less than 8 characters
            "confirm_password": "Short1!"
        }
        
        with pytest.raises(ValidationError):
            UserCreateSchema(**user_data)

    def test_password_max_length(self):
        """Test password maximum length validation."""
        long_password = "a" * 129  # More than 128 characters
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith",
            "password": long_password,
            "confirm_password": long_password
        }
        
        with pytest.raises(ValidationError):
            UserCreateSchema(**user_data)

    def test_inherits_base_user_schema_fields(self):
        """Test that UserCreateSchema inherits all BaseUserSchema fields."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "John",
            "middle_name": "Michael",
            "last_name": "Doe",
            "id_no": 12345,
            "is_active": True,
            "is_superuser": True,
            "security_question": SecurityQuestionsSchema.FIRST_PET_NAME,
            "security_answer": "Fluffy",
            "account_status": AccountStatusSchema.ACTIVE,
            "role": RoleChoicesSchema.ADMIN,
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        
        user = UserCreateSchema(**user_data)
        assert user.username == "testuser"
        assert user.middle_name == "Michael"
        assert user.is_active is True
        assert user.is_superuser is True
        assert user.account_status == AccountStatusSchema.ACTIVE
        assert user.role == RoleChoicesSchema.ADMIN


class TestUserReadSchema:
    """Tests for UserReadSchema."""

    def test_valid_user_read_schema(self):
        """Test creating a valid UserReadSchema."""
        user_id = uuid.uuid4()
        user_data = {
            "id": user_id,
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith",
            "full_name": "John Doe"
        }
        
        user = UserReadSchema(**user_data)
        assert user.id == user_id
        assert user.full_name == "John Doe"
        assert user.email == "test@example.com"

    def test_user_read_schema_with_middle_name(self):
        """Test UserReadSchema with middle name in full_name."""
        user_id = uuid.uuid4()
        user_data = {
            "id": user_id,
            "email": "test@example.com",
            "first_name": "John",
            "middle_name": "Michael",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith",
            "full_name": "John Michael Doe"
        }
        
        user = UserReadSchema(**user_data)
        assert user.full_name == "John Michael Doe"
        assert user.middle_name == "Michael"

    def test_id_is_uuid(self):
        """Test that id must be a valid UUID."""
        user_data = {
            "id": "not-a-uuid",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "id_no": 12345,
            "security_question": SecurityQuestionsSchema.MOTHERS_MAIDEN_NAME,
            "security_answer": "Smith",
            "full_name": "John Doe"
        }
        
        with pytest.raises(ValidationError):
            UserReadSchema(**user_data)

    def test_inherits_base_user_schema_fields(self):
        """Test that UserReadSchema inherits all BaseUserSchema fields."""
        user_id = uuid.uuid4()
        user_data = {
            "id": user_id,
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "John",
            "middle_name": "Michael",
            "last_name": "Doe",
            "id_no": 12345,
            "is_active": True,
            "is_superuser": False,
            "security_question": SecurityQuestionsSchema.FIRST_PET_NAME,
            "security_answer": "Fluffy",
            "account_status": AccountStatusSchema.ACTIVE,
            "role": RoleChoicesSchema.CUSTOMER,
            "full_name": "John Michael Doe"
        }
        
        user = UserReadSchema(**user_data)
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.account_status == AccountStatusSchema.ACTIVE
        assert user.role == RoleChoicesSchema.CUSTOMER
