import pydantic

from job_scheduler.models import Job


class CreateJob(pydantic.BaseModel):
    job: Job
