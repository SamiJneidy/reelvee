import re
from typing import Any

from beanie import PydanticObjectId

from app.modules.invoices.models import Invoice, InvoiceCounter


class InvoiceRepository:

    def _build_match_filter(
        self, user_id: PydanticObjectId, filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        filters = filters or {}
        match_filter: dict[str, Any] = {"user_id": user_id}
        for field in ("currency",):
            if filters.get(field) is not None:
                match_filter[field] = filters[field]
        for field in ("invoice_number", "order_number", "order_reference_number"):
            if filters.get(field) is not None:
                match_filter[field] = {
                    "$regex": re.escape(filters[field]),
                    "$options": "i",
                }
        return match_filter

    def _deserialize(self, raw: dict[str, Any]) -> Invoice:
        return Invoice.model_validate(raw)

    async def get_by_id(
        self, user_id: PydanticObjectId, id: PydanticObjectId, session=None
    ) -> Invoice | None:
        return await Invoice.find_one(
            Invoice.user_id == user_id,
            Invoice.id == id,
            session=session,
        )

    async def get_list(
        self,
        user_id: PydanticObjectId,
        skip: int = 0,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[Invoice]]:
        match_filter = self._build_match_filter(user_id=user_id, filters=filters)
        total = await Invoice.get_pymongo_collection().count_documents(
            match_filter, session=session
        )
        pipeline = [
            {"$match": match_filter},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
        ]
        cursor = Invoice.get_pymongo_collection().aggregate(pipeline, session=session)
        raw_list = await cursor.to_list(length=None)
        return total, [self._deserialize(raw) for raw in raw_list]

    async def next_invoice_number(
        self, user_id: PydanticObjectId, session=None
    ) -> int:
        """Return the next sequential invoice number for a store.

        Uses an atomic ``find_one_and_update`` with ``$inc`` + ``upsert`` so
        concurrent invoice creation never produces duplicate numbers.
        """
        result = await InvoiceCounter.get_pymongo_collection().find_one_and_update(
            {"_id": user_id},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True,
            session=session,
        )
        return result["seq"]

    async def create(self, data: dict[str, Any], session=None) -> Invoice:
        invoice = Invoice(**data)
        await invoice.insert(session=session)
        return await self.get_by_id(invoice.user_id, invoice.id, session=session)

    async def update_by_id(
        self,
        user_id: PydanticObjectId,
        id: PydanticObjectId,
        data: dict[str, Any],
        session=None,
    ) -> Invoice | None:
        invoice = await Invoice.find_one(
            Invoice.user_id == user_id,
            Invoice.id == id,
            session=session,
        )
        if invoice is None:
            return None
        for key, value in data.items():
            if hasattr(Invoice, key):
                setattr(invoice, key, value)
        await invoice.save(session=session)
        return await self.get_by_id(invoice.user_id, invoice.id, session=session)

    async def delete_by_id(
        self, user_id: PydanticObjectId, id: PydanticObjectId, session=None
    ) -> None:
        invoice = await Invoice.find_one(
            Invoice.user_id == user_id,
            Invoice.id == id,
            session=session,
        )
        if invoice is not None:
            await invoice.delete(session=session)
