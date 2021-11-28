import datetime

from pydantic import BaseModel


class StopLoss(BaseModel):
    fqn_id: str
    trigger: float
    valid_until: datetime.date

    def to_response(self):
        """
        Formats the object to be represented in the HTTP response.
        """

        # For now, mostly column renaming in a more friendly way to be displayed in my Google Sheets
        return dict(fqn_id=self.fqn_id, stop_loss_trigger=self.trigger, stop_loss_valid_until=self.valid_until)
