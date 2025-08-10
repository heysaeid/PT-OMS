from elasticsearch.dsl.connections import connections
from src.models.entities.order_index import OrderIndex
from src.configs.config import settings


def main():
    try:
        connections.create_connection(hosts=settings.ELASTIC.HOSTS)
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
