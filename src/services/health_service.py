from dataclasses import dataclass


@dataclass(frozen=True)
class HealthStatus:
    status: str
    service: str
    version: str


class HealthService:
    def get_status(self) -> HealthStatus:
        return HealthStatus(status="ok", service="EduTrack", version="v1")
