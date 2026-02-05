from pydantic import BaseModel, ConfigDict


class MonitorOutputMode(BaseModel):
    width: int
    height: int
    refresh_rate_hz: float

    model_config = ConfigDict(from_attributes=True)


class MonitorOutput(BaseModel):
    name: str
    description: str
    x: int
    y: int
    width: int
    height: int
    scale: float
    transform: str
    scale_filter: str
    adaptive_sync: bool
    is_dpms_enabled: bool
    modes: list[MonitorOutputMode]
    model_config = ConfigDict(from_attributes=True)
