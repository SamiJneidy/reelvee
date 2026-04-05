from fastapi import APIRouter, Depends, Request, Response, status
from typing import Annotated

from app.core.context import CurrentUser
from app.core.database import get_session
from app.modules.auth.dependencies import get_auth_service, get_request_context, get_user_from_sign_up_complete_token
from app.modules.auth.service import AuthService
from app.modules.users.schemas.requests import ChangeEmailRequest, RequestEmailChangeRequest, SignUpCompleteRequest
from app.modules.users.schemas.responses import SignUpCompleteResponse, UserResponse
from app.shared.schemas import SingleResponse
from app.shared.schemas.responses import SuccessResponse
from .dependencies import UserService, get_user_service
from .schemas import UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ---------------------------------------------------------------------
# POST routes
# ---------------------------------------------------------------------

@router.post(
    "/signup/complete",
    response_model=SingleResponse[SignUpCompleteResponse],
    summary="Complete sign up (onboarding)",
    description=(
        "Finishes onboarding by saving personal profile fields to the users collection "
        "and creating the initial store in the stores collection."
    ),
)
async def sign_up_complete(
    request: Request,
    response: Response,
    body: SignUpCompleteRequest,
    session=Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
    current_user_to_complete: UserResponse = Depends(get_user_from_sign_up_complete_token),
) -> SingleResponse[SignUpCompleteResponse]:
    user = await user_service.sign_up_complete(current_user_to_complete.email, body, session)
    access_token = await auth_service.create_access_token(
        request, response, current_user_to_complete.id, set_cookie=False
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, current_user_to_complete.id, set_cookie=False
    )
    return SingleResponse[SignUpCompleteResponse](
        data=SignUpCompleteResponse(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    )


@router.post(
    "/request-email-change",
    response_model=SuccessResponse,
    summary="Request email change",
)
async def request_email_change(
    body: RequestEmailChangeRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_request_context),
    session=Depends(get_session),
) -> SuccessResponse:
    await user_service.request_email_change(current_user, body, session)
    return SuccessResponse(detail="Email change link sent successfully")


@router.post(
    "/confirm-email-change",
    response_model=SingleResponse[UserResponse],
    summary="Confirm email change",
)
async def confirm_email_change(
    body: ChangeEmailRequest,
    request: Request,
    response: Response,
    session=Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> SingleResponse[UserResponse]:
    user_internal = await user_service.confirm_email_change(body, session)
    await auth_service.revoke_all_refresh_tokens(user_internal.id)
    return SingleResponse[UserResponse](data=UserResponse.model_validate(user_internal))


# ---------------------------------------------------------------------
# PATCH routes
# ---------------------------------------------------------------------

@router.patch(
    "/me",
    response_model=SingleResponse[UserResponse],
    summary="Update current user profile",
)
async def update_current_user(
    body: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_request_context),
    session=Depends(get_session),
) -> SingleResponse[UserResponse]:
    data = await user_service.update_by_email(
        current_user.user.email,
        body.model_dump(exclude_none=True),
        session=session,
    )
    return SingleResponse[UserResponse](data=UserResponse.model_validate(data))


# ---------------------------------------------------------------------
# DELETE routes
# ---------------------------------------------------------------------

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user account",
)
async def delete_current_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: CurrentUser = Depends(get_request_context),
    session=Depends(get_session),
) -> None:
    await user_service.delete_user(current_user.user.email, session=session)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user by email (admin)",
)
async def delete_user_by_email(
    email: str,
    user_service: Annotated[UserService, Depends(get_user_service)],
    session=Depends(get_session),
) -> None:
    await user_service.delete_user(email, session=session)
