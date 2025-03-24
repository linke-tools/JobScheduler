from typing import Any, Dict, List, Text

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore  # type: ignore
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from job_scheduler.job_runner import JobRunner
from job_scheduler.models import RunnableJob
from job_scheduler.settings import settings

DATABASE_URL = f"{settings.DB_SCHEMA_APSCHEDULER}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


engine: AsyncEngine = create_async_engine(
    DATABASE_URL, echo=False, future=True
)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


scheduler = AsyncIOScheduler(
    jobstores={"default": SQLAlchemyJobStore(url=DATABASE_URL)},
    job_defaults={"coalesce": False, "max_instances": 3},
    timezone=settings.TIMEZONE,
)

job_runner = JobRunner()


async def start_apscheduler():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: conn.execute(text("SELECT 1")))
        logger.debug("Database connection successful.")
    except SQLAlchemyError as e:
        logger.exception("Database connection failed.")
        raise e

    logger.debug("Starting APScheduler...")
    scheduler.start()  # type: ignore


async def stop_apscheduler():
    logger.debug("Stopping APScheduler...")
    scheduler.shutdown(wait=False)  # type: ignore
    await engine.dispose()
    logger.debug("APScheduler and database connections closed...")


async def get_num_apscheduler_jobs():
    return len(scheduler.get_jobs())  # type: ignore


async def add_job_to_scheduler(job: RunnableJob) -> str:
    try:
        scheduler.add_job(job_runner.run_job, "date", run_date=job.job.run_at, args=[job], id=job.uuid, misfire_grace_time=None, max_instances=1)  # type: ignore
        logger.debug(
            f"Added job {job.uuid} to the scheduler to run at date={job.job.run_at}."
        )
        return job.uuid
    except Exception as exp:
        logger.error(f"Error adding job {job.uuid} to the scheduler: {exp}")
        raise exp


async def clear_jobs_from_scheduler() -> int:
    try:
        num_jobs = len(scheduler.get_jobs())  # type: ignore
        scheduler.remove_all_jobs()  # type: ignore
        logger.debug(f"Removed {num_jobs} unscheduled jobs from scheduler.")
        return num_jobs
    except Exception as exp:
        logger.error(
            f"Error removing all unscheduled jobs from scheduler: {exp}"
        )
        raise exp


def job_to_dict(job: Any) -> Dict[Text, Any]:
    return {
        "id": job.id,
        "name": job.name,
        "trigger": str(job.trigger),
        "next_run_time": job.next_run_time.isoformat()
        if job.next_run_time
        else None,
        "args": job.args[1],
        "kwargs": job.kwargs,
        "misfire_grace_time": job.misfire_grace_time,
        "max_instances": job.max_instances,
    }


async def get_jobs_from_scheduler() -> List[Any]:
    return [job.args[1].dict() for job in scheduler.get_jobs()]  # type: ignore


async def remove_job_from_scheduler(job_uuid: str) -> None:
    try:
        scheduler.remove_job(job_uuid)  # type: ignore
        logger.debug(f"Removed job {job_uuid} from scheduler.")
    except Exception as exp:
        logger.error(f"Error removing job {job_uuid} from scheduler: {exp}")
        raise exp
