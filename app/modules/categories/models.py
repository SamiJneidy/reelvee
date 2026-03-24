from beanie import Indexed

from app.shared.models.base import BaseDocument


class Category(BaseDocument):
    name: Indexed(str, unique=True)

    class Settings:
        name = "categories"
