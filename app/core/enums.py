from enum import Enum

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class TokenScope(str, Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"
    INVITE = "INVITE"
    SIGN_UP_COMPLETE = "SIGN_UP_COMPLETE"
    RESET_PASSWORD = "RESET_PASSWORD"
    EMAIL_CHANGE = "EMAIL_CHANGE"

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    SALESMAN = "SALESMAN"
    ACCOUNTANT = "ACCOUNTANT"

class UserType(str, Enum):
    CLIENT = "CLIENT"
    DEVELOPR = "DEVELOPER"

class UserStatus(str, Enum):
    PENDING = "PENDING"          # Awaiting email/phone verification
    ACTIVE = "ACTIVE"            # Verified and fully accessible
    BLOCKED = "BLOCKED"          # Temporary suspension (e.g., too many failed logins)
    DISABLED = "DISABLED"        # Manual deactivation by admin (reversible)
    DELETED = "DELETED"          # Soft-deleted (GDPR compliance; irreversible)

class OTPStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"

class OTPUsage(str, Enum):
    LOGIN = "LOGIN"
    PASSWORD_RESET = "PASSWORD_RESET"
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"

class ProjectStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class UserPlan(str, Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"

class UserStep(str, Enum):
    ONE = "ONE"
    TWO = "TWO"


class ItemStatus(str, Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    LOW_STOCK = "low_stock"


class ItemType(str, Enum):
    PRODUCT = "product"
    SERVICE = "service"