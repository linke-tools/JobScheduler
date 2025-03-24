import uuid
from typing import Any, Dict, Text

from job_scheduler import scheduler
from job_scheduler.models import Job, RunnableJob


async def create_job(job: Job) -> Dict[Text, Any]:
    job_uuid = await scheduler.add_job_to_scheduler(
        job=RunnableJob(job=job, uuid=str(uuid.uuid4()))
    )
    return {"status": "success", "job_uuid": job_uuid}


async def clear_jobs_from_scheduler() -> Dict[Text, Any]:
    num_jobs = await scheduler.clear_jobs_from_scheduler()
    return {"status": "success", "num_jobs": num_jobs}


async def get_job_from_scheduler(job_uuid: str) -> Dict[Text, Any]:
    jobs = await scheduler.get_jobs_from_scheduler()

    for job in jobs:
        if job["uuid"] == job_uuid:
            return {"status": "success", "job": job}

    return {"status": "error", "message": "Job not found"}


async def get_jobs_from_scheduler() -> Dict[Text, Any]:
    jobs = await scheduler.get_jobs_from_scheduler()
    return {"status": "success", "jobs": jobs}


async def remove_job_from_scheduler(job_uuid: str) -> Dict[Text, Any]:
    await scheduler.remove_job_from_scheduler(job_uuid=job_uuid)
    return {"status": "success", "job_uuid": job_uuid}
