from elasticsearch.dsl import (
    Document,
    InnerDoc,
    Date,
    Keyword,
    Text,
    Integer,
    Long,
    Boolean,
    Nested,
    Object,
    analyzer,
)

from src.configs.config import settings


persian_analyzer = analyzer(
    "persian_analyzer",
    tokenizer="standard",
    filter=[
        "lowercase",
        "decimal_digit",
        "arabic_normalization",
        "persian_normalization",
    ],
)


class CustomerAccount(InnerDoc):
    accountId = Keyword(ignore_above=256)
    type = Keyword(ignore_above=256)
    loyaltyTier = Keyword(ignore_above=256)
    vip = Boolean()
    customerSince = Date()
    preferredLanguage = Keyword(index=False)


class ContactPoints(InnerDoc):
    mobile = Keyword(ignore_above=256)
    email = Keyword(ignore_above=256)
    preferredMethod = Keyword(ignore_above=256)


class Party(InnerDoc):
    nationalId = Keyword(ignore_above=256)
    fullName = Text(analyzer=persian_analyzer, fields={"keyword": Keyword()})
    contactPoints = Object(ContactPoints)
    birthDate = Date(format="yyyy-MM-dd")
    gender = Keyword(ignore_above=64)


class PriceSummary(InnerDoc):
    totalAmount = Long()
    discountAmount = Long()
    payableAmount = Long()
    currency = Keyword(ignore_above=32)


class ProductAttributes(InnerDoc):
    brand = Keyword(ignore_above=256)
    model = Text(fields={"keyword": Keyword()})
    mac_id = Keyword(ignore_above=256)
    category = Keyword(ignore_above=256)


class ProductOrderItem(InnerDoc):
    itemId = Keyword(ignore_above=256)
    productId = Keyword(ignore_above=256)
    sku = Keyword(ignore_above=256)
    status = Keyword(ignore_above=128)
    type = Keyword(ignore_above=128)
    quantity = Integer()
    unitPrice = Long()
    totalPrice = Long()
    stockLocation = Keyword(index=False)
    attributes = Object(ProductAttributes)


class ServiceAttributes(InnerDoc):
    planType = Keyword(ignore_above=128)
    planName = Text(analyzer=persian_analyzer, fields={"keyword": Keyword()})
    dataAllowance = Keyword(ignore_above=128)
    bandwidth = Keyword(ignore_above=128)
    category = Keyword(ignore_above=256)


class Provisioning(InnerDoc):
    status = Keyword(ignore_above=128)
    provisioningType = Keyword(ignore_above=128)
    targetIdentifier = Keyword(ignore_above=256)
    serviceIds = Keyword(multi=True, ignore_above=256)
    activationDate = Date()
    billingStartDate = Date()


class ServiceOrderItem(InnerDoc):
    itemId = Keyword(ignore_above=256)
    productId = Keyword(ignore_above=256)
    sku = Keyword(ignore_above=256)
    status = Keyword(ignore_above=128)
    type = Keyword(ignore_above=128)
    quantity = Integer()
    unitPrice = Long()
    totalPrice = Long()
    bundleId = Keyword(ignore_above=256)
    attributes = Object(ServiceAttributes)
    provisioning = Object(Provisioning)


class Address(InnerDoc):
    fullAddress = Text(analyzer=persian_analyzer, fields={"keyword": Keyword()})
    city = Text(analyzer=persian_analyzer, fields={"keyword": Keyword()})
    postalCode = Keyword(ignore_above=32)
    country = Keyword(ignore_above=128)


class ShipmentHistory(InnerDoc):
    status = Keyword(ignore_above=128)
    timestamp = Date()
    recipientName = Text(
        analyzer=persian_analyzer,
        fields={"keyword": Keyword()},
        index=False,
    )


class ShipmentOrder(InnerDoc):
    shipmentId = Keyword(ignore_above=256)
    status = Keyword(ignore_above=128)
    trackingNumber = Keyword(ignore_above=256)
    carrier = Keyword(ignore_above=256)
    items = Keyword(multi=True, ignore_above=256)
    address = Object(Address)
    history = Nested(ShipmentHistory)


class Transaction(InnerDoc):
    id = Keyword(ignore_above=256)
    type = Keyword(ignore_above=128)
    amount = Long()
    processedAt = Date()
    authorizationCode = Keyword(ignore_above=256, index=False)


class Payment(InnerDoc):
    method = Keyword(ignore_above=128)
    status = Keyword(ignore_above=128)
    provider = Keyword(ignore_above=256)
    transactions = Nested(Transaction)


class Invoice(InnerDoc):
    invoiceId = Keyword(ignore_above=256)
    status = Keyword(ignore_above=128)
    issueDate = Date()
    amount = Long()
    taxAmount = Long()
    currency = Keyword(ignore_above=32)


class AuditDetails(InnerDoc):
    field = Keyword(ignore_above=256)
    from_ = Keyword(index=False)
    to = Keyword(index=False)


class AuditTrail(InnerDoc):
    timestamp = Date()
    action = Keyword(ignore_above=256)
    performedBy = Keyword(ignore_above=256, index=False)
    details = Object(AuditDetails)


class AppliedDiscount(InnerDoc):
    code = Keyword(ignore_above=256)
    description = Text(analyzer=persian_analyzer, index=False)
    amount = Long()


class OrderIndex(Document):
    orderId = Keyword(ignore_above=256)
    status = Keyword(ignore_above=128)
    createdAt = Date()
    updatedAt = Date()
    channel = Keyword(ignore_above=128)

    customerAccount = Object(CustomerAccount)
    party = Object(Party)
    priceSummary = Object(PriceSummary)

    appliedDiscounts = Nested(AppliedDiscount)
    productOrderItems = Nested(ProductOrderItem)
    serviceOrderItems = Nested(ServiceOrderItem)
    shipmentOrders = Nested(ShipmentOrder)
    payment = Nested(Payment)
    invoices = Nested(Invoice)
    returns = Object()
    communications = Object()
    auditTrail = Nested(AuditTrail)

    class Index:
        name = settings.ORDER_INDEX_NAME
        dynamic = "strict"
        settings = {
            "refresh_interval": "30s",
            "number_of_shards": 15,
            "number_of_replicas": 1,
            "analysis": {
                "analyzer": {
                    "persian_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "decimal_digit",
                            "arabic_normalization",
                            "persian_normalization",
                        ],
                    },
                },
            },
        }

    @classmethod
    def _matches(cls, hit):
        return hit["_index"].startswith(cls._index._name.split("-v")[0])
