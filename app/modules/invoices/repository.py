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
        if filters.get("order_id") is not None:
            match_filter["order_id"] = filters["order_id"]
        if filters.get("customer_id") is not None:
            match_filter["customer.id"] = filters["customer_id"]
        if filters.get("item_id") is not None:
            match_filter["items.id"] = filters["item_id"]
        for field in ("invoice_number", "order_number"):
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

    async def get_by_order_id(
        self,
        user_id: PydanticObjectId,
        order_id: PydanticObjectId,
        session=None,
    ) -> Invoice | None:
        return await Invoice.find_one(
            Invoice.user_id == user_id,
            Invoice.order_id == order_id,
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
        # Count on the raw collection — no join needed, hits the index directly.
        total = await Invoice.get_pymongo_collection().count_documents(
            match_filter, session=session
        )
        invoices = await Invoice.find(match_filter, session=session).sort(-Invoice.created_at).skip(skip).limit(limit).to_list()
        return total, invoices

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
