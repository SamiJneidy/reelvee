from fastapi import status
from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")

class SingleResponse(BaseModel, Generic[T]):
    data: T = Field(..., description="This may be any schema value")

class ListResponse(BaseModel, Generic[T]):
    data: list[T] = Field(..., description="This may be any schema value")

class SuccessResponse(BaseModel):
    detail: str = Field(
        default="Success", 
        description="The detail of the success response", 
        example="The request was processed successfully"
    )
    status_code: int = Field(
        default=status.HTTP_200_OK, 
        description="The status code of the success response", 
        example=status.HTTP_200_OK
    )

class ErrorResponse(BaseModel):
    detail: str = Field(
        default="Error", 
        description="The detail of the error response", 
        example="An error occurred while processing the request"
    )
    status_code: int = Field(
        default=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        description="The status code of the error response", 
        example=status.HTTP_400_BAD_REQUEST
    )
