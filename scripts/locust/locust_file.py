import uuid
import random
import os
from locust import task, between, User
from faker import Faker
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro
from datetime import datetime, date, timezone

SCHEMA_PATH = "schemas/avro/orders/order-events.avsc"


try:
    value_schema = avro.load(SCHEMA_PATH)
    key_schema_str = '"string"'
    key_schema = avro.loads(key_schema_str)
except Exception as e:
    print(f"FATAL: Could not load Avro schema from {SCHEMA_PATH}. Error: {e}")
    exit(1)

# --- تنظیمات ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv("LOCUST_KAFKA_HOSTS", "localhost:9092")
SCHEMA_REGISTRY_URL = os.getenv("LOCUST_SCHEMA_REGISTRY_URL", "http://localhost:8081")
TOPIC = "order.events.v1"

fake = Faker()


def to_timestamp_ms(dt_obj):
    return datetime(2022, 3, 25, 2, 39, 20, 736, tzinfo=timezone.utc)
    return int(dt_obj.timestamp() * 1000)


def to_days_since_epoch(dt_obj):
    return (dt_obj - date(1970, 1, 1)).days


def _generate_customer_account():
    return {
        "accountId": str(uuid.uuid4()),
        "type": random.choice(["INDIVIDUAL", "BUSINESS"]),
        "loyaltyTier": random.choice(["STANDARD", "SILVER", "GOLD"]),
        "vip": fake.boolean(chance_of_getting_true=15),
        "preferredLanguage": "fa",
    }


def _generate_party():
    return {
        "nationalId": fake.ssn(),
        "fullName": fake.name(),
        "contactPoints": {
            "mobile": fake.phone_number(),
            "email": fake.email(),
            "preferredMethod": random.choice(["SMS", "EMAIL"]),
        },
        "gender": random.choice(["MALE", "FEMALE", "UNKNOWN"]),
    }


def _generate_price_summary():
    total = random.randint(100000, 5000000)
    discount = random.randint(0, total // 4)
    return {
        "totalAmount": total,
        "discountAmount": discount,
        "payableAmount": total - discount,
        "currency": "IRR",
    }


def _generate_product_order_item(status):
    return {
        "itemId": str(uuid.uuid4()),
        "productId": f"PROD-{random.randint(100, 999)}",
        "sku": f"SKU-{random.randint(1000, 9999)}",
        "status": status,
        "type": random.choice(["PHYSICAL", "DIGITAL"]),
        "quantity": random.randint(1, 3),
        "unitPrice": random.randint(50000, 1000000),
        "totalPrice": random.randint(50000, 3000000),
        "stockLocation": "Warehouse-1",
        "attributes": {
            "brand": fake.company(),
            "model": "Model-X",
            "mac_id": fake.mac_address(),
            "category": "Electronics",
        },
    }


def _generate_payment():
    return {
        "method": "ONLINE_GATEWAY",
        "status": random.choice(["PENDING", "SUCCESSFUL", "FAILED"]),
        "provider": "SamanBank",
        "transactions": [
            {
                "id": str(uuid.uuid4()),
                "type": "SALE",
                "amount": random.randint(100000, 5000000),
                "processedAt": to_timestamp_ms(datetime.now()),
                "authorizationCode": fake.md5(),
            }
        ],
    }


def _generate_shipment_order(status):
    return {
        "shipmentId": str(uuid.uuid4()),
        "status": status,
        "trackingNumber": fake.bothify(text="??##########"),
        "carrier": "Peyk",
        "items": [str(uuid.uuid4())],
        "address": {
            "fullAddress": fake.address(),
            "city": fake.city(),
            "postalCode": fake.postcode(),
            "country": fake.country(),
        },
        "history": [],
    }


def _generate_communication():
    return {
        "communicationId": str(uuid.uuid4()),
        "channel": "SMS",
        "timestamp": to_timestamp_ms(datetime.now(tz=timezone.utc)),
        "content": "Your order has been shipped.",
    }


def _generate_audit_trail():
    return {
        "timestamp": to_timestamp_ms(datetime.now(tz=timezone.utc)),
        "action": "STATUS_UPDATE",
        "performedBy": "SYSTEM",
        "details": {"field": "status", "from": "PROCESSING", "to": "SHIPPED"},
    }


def generate_unified_order_payload(order_id=None, status=None):
    if order_id is None:
        order_id = str(uuid.uuid4())

    current_status = status or random.choice(["PENDING", "CONFIRMED", "PROCESSING"])

    payload = {
        "order": {
            "orderId": order_id,
            "status": current_status,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "channel": "ONLINE_WEB",
            "customerAccount": _generate_customer_account(),
            "party": _generate_party(),
            "priceSummary": _generate_price_summary(),
            "appliedDiscounts": [],  # TODO: add applied discounts
            "productOrderItems": [
                _generate_product_order_item(current_status)
                for _ in range(random.randint(1, 2))
            ],
            "serviceOrderItems": [],
            "shipmentOrders": [_generate_shipment_order(current_status)]
            if current_status in ["SHIPPED", "DELIVERED", "COMPLETED"]
            else [],
            "payment": [_generate_payment()],
            "invoices": [],
            "returns": [],
            "communications": [_generate_communication()]
            if current_status == "SHIPPED"
            else [],
            "auditTrail": [_generate_audit_trail()],
        }
    }
    return payload


class KafkaUser(User):
    wait_time = between(0.1, 0.5)

    def __init__(self, environment):
        super().__init__(environment)
        producer_conf = {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "schema.registry.url": SCHEMA_REGISTRY_URL,
        }
        self.producer = AvroProducer(
            producer_conf,
            default_value_schema=value_schema,
            default_key_schema=key_schema,
        )
        self.existing_order_ids = []

    def on_stop(self):
        self.producer.flush()

    @task(10)
    def insert_new_order(self):
        payload = generate_unified_order_payload(status="PROCESSING")
        order_id = payload["order"]["orderId"]

        try:
            self.producer.produce(topic=TOPIC, key=order_id, value=payload)
            self.environment.events.request.fire(
                request_type="KAFKA",
                name="insert_unified_order",
                response_time=0,
                response_length=0,
                exception=None,
            )
            self.existing_order_ids.append(order_id)
            if len(self.existing_order_ids) > 1000:
                self.existing_order_ids.pop(0)

        except Exception as e:
            self.environment.events.request.fire(
                request_type="KAFKA",
                name="insert_unified_order",
                response_time=0,
                response_length=0,
                exception=e,
            )

    @task(3)
    def update_existing_order(self):
        """شبیه‌سازی به‌روزرسانی یک سفارش موجود با اسکیمای جدید"""
        if not self.existing_order_ids:
            return

        order_id = random.choice(self.existing_order_ids)
        new_status = random.choice(["SHIPPED", "COMPLETED", "CANCELLED"])
        payload = generate_unified_order_payload(order_id=order_id, status=new_status)

        try:
            self.producer.produce(topic=TOPIC, key=order_id, value=payload)
            self.environment.events.request.fire(
                request_type="KAFKA",
                name="update_unified_order",
                response_time=0,
                response_length=0,
                exception=None,
            )
        except Exception as e:
            self.environment.events.request.fire(
                request_type="KAFKA",
                name="update_unified_order",
                response_time=0,
                response_length=0,
                exception=e,
            )
