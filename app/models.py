from pydantic import BaseModel
from typing import Optional


class Settings(BaseModel):
    limit_pages: int
    proxy: Optional[str] = None


class Product(BaseModel):
    product_title: str
    product_price: float
    path_to_image: str
