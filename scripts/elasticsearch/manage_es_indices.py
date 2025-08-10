# manage_es_indices.py
import sys
from datetime import datetime, timedelta
from elasticsearch.dsl import IndexTemplate
from elasticsearch.dsl.connections import connections
from elasticsearch.exceptions import NotFoundError
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.entities.order_index import OrderIndex 

INDEX_PATTERN_PREFIX = "orders-v1"
SEARCH_ALIAS = "orders-search"
WRITE_ALIAS = "order.events.v1"
TEMPLATE_NAME = "orders_template_v1"


def setup_template():
    print(f"Setting up index template '{TEMPLATE_NAME}'...")

    from elasticsearch import Elasticsearch
    
    es = connections.get_connection()
    
    template_body = {
        "index_patterns": [f"{INDEX_PATTERN_PREFIX}-*"],
        "template": {
            "settings": OrderIndex.Index.settings,
            "mappings": OrderIndex._doc_type.mapping.to_dict(),
            "aliases": {
                SEARCH_ALIAS: {}
            }
        }
    }
    
    # استفاده از indices.put_index_template
    es.indices.put_index_template(
        name=TEMPLATE_NAME,
        body=template_body
    )
    print("Template successfully saved.")

def get_current_month_index_name():
    return f"{INDEX_PATTERN_PREFIX}-{datetime.now().strftime('%Y-%m')}"

def ensure_current_index_and_aliases_exist():
    print("Ensuring current index and aliases exist...")
    client = connections.get_connection()
    current_index = get_current_month_index_name()

    if not client.indices.exists(index=current_index):
        print(f"Index '{current_index}' does not exist. Creating it...")
        client.indices.create(index=current_index)
        print(f"Index '{current_index}' created.")

    if not client.indices.exists_alias(name=WRITE_ALIAS):
        print(f"Write alias '{WRITE_ALIAS}' does not exist. Pointing it to '{current_index}'...")
        client.indices.put_alias(index=current_index, name=WRITE_ALIAS)
        print(f"Write alias '{WRITE_ALIAS}' created.")

def perform_monthly_rollover():
    print("Performing monthly rollover check...")
    client = connections.get_connection()
    
    try:
        current_write_indices = list(client.indices.get_alias(name=WRITE_ALIAS).keys())
        if not current_write_indices:
            print("No write alias found. Running initial setup...")
            ensure_current_index_and_aliases_exist()
            return
        
        old_write_index = current_write_indices[0]
        
        new_write_index = get_current_month_index_name()
        
        if old_write_index == new_write_index:
            print(f"Rollover not needed. Write alias is already pointing to the current month's index: '{new_write_index}'")
            return
            
        print(f"Rollover needed. Transitioning from '{old_write_index}' to '{new_write_index}'...")

        if not client.indices.exists(index=new_write_index):
            client.indices.create(index=new_write_index)
            print(f"Created new index: '{new_write_index}'")

        actions = [
            {"remove": {"index": old_write_index, "alias": WRITE_ALIAS}},
            {"add": {"index": new_write_index, "alias": WRITE_ALIAS}}
        ]
        client.indices.update_aliases(body={"actions": actions})
        print(f"Successfully rolled over write alias to '{new_write_index}'.")

    except NotFoundError:
        print("Write alias not found. Running initial setup...")
        ensure_current_index_and_aliases_exist()
    except Exception as e:
        print(f"An error occurred during rollover: {e}")
        sys.exit(1)


if __name__ == "__main__":
    connections.create_connection(hosts=['http://localhost:9200'])

    if len(sys.argv) < 2:
        print("Usage: python manage_es_indices.py <command>")
        print("Commands: setup, ensure, rollover")
        sys.exit(1)

    command = sys.argv[1]

    if command == "setup":
        setup_template()
    elif command == "ensure":
        ensure_current_index_and_aliases_exist()
    elif command == "rollover":
        perform_monthly_rollover()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)