from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class BaseSchemaCreationReqSchema(BaseModel):
    is_active: bool = True


class BaseSchemaEditReqSchema(BaseModel):
    is_active: bool


class BaseSchemaListingReqSchema(BaseModel):
    is_active: Optional[bool]
    start_time: Optional[str]
    end_time: Optional[str]
    ordering: Optional[str]

    def get_start_time(self):
        if self.start_time:
            try:
                start_time_obj = datetime.strptime(self.start_time, '%Y-%m-%dT%H:%M:%SZ')
                return start_time_obj
            except ValueError as e:
                raise ValueError(f"Start time format is incorrect: {e}")
        return None

    def get_end_time(self):
        if self.end_time:
            try:
                end_time_obj = datetime.strptime(self.end_time, '%Y-%m-%dT%H:%M:%SZ')
                return end_time_obj
            except ValueError as e:
                raise ValueError(f"End time format is incorrect: {e}")
        return None
