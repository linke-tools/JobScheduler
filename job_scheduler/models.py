from datetime import datetime
from typing import Any, Dict, Optional, Text

import pydantic


class HTTPJobData(pydantic.BaseModel):
    url: str
    method: str = "GET"
    headers: Dict[Text, Any] = {}
    body: Optional[str] = None
    timeout: Optional[int] = None


class JobAction(pydantic.BaseModel):
    """Supported command types"""

    http: Optional[HTTPJobData] = None


class Job(pydantic.BaseModel):
    name: str
    category: Optional[str] = None

    run_at: datetime

    action: JobAction
    on_success: Optional[JobAction] = None
    on_failure: Optional[JobAction] = None

    @pydantic.field_serializer("run_at")
    def serialize_run_at(self, run_at: datetime) -> str:
        return run_at.isoformat()


class RunnableJob(pydantic.BaseModel):
    job: Job
    uuid: str

    def to_context(self) -> Dict[Text, Any]:
        return {
            "job_category": self.job.category,
            "job_name": self.job.name,
            "job_uuid": self.uuid,
        }
