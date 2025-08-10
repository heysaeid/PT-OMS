from enum import StrEnum


class OrderStatusType(StrEnum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    PURCHASED = "PURCHASED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"
    COMPLETED = "COMPLETED"
    SHIPPED = "SHIPPED"
    PROCESSING = "PROCESSING"


class ItemStatusType(StrEnum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    PROCESSING = "PROCESSING"


class PaymentStatusType(StrEnum):
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    PENDING = "PENDING"


class PaymentMethodType(StrEnum):
    CW = "CW"
    CARD = "CARD"
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"
    OTHER = "OTHER"
    ONLINE_GATEWAY = "ONLINE_GATEWAY"


class GenderType(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNKNOWN = "UNKNOWN"


class CustomerType(StrEnum):
    INDIVIDUAL = "INDIVIDUAL"
    BUSINESS = "BUSINESS"


class ProvisioningStatusType(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"


class ProvisioningTypeType(StrEnum):
    NEW_ACTIVATION = "NEW_ACTIVATION"
    MIGRATION = "MIGRATION"
    UPGRADE = "UPGRADE"


class ContactMethodType(StrEnum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    CALL = "CALL"


class OrderItemType(StrEnum):
    PHYSICAL = "PHYSICAL"
    DIGITAL_SERVICE = "DIGITAL_SERVICE"
    DIGITAL = "DIGITAL"


class SortOrderByType(StrEnum):
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    ORDER_DATE = "orderDate"
    ORDER_STATUS = "orderStatus"
    NATIONAL_ID = "nationalId"
    MOBILE = "mobile"
    EMAIL = "email"
