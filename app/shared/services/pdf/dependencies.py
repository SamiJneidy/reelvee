from functools import lru_cache

from fastapi import Depends
from jinja2 import Environment, FileSystemLoader

from app.modules.storage.dependencies import StorageService, get_storage_service
from app.shared.services.pdf.service import PDFService


@lru_cache
def get_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(PDFService.TEMPLATE_DIR),
        autoescape=True,
    )


def get_pdf_service(
    env: Environment = Depends(get_jinja_env),
    storage: StorageService = Depends(get_storage_service),
) -> PDFService:
    return PDFService(env, storage)
