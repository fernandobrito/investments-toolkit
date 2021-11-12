from pydantic import BaseModel


class BrokerBalance(BaseModel):
    balance: float
    currency: str
