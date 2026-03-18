from app.modules.auth.service import AuthService
from app.modules.users.schemas.requests import ChangeEmailRequest, RequestEmailChangeRequest, SignUpCompleteRequest
from app.modules.users.schemas.responses import SignUpCompleteResponse, UserResponse


from fastapi import APIRouter, Depends, Query, Request, Response, status
from typing import Annotated

from app.core.context import RequestContext
from app.core.database import get_session
from app.modules.auth.dependencies import get_auth_service, get_request_context, get_user_from_sign_up_complete_token
from app.shared.schemas import SingleResponse
from app.shared.schemas.responses import SuccessResponse
from .dependencies import UserService, get_user_service
from .schemas import UserResponse, UserUpdate
from .docs import UserDocs

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# ---------------------------------------------------------------------
# POST routes (current user)
# ---------------------------------------------------------------------
@router.post(
    "/signup/complete",
    response_model=SingleResponse[SignUpCompleteResponse],
    summary=UserDocs.SignUpComplete.summary,
    description=UserDocs.SignUpComplete.description,
    responses=UserDocs.SignUpComplete.responses,
)
async def sign_up_complete(
    request: Request,
    response: Response,
    body: SignUpCompleteRequest,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_user_from_sign_up_complete_token),
) -> SingleResponse[SignUpCompleteResponse]:
    data = await user_service.sign_up_complete(current_user.email, body, session)
    response.delete_cookie("sign_up_complete_token")
    access_token = await auth_service.create_access_token(
        request, response, current_user.id, set_cookie=True
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, data.user.id, set_cookie=True
    )
    return SingleResponse[SignUpCompleteResponse](data=data)


@router.post(
    "/request-email-change",
    response_model=SuccessResponse,
    summary=UserDocs.RequestEmailChange.summary,
    description=UserDocs.RequestEmailChange.description,
    responses=UserDocs.RequestEmailChange.responses,
)
async def request_email_change(
    body: RequestEmailChangeRequest,
    user_service: UserService = Depends(get_user_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> SuccessResponse:
    await user_service.request_email_change(ctx.user.id, body, session)
    return SuccessResponse(detail="Email change link sent successfully")


@router.post(
    "/confirm-email-change",
    response_model=SingleResponse[UserResponse],
    summary=UserDocs.ConfirmEmailChange.summary,
    description=UserDocs.ConfirmEmailChange.description,
    responses=UserDocs.ConfirmEmailChange.responses,
)
async def confirm_email_change(
    body: ChangeEmailRequest,
    request: Request,
    response: Response,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> SingleResponse[UserResponse]:
    data = await user_service.confirm_email_change(body, session)
    access_token = await auth_service.create_access_token(
        request, response, data.id, set_cookie=True
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, data.id, set_cookie=True
    )
    return SingleResponse[UserResponse](data=data)


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


@router.delete(
    "/me/logo",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=UserDocs.DeleteOwnLogo.summary,
    description=UserDocs.DeleteOwnLogo.description,
    responses=UserDocs.DeleteOwnLogo.responses,
)
async def delete_logo(
    user_service: UserService = Depends(get_user_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> None:
    await user_service.delete_logo(ctx, session)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=UserDocs.SoftDeleteUser.summary,
    description=UserDocs.SoftDeleteUser.description,
    responses=UserDocs.SoftDeleteUser.responses,
)
async def delete_current_user(
    email: str,
    user_service: Annotated[UserService, Depends(get_user_service)],
    session = Depends(get_session),
) -> None:
    await user_service.delete_user(email, session=session)
