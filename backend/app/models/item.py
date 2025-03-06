from pydantic import BaseModel
from decimal import Decimal

class Item(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Decimal
    in_stock: bool