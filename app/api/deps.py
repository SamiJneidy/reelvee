from typing import Annotated

from fastapi import Depends

from app.core.database import transactional_session
from app.core.unit_of_work import MongoUnitOfWork, UnitOfWork


async def get_unit_of_work() -> UnitOfWork:
    """No transaction (e.g. read-only). Repositories use session=None."""
    yield MongoUnitOfWork(session=None)


async def get_transactional_unit_of_work() -> UnitOfWork:
    """Starts a transaction and yields a UoW. Commit/abort handled for you."""
    async with transactional_session() as session:
        yield MongoUnitOfWork(session=session)


# For route injection: choose the one that fits the endpoint
UnitOfWorkDep = Annotated[UnitOfWork, Depends(get_unit_of_work)]
TransactionalUnitOfWorkDep = Annotated[UnitOfWork, Depends(get_transactional_unit_of_work)]
