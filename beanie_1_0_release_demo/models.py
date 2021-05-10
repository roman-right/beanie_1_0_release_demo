from typing import Optional

import pymongo
from beanie import Document, Indexed
from pydantic import BaseModel, Field


class Category(BaseModel):
    name: str
    description: str


class Product(Document):
    name: str
    description: Optional[str] = None
    price: Indexed(float, pymongo.DESCENDING)
    category: Category
    num: int

    class Collection:
        name = "products"
        indexes = [
            [
                ("name", pymongo.TEXT),
                ("description", pymongo.TEXT),
            ],
        ]


class ProductShortView(BaseModel):
    name: str
    price: float


class ProductCustomView(BaseModel):
    name: str
    category: str

    class Settings:
        projection = {"name": 1, "category": "$category.name"}


class TotalCountView(BaseModel):
    category: str = Field(None, alias="_id")
    total: int
