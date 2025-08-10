import os
import glob
import argparse
import logging
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.error import SchemaRegistryError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_schema_registry_client() -> SchemaRegistryClient:
    registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
    logging.info(f"Connecting to Schema Registry at {registry_url}")
    return SchemaRegistryClient({"url": registry_url})


def derive_subject_name(file_path: str) -> str:
    base_name = os.path.basename(file_path)
    topic_name, _ = os.path.splitext(base_name)
    return f"{topic_name}-value"


def register_schema(
    client: SchemaRegistryClient,
    subject: str,
    schema_str: str,
) -> None:
    new_schema = Schema(schema_str, schema_type="AVRO")

    try:
        latest_version = client.get_latest_version(subject)
        logging.info(
            f"Subject '{subject}' already exists with version {latest_version.version}.",
        )

        is_compatible = client.test_compatibility(subject, new_schema)

        if is_compatible:
            logging.info(
                f"Schema for '{subject}' is compatible. Registering new version...",
            )
            schema_id = client.register_schema(subject, new_schema)
            logging.info(
                f"Successfully registered schema for '{subject}' with ID {schema_id}.",
            )
        else:
            logging.error(
                f"SCHEMA INCOMPATIBLE! Schema for '{subject}' is not compatible with the latest version. Aborting.",
            )
            raise ValueError(f"Incompatible schema for subject {subject}")

    except SchemaRegistryError as e:
        if e.http_status_code == 404:
            logging.info(f"Subject '{subject}' not found. Registering as a new schema.")
            schema_id = client.register_schema(subject, new_schema)
            logging.info(
                f"Successfully registered schema for '{subject}' with ID {schema_id}.",
            )
        else:
            logging.error(f"An error occurred with the Schema Registry: {e}")
            raise


def main(files_to_register: list[str] | None = None):
    client = get_schema_registry_client()

    if files_to_register:
        schema_files = files_to_register
        logging.info(f"Found {len(schema_files)} specific file(s) to register.")
    else:
        search_path = os.path.join("schemas", "**", "*.avsc")
        schema_files = glob.glob(search_path, recursive=True)
        logging.info(f"Found {len(schema_files)} Avro schema files to process.")

    if not schema_files:
        logging.warning("No schema files found. Exiting.")
        return

    for file_path in schema_files:
        try:
            logging.info(f"--- Processing file: {file_path} ---")
            with open(file_path, "r") as f:
                schema_str = f.read()

            subject_name = derive_subject_name(file_path)
            register_schema(client, subject_name, schema_str)
        except Exception as e:
            logging.error(f"Failed to process {file_path}. Reason: {e}")
            exit(1)

    logging.info("--- Schema registration process completed successfully. ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Register Avro schemas with the Schema Registry.",
    )
    parser.add_argument(
        "--file",
        dest="files",
        action="append",
        help="Specify a single .avsc file to register. Can be used multiple times.",
    )
    args = parser.parse_args()

    main(files_to_register=args.files)
