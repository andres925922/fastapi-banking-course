import uuid
from enum import Enum

from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field

from core.domain.exceptions import InvalidPasswordException


class SecurityQuestionsSchema(str, Enum):
    MOTHERS_MAIDEN_NAME = "mothers_maiden_name"
    FIRST_PET_NAME = "first_pet_name"
    FAVORITE_TEACHER = "favorite_teacher"
    BIRTH_CITY = "birth_city"
    FAVORITE_BOOK = "favorite_book"

    @classmethod
    def get_description(cls, value: "SecurityQuestionsSchema"):
        descriptions = {
            cls.MOTHERS_MAIDEN_NAME: "What is your mother's maiden name?",
            cls.FIRST_PET_NAME: "What was the name of your first pet?",
            cls.FAVORITE_TEACHER: "Who was your favorite teacher?",
            cls.BIRTH_CITY: "In which city were you born?",
            cls.FAVORITE_BOOK: "What is your favorite book?",
        }
        return descriptions.get(value, "Unknown security question")
    

class AccountStatusSchema(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING = "pending"


class RoleChoicesSchema(str, Enum):
    CUSTOMER = "customer"
    ACCOUNT_EXECUTIVE = "account_executive"
    BRANCH_MANAGER = "branch_manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    TELLER = "teller"


class BaseUserSchema(SQLModel):
    username: str | None = Field(default=None, max_length=12, unique=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    first_name: str = Field(max_length=30)
    middle_name: str | None = Field(max_length=30, default=None)
    last_name: str = Field(max_length=30)
    is_active: bool = False
    is_superuser: bool = False
    security_question: SecurityQuestionsSchema = Field(max_length=30)
    security_answer: str = Field(max_length=30)
    account_status: AccountStatusSchema = Field(default=AccountStatusSchema.INACTIVE)
    role: RoleChoicesSchema = Field(default=RoleChoicesSchema.CUSTOMER)



class UserCreateSchema(BaseUserSchema):
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values.data and v != values.data["password"]:
            raise InvalidPasswordException("Passwords do not match.")
        return v


class UserReadSchema(BaseUserSchema):
    id: uuid.UUID
    full_name: str