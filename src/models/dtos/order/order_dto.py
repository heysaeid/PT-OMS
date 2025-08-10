from __future__ import annotations
from typing import Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr
from src.models.types.order_types import (
    OrderStatusType,
    ItemStatusType,
    PaymentStatusType,
    PaymentMethodType,
    GenderType,
    CustomerType,
    ProvisioningStatusType,
    ProvisioningTypeType,
    ContactMethodType,
    OrderItemType,
)


class CustomerAccount(BaseModel):
    accountId: str
    type: CustomerType
    loyaltyTier: str = "STANDARD"
    vip: bool = False
    customerSince: date | None = None
    preferredLanguage: str = Field(default="fa", min_length=2, max_length=5)


class ContactPoints(BaseModel):
    mobile: str | None = None
    email: EmailStr | None = None
    preferredMethod: ContactMethodType = ContactMethodType.SMS


class Party(BaseModel):
    nationalId: str | None = None
    fullName: str | None = None
    contactPoints: ContactPoints
    birthDate: date | None = None
    gender: GenderType = GenderType.UNKNOWN


class PriceSummary(BaseModel):
    totalAmount: int
    discountAmount: int = 0
    payableAmount: int
    currency: str = "TRY"


class ProductAttributes(BaseModel):
    brand: str = "Unknown"
    model: str | None = None
    mac_id: str | None = None
    category: str | None = None


class ServiceAttributes(BaseModel):
    planType: str | None = None
    planName: str | None = None
    dataAllowance: str | None = None
    bandwidth: str | None = None
    category: str | None = None


class Provisioning(BaseModel):
    status: ProvisioningStatusType = ProvisioningStatusType.ACTIVE
    provisioningType: ProvisioningTypeType = ProvisioningTypeType.NEW_ACTIVATION
    targetIdentifier: str | None = None
    serviceIds: list[str] = []
    activationDate: datetime | None = None
    billingStartDate: datetime | None = None


class ProductOrderItem(BaseModel):
    itemId: str
    productId: str
    sku: str
    status: ItemStatusType
    type: OrderItemType = OrderItemType.PHYSICAL
    quantity: int = 1
    unitPrice: int
    totalPrice: int
    stockLocation: str | None = None
    attributes: ProductAttributes


class ServiceOrderItem(BaseModel):
    itemId: str
    productId: str
    sku: str
    status: ItemStatusType
    type: OrderItemType = OrderItemType.DIGITAL_SERVICE
    quantity: int = 1
    unitPrice: int
    totalPrice: int
    bundleId: str | None = None
    attributes: ServiceAttributes
    provisioning: Provisioning


class ShipmentAddress(BaseModel):
    fullAddress: str | None = None
    city: str | None = None
    postalCode: str | None = None
    country: str = "TR"


class ShipmentHistoryItem(BaseModel):
    status: ItemStatusType
    timestamp: datetime | None = None
    recipientName: str | None = None


class ShipmentOrder(BaseModel):
    shipmentId: str
    status: ItemStatusType
    trackingNumber: str | None = None
    carrier: str = "INTERNAL_DELIVERY"
    items: list[str] = []
    address: ShipmentAddress
    history: list[ShipmentHistoryItem] = []


class PaymentTransaction(BaseModel):
    id: str
    type: Literal["SALE", "REFUND", "AUTH", "CAPTURE"] = "SALE"
    amount: int
    processedAt: datetime | None = None
    authorizationCode: str | None = None


class Payment(BaseModel):
    method: PaymentMethodType
    status: PaymentStatusType
    provider: str | None = None
    transactions: list[PaymentTransaction]


class Invoice(BaseModel):
    invoiceId: str
    status: Literal["PAID", "UNPAID", "VOID", "REFUNDED"] = "PAID"
    issueDate: datetime | None = None
    amount: int
    taxAmount: int = 0
    currency: str = "TRY"


class AuditDetails(BaseModel):
    field: str | None = None
    from_: str | None = Field(default=None, alias="from")
    to: str | None = None


class AuditTrailItem(BaseModel):
    timestamp: datetime | None = None
    action: str
    performedBy: str = "system"
    details: AuditDetails | None = None


class OrderRoot(BaseModel):
    orderId: str
    status: OrderStatusType
    createdAt: datetime
    updatedAt: datetime
    channel: str | None = None
    customerAccount: CustomerAccount
    party: Party
    priceSummary: PriceSummary
    appliedDiscounts: list[dict] = []
    productOrderItems: list[ProductOrderItem] = []
    serviceOrderItems: list[ServiceOrderItem] = []
    shipmentOrders: list[ShipmentOrder] = []
    payment: list[Payment] = []
    invoices: list[Invoice] = []
    returns: list[dict] = []
    communications: list[dict] = []
    auditTrail: list[AuditTrailItem] = []
