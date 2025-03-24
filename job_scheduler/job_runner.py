from datetime import datetime

from loguru import logger

from job_scheduler.commands import Command
from job_scheduler.models import RunnableJob


class JobRunner:
    async def run_job(self, job: RunnableJob) -> None:
        try:
            try:
                logger.debug(f"Running job {job} at {datetime.now()}...")

                command = Command.get_command(job.job.action)

                await command.execute(context=job.to_context())

            except Exception as exp:
                logger.error(f"Error running job {job}: {exp}")

                if job.job.on_failure:
                    try:
                        failure_command = Command.get_command(
                            job.job.on_failure
                        )
                        await failure_command.execute(context=job.to_context())
                    except Exception as exp:
                        logger.error(
                            f"Error running failure follow-up action for job {job}: {exp}"
                        )
            else:
                logger.debug(
                    f"Job {job} completed successfully at {datetime.now()}"
                )

                try:
                    if job.job.on_success:
                        success_command = Command.get_command(
                            job.job.on_success
                        )
                        await success_command.execute(context=job.to_context())
                except Exception as exp:
                    logger.error(
                        f"Error running success follow-up action for job {job}: {exp}"
                    )
        except Exception as exp:
            # Saveguard to prevent crashing the scheduler
            logger.exception(f"Uncaught exception in job runner: {exp}")
