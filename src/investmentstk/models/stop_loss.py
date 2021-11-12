import datetime

from pydantic import BaseModel


class StopLoss(BaseModel):
    fqn_id: str
    trigger: float
    valid_until: datetime.date
