import asyncio
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.modules.storage.schemas import FileResponse
from app.modules.storage.service import StorageService


class PDFService:
    TEMPLATE_DIR = Path(__file__).parent / "templates"

    def __init__(self, env: Environment, storage: StorageService) -> None:
        self._env = env
        self._storage = storage

    def _render_pdf_sync(self, template_name: str, context: dict) -> bytes:
        html = self._env.get_template(template_name).render(**context)
        return HTML(string=html).write_pdf()

    async def render_bytes(self, template_name: str, context: dict) -> bytes:
        return await asyncio.to_thread(self._render_pdf_sync, template_name, context)

    async def render_and_upload(
        self,
        template_name: str,
        filename: str,
        context: dict,
        path: str,
    ) -> FileResponse:
        pdf_bytes = await self.render_bytes(template_name, context)
        return await self._storage.upload_bytes(
            path=path,
            filename=filename,
            content=pdf_bytes,
            content_type="application/pdf",
        )

    async def delete_pdf(self, key: str) -> None:
        await self._storage.delete_file(key)
