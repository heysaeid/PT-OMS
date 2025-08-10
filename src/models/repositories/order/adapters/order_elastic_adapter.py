import logging
from datetime import datetime, timedelta
from typing import Any

from elasticsearch import NotFoundError  # Import specific exception
from archipy.adapters.elasticsearch.adapters import AsyncElasticsearchAdapter

from src.configs.config import settings
from src.models.dtos.order.order_repository_interface_dtos import (
    GetOrderByIdQueryDTO,
    GetOrderByIdResponseDTO,
    SearchOrdersQueryDTO,
    SearchOrdersResponseDTO,
)
from src.models.dtos.order.order_dto import OrderRoot

logger = logging.getLogger(__name__)


class OrderElasticAdapter:
    """
    Adapter for interacting with the order index in Elasticsearch.
    Handles searching, fetching by ID, and abstracts Elasticsearch query complexities.
    """

    _INDEX_NAME = "orders-v1-2025-08"
    _ORDER_ID_FIELD = "order.orderId"
    _STATUS_FIELD = "order.status"
    _NATIONAL_ID_FIELD = "order.party.nationalId.keyword"
    _MOBILE_FIELD = "order.party.contactPoints.mobile.keyword"
    _EMAIL_FIELD = "order.party.contactPoints.email.keyword"
    _CREATED_AT_FIELD = "order.createdAt"

    def __init__(
        self, elastic_client: AsyncElasticsearchAdapter, index_name: str | None = None
    ):
        self.elastic_client = elastic_client
        self.index_name = index_name or self._INDEX_NAME

    async def get_order_by_id(
        self, input_dto: GetOrderByIdQueryDTO
    ) -> GetOrderByIdResponseDTO | None:
        """
        Fetches a single order document by its ID from Elasticsearch.

        Returns:
            The order DTO if found, otherwise None.
        """
        try:
            response = await self.elastic_client.get(
                index=self.index_name, id=input_dto.order_id
            )
            source = response.get("_source", {})
            order_data = source.get("order", {})
            if not order_data:
                logger.warning(
                    f"Order data is empty for document ID: {input_dto.order_id}"
                )
                return None

            order = OrderRoot.model_validate(order_data)
            return GetOrderByIdResponseDTO(order=order)
        except NotFoundError:
            logger.info(f"Order with ID '{input_dto.order_id}' not found.")
            return None
        except Exception as e:
            logger.error(f"Error fetching order by ID '{input_dto.order_id}': {e}")
            raise

    async def search_orders(
        self, input_dto: SearchOrdersQueryDTO
    ) -> SearchOrdersResponseDTO:
        query = self._build_search_query(input_dto)

        response = await self.elastic_client.search(index=self.index_name, query=query)

        hits_data = response.get("hits", {})
        total_hits = hits_data.get("total", {}).get("value", 0)
        items: list[OrderRoot] = []
        for hit in hits_data.get("hits", []):
            source = hit.get("_source", {})
            order_data = source.get("order", {})
            if order_data:
                try:
                    items.append(OrderRoot.model_validate(order_data))
                except Exception as e:
                    doc_id = hit.get("_id")
                    logger.error(
                        f"Failed to validate order data for doc ID {doc_id}: {e}"
                    )

        total_pages = (total_hits + input_dto.size - 1) // input_dto.size
        return SearchOrdersResponseDTO(
            total=total_hits,
            page=input_dto.page,
            size=input_dto.size,
            total_pages=total_pages,
            orders=items,
        )

    def _build_search_query(self, input_dto: SearchOrdersQueryDTO) -> dict[str, Any]:
        must_clauses = []

        filter_map = {
            input_dto.order_id: {"term": {self._ORDER_ID_FIELD: input_dto.order_id}},
            input_dto.order_status: {
                "term": {self._STATUS_FIELD: input_dto.order_status}
            },
            input_dto.national_id: {
                "term": {self._NATIONAL_ID_FIELD: input_dto.national_id}
            },
            input_dto.mobile: {"term": {self._MOBILE_FIELD: input_dto.mobile}},
            input_dto.email: {"term": {self._EMAIL_FIELD: input_dto.email}},
        }

        for value, clause in filter_map.items():
            if value:
                must_clauses.append(clause)

        if input_dto.order_date:
            try:
                start_date = datetime.fromisoformat(input_dto.order_date.split("T")[0])
                end_date = start_date + timedelta(days=1)
                must_clauses.append(
                    {
                        "range": {
                            self._CREATED_AT_FIELD: {
                                "gte": start_date.isoformat(),
                                "lt": end_date.isoformat(),
                            }
                        }
                    }
                )
            except ValueError:
                logger.warning(
                    f"Invalid date format provided: {input_dto.order_date}. Ignoring date filter."
                )

        from_ = (input_dto.page - 1) * input_dto.size

        query = {
            "from": from_,
            "size": input_dto.size,
            "query": {"bool": {"must": must_clauses}},
        }

        if input_dto.sort_by:
            query["sort"] = [{input_dto.sort_by: {"order": input_dto.sort_order.value}}]

        return query
