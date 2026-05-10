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


class TempFileUploadPath(str, Enum):
    ITEM_THUMBNAIL = "temp/items/thumbnails"
    ITEM_IMAGE     = "temp/items/images"
    STORE_LOGO      = "temp/stores/logos"
    STORE_BACKGROUND_IMAGE = "temp/stores/background_images"

class PermanentFileUploadPath(str, Enum):
    ITEM_THUMBNAIL = "uploads/items/thumbnails"
    ITEM_IMAGE     = "uploads/items/images"
    STORE_LOGO      = "uploads/stores/logos"
    STORE_QR_CODE   = "uploads/stores/qr_codes"
    STORE_BACKGROUND_IMAGE = "uploads/stores/background_images"
    INVOICE_PDF     = "uploads/invoices/pdfs"


class RecordSource(str, Enum):
    WEB      = "web"       # submitted via public web storefront
    APP      = "app"       # submitted via mobile app (future)
    INTERNAL = "internal"  # created manually by store owner via dashboard


class CustomerStatus(str, Enum):
    ACTIVE  = "active"
    BLOCKED = "blocked"


class OrderStatus(str, Enum):
    NEW        = "new"
    SEEN       = "seen"
    CONTACTED  = "contacted"
    CONFIRMED  = "confirmed"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    CANCELLED  = "cancelled"
    IGNORED    = "ignored"


class DeliveryStatus(str, Enum):
    PENDING   = "pending"
    PREPARING = "preparing"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    RETURNED  = "returned"


class PaymentMethod(str, Enum):
    CASH          = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD   = "credit_card"
    MOBILE_WALLET = "mobile_wallet"
    CHEQUE        = "cheque"
    OTHER         = "other"


class PaymentStatus(str, Enum):
    UNPAID   = "unpaid"
    PARTIAL  = "partial"
    PAID     = "paid"
    REFUNDED = "refunded"


class TemplateId(str, Enum):
    TEMPLATE_A = "TEMPLATE_A"
    TEMPLATE_B = "TEMPLATE_B"


class Layout(str, Enum):
    LIST = "LIST"
    GRID = "GRID"


class ButtonVariant(str, Enum):
    FILLED   = "FILLED"
    OUTLINE = "OUTLINE"
    SOFT   = "SOFT"


class ButtonShape(str, Enum):
    ROUNDED = "ROUNDED"
    SQUARE  = "SQUARE"
    PILL    = "PILL"


class BackgroundType(str, Enum):
    COLOR    = "COLOR"
    IMAGE    = "IMAGE"
    GRADIENT = "GRADIENT"


class Font(str, Enum):
    INTER = "INTER",
    ROBOTO = "ROBOTO",
    POPPINS = "POPPINS",
    LATO = "LATO",
    MONTSERRAT = "MONTSERRAT",
    SEKUYA = "SEKUYA",
    RUBIK = "RUBIK",
    ARCHIVO_BLACK = "ARCHIVO_BLACK"


class OSType(str, Enum):
    ios     = "ios"
    android = "android"
    windows = "windows"
    macos   = "macos"
    linux   = "linux"
    unknown = "unknown"


class AnalyticsEventType(str, Enum):
    store_view = "store_view"
    item_view  = "item_view"


class ExpenseCategory(str, Enum):
    RENT = "rent"
    UTILITIES = "utilities"
    SUPPLIES = "supplies"
    SALARIES = "salaries"
    MARKETING = "marketing"
    SHIPPING = "shipping"
    MAINTENANCE = "maintenance"
    TAXES = "taxes"
    OTHER = "other"


class ExpensePaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"
