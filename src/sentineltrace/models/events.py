from datetime import datetime

from pydantic import BaseModel


class SecurityEvent(BaseModel):
    event_id: str
    timestamp: datetime
    user_id: str
    device_id: str
    event_type: str
    success: bool
    source_ip: str
    country: str
    user_agent: str
    resource: None | str
    session_id: None | str