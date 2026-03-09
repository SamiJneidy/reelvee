from app.modules.users.schemas.responses import UserResponse


from fastapi import APIRouter, Depends, Query, status
from typing import Annotated

from app.core.context import RequestContext
from app.core.database import get_session
from app.modules.auth.auth.dependencies import get_request_context
from app.shared.schemas import SingleResponse
from .dependencies import UserService, get_user_service
from .schemas import UserResponse, UserUpdate
from .docs import UserDocs

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ---------------------------------------------------------------------
# PATCH routes (current user)
# ---------------------------------------------------------------------
@router.patch(
    "/me",
    response_model=SingleResponse[UserResponse],
    summary=UserDocs.UpdateUser.summary,
    description=UserDocs.UpdateUser.description,
    responses=UserDocs.UpdateUser.responses,
)
async def update_current_user(
    body: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> SingleResponse[UserResponse]:
    data = await user_service.update_by_email(
        ctx.user.email,
        body.model_dump(exclude_none=True,),
        session=session,
    )
    return SingleResponse[UserResponse](data=UserResponse.model_validate(data))


# ---------------------------------------------------------------------
# DELETE routes
# ---------------------------------------------------------------------
@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=UserDocs.SoftDeleteUser.summary,
    description=UserDocs.SoftDeleteUser.description,
    responses=UserDocs.SoftDeleteUser.responses,
)
async def delete_current_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> None:
    await user_service.delete_user(ctx.user.email, session=session)
