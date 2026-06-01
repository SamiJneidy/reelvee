from enum import Enum


class AuditEventType(str, Enum):
    # Auth
    AUTH_SIGNUP            = "auth.signup"
    AUTH_LOGIN             = "auth.login"
    AUTH_LOGIN_FAILED      = "auth.login_failed"
    AUTH_LOGOUT            = "auth.logout"
    AUTH_TOKEN_REFRESH     = "auth.token_refresh"
    AUTH_PASSWORD_RESET    = "auth.password_reset"
    AUTH_EMAIL_VERIFIED    = "auth.email_verified"
    AUTH_GOOGLE_LOGIN      = "auth.google_login"

    # User
    USER_CREATED               = "user.created"
    USER_ONBOARDING_COMPLETED  = "user.onboarding_completed"
    USER_EMAIL_CHANGED         = "user.email_changed"

    # Store
    STORE_CREATED = "store.created"
    STORE_UPDATED = "store.updated"

    # Item
    ITEM_CREATED = "item.created"
    ITEM_UPDATED = "item.updated"
    ITEM_DELETED = "item.deleted"

    # Category
    CATEGORY_CREATED = "category.created"
    CATEGORY_UPDATED = "category.updated"
    CATEGORY_DELETED = "category.deleted"

    # Customer
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"

    # Order
    ORDER_CREATED        = "order.created"
    ORDER_UPDATED        = "order.updated"
    ORDER_STATUS_CHANGED = "order.status_changed"
    ORDER_DELETED        = "order.deleted"

    # Invoice
    INVOICE_CREATED       = "invoice.created"
    INVOICE_DELETED       = "invoice.deleted"
    INVOICE_PDF_GENERATED = "invoice.pdf_generated"

    # Expense
    EXPENSE_CREATED = "expense.created"
    EXPENSE_UPDATED = "expense.updated"
    EXPENSE_DELETED = "expense.deleted"

    # File / Storage
    FILE_UPLOAD_URL_REQUESTED = "file.upload_url_requested"
    FILE_DELETED              = "file.deleted"


class AuditResourceType(str, Enum):
    USER     = "user"
    STORE    = "store"
    ITEM     = "item"
    CATEGORY = "category"
    CUSTOMER = "customer"
    ORDER    = "order"
    INVOICE  = "invoice"
    EXPENSE  = "expense"
    FILE     = "file"
