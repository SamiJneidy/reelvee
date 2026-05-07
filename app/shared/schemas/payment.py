"""Shared payment snapshot used by orders, invoices, and related API schemas."""

from datetime import datetime

from pydantic import BaseModel

from app.core.enums import PaymentMethod, PaymentStatus


class PaymentDetails(BaseModel):
    status: PaymentStatus
    method: PaymentMethod | None = None
    amount_paid: float | None = None
    paid_at: datetime | None = None
    reference: str | None = None
    notes: str | None = None
