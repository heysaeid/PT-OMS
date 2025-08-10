# file: order_mapping.py

from elasticsearch.dsl import (
    Document,
    Text,
    Keyword,
    Date,
    Boolean,
    Long,
    Integer,
    Nested,
    InnerDoc,
    Object,
    analyzer,
)
from elasticsearch.dsl.connections import connections

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
    accountId = Keyword()
    type = Keyword()
    loyaltyTier = Keyword()
    vip = Boolean()
    customerSince = Date()
    preferredLanguage = Keyword()


class ContactPoints(InnerDoc):
    mobile = Keyword()
    email = Keyword()
    preferredMethod = Keyword()


class Party(InnerDoc):
    nationalId = Keyword()
    fullName = Text(analyzer=persian_analyzer, fields={"keyword": Keyword()})
    contactPoints = Object(ContactPoints)
    birthDate = Date(format="yyyy-MM-dd")
    gender = Keyword()


class PriceSummary(InnerDoc):
    totalAmount = Long()
    discountAmount = Long()
    payableAmount = Long()
    currency = Keyword()


class ProductAttributes(InnerDoc):
    brand = Keyword()
    model = Text(fields={"keyword": Keyword()})
    mac_id = Keyword()
    category = Keyword()


class ProductOrderItem(InnerDoc):
    itemId = Keyword()
    productId = Keyword()
    sku = Keyword()
    status = Keyword()
    type = Keyword()
    quantity = Integer()
    unitPrice = Long()
    totalPrice = Long()
    stockLocation = Keyword()
    attributes = Object(ProductAttributes)


class ServiceAttributes(InnerDoc):
    planType = Keyword()
    planName = Text(analyzer=persian_analyzer, fields={"keyword": Keyword()})
    dataAllowance = Keyword()
    bandwidth = Keyword()
    category = Keyword()


class Provisioning(InnerDoc):
    status = Keyword()
    provisioningType = Keyword()
    targetIdentifier = Keyword()
    serviceIds = Keyword()
    activationDate = Date()
    billingStartDate = Date()


class ServiceOrderItem(InnerDoc):
    itemId = Keyword()
    productId = Keyword()
    sku = Keyword()
    status = Keyword()
    type = Keyword()
    quantity = Integer()
    unitPrice = Long()
    totalPrice = Long()
    bundleId = Keyword()
    attributes = Object(ServiceAttributes)
    provisioning = Object(Provisioning)


class Address(InnerDoc):
    fullAddress = Text(analyzer=persian_analyzer, fields={"keyword": Keyword()})
    city = Text(analyzer=persian_analyzer, fields={"keyword": Keyword()})
    postalCode = Keyword()
    country = Keyword()


class ShipmentHistory(InnerDoc):
    status = Keyword()
    timestamp = Date()
    recipientName = Text(analyzer=persian_analyzer, fields={"keyword": Keyword()})


class ShipmentOrder(InnerDoc):
    shipmentId = Keyword()
    status = Keyword()
    trackingNumber = Keyword()
    carrier = Keyword()
    items = Keyword()
    address = Object(Address)
    history = Nested(ShipmentHistory)


class Transaction(InnerDoc):
    id = Keyword()
    type = Keyword()
    amount = Long()
    processedAt = Date()
    authorizationCode = Keyword()


class Payment(InnerDoc):
    method = Keyword()
    status = Keyword()
    provider = Keyword()
    transactions = Nested(Transaction)


class Invoice(InnerDoc):
    invoiceId = Keyword()
    status = Keyword()
    issueDate = Date()
    amount = Long()
    taxAmount = Long()
    currency = Keyword()


class AuditDetails(InnerDoc):
    """
    Defines the audit details. Uses 'from_' and 'to' to track changes.
    The field in Elasticsearch will be named 'from_'.
    """

    field = Keyword()
    # 'from' is a reserved keyword in Python, so we use 'from_'
    # This is the standard and recommended practice.
    from_ = Keyword()
    to = Keyword()


class AuditTrail(InnerDoc):
    timestamp = Date()
    action = Keyword()
    performedBy = Keyword()
    details = Object(AuditDetails)


class OrderIndex(Document):
    orderId = Keyword()
    status = Keyword()
    createdAt = Date()
    updatedAt = Date()
    channel = Keyword()

    customerAccount = Object(CustomerAccount)
    party = Object(Party)
    priceSummary = Object(PriceSummary)

    appliedDiscounts = Nested()
    productOrderItems = Nested(ProductOrderItem)
    serviceOrderItems = Nested(ServiceOrderItem)
    shipmentOrders = Nested(ShipmentOrder)
    payment = Nested(Payment)
    invoices = Nested(Invoice)
    returns = Nested()
    communications = Nested()
    auditTrail = Nested(AuditTrail)

    class Index:
        name = "orders"
        settings = {"number_of_shards": 1, "number_of_replicas": 1}

    @classmethod
    def _matches(cls, hit):
        return hit["_index"].startswith(cls._index._name)


def main():
    try:
        connections.create_connection(hosts=["http://localhost:9200"])
        print("Successfully connected to Elasticsearch.")

        if connections.get_connection().indices.exists(index=OrderIndex.Index.name):
            print(f"Index '{OrderIndex.Index.name}' already exists.")
        else:
            print(f"Creating index '{OrderIndex.Index.name}'...")
            OrderIndex.init()
            print("Index created successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
