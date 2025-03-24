import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Text

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from job_scheduler import domain
from job_scheduler.api_models import CreateJob
from job_scheduler.scheduler import (
    get_num_apscheduler_jobs,
    start_apscheduler,
    stop_apscheduler,
)
from job_scheduler.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    await start_apscheduler()

    yield

    logger.info("Shutting down the application...")
    await stop_apscheduler()


app = FastAPI(lifespan=lifespan)


class CustomLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Any, call_next: Any):
        response = await call_next(request)

        if request.url.path == "/health":
            logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

        return response


app.add_middleware(CustomLoggingMiddleware)


def verify_token(x_token: str = Header(None)):
    if x_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Missing or invalid authentication token (x-token header)",
        )


@app.get("/health", response_class=JSONResponse)
async def health_check() -> JSONResponse:
    try:
        try:
            await get_num_apscheduler_jobs()
        except Exception:
            data = {
                "status": "unhealthy",
            }
            return JSONResponse(content=data, status_code=500)
        else:
            data = {
                "status": "healthy",
            }
            return JSONResponse(content=data)
    except ValueError as exp:
        return JSONResponse(
            content={"error_type": "client", "error_message": str(exp)},
            status_code=400,
        )
    except Exception as exp:
        logger.exception("Error in health check")
        return JSONResponse(
            content={"error_type": "server", "error_message": str(exp)},
            status_code=500,
        )


@app.post("/jobs/create", response_class=JSONResponse)
async def create_job(
    params: CreateJob,
    token: str = Depends(verify_token),
) -> JSONResponse:
    try:
        logger.debug(f"Create job called with params: {params}")

        return JSONResponse(content=await domain.create_job(job=params.job))
    except ValueError as exp:
        return JSONResponse(
            content={"error_type": "client", "error_message": str(exp)},
            status_code=400,
        )
    except Exception as exp:
        logger.exception("Error in create job")
        return JSONResponse(
            content={"error_type": "server", "error_message": str(exp)},
            status_code=500,
        )


@app.delete("/jobs", response_class=JSONResponse)
async def clear_jobs(token: str = Depends(verify_token)) -> JSONResponse:
    try:
        logger.debug("Clear jobs called.")

        return JSONResponse(content=await domain.clear_jobs_from_scheduler())
    except ValueError as exp:
        return JSONResponse(
            content={"error_type": "client", "error_message": str(exp)},
            status_code=400,
        )
    except Exception as exp:
        logger.exception("Error in clear jobs")
        return JSONResponse(
            content={"error_type": "server", "error_message": str(exp)},
            status_code=500,
        )


@app.delete("/jobs/{job_uuid}", response_class=JSONResponse)
async def remove_job(
    job_uuid: str, token: str = Depends(verify_token)
) -> JSONResponse:
    try:
        logger.debug(f"Remove job called with job_uuid={job_uuid}.")

        return JSONResponse(
            content=await domain.remove_job_from_scheduler(job_uuid=job_uuid)
        )
    except ValueError as exp:
        return JSONResponse(
            content={"error_type": "client", "error_message": str(exp)},
            status_code=400,
        )
    except Exception as exp:
        logger.exception("Error in remove job")
        return JSONResponse(
            content={"error_type": "server", "error_message": str(exp)},
            status_code=500,
        )


@app.get("/jobs/number", response_class=JSONResponse)
async def get_num_jobs(token: str = Depends(verify_token)) -> JSONResponse:
    try:
        data: Dict[Text, Any] = {
            "num_jobs": await get_num_apscheduler_jobs(),
        }
        return JSONResponse(content=data)
    except ValueError as exp:
        return JSONResponse(
            content={"error_type": "client", "error_message": str(exp)},
            status_code=400,
        )
    except Exception as exp:
        logger.exception("Error in get num jobs")
        return JSONResponse(
            content={"error_type": "server", "error_message": str(exp)},
            status_code=500,
        )


@app.get("/jobs", response_class=JSONResponse)
async def get_jobs(token: str = Depends(verify_token)) -> JSONResponse:
    try:
        logger.debug("Get all jobs called.")

        return JSONResponse(content=await domain.get_jobs_from_scheduler())
    except ValueError as exp:
        return JSONResponse(
            content={"error_type": "client", "error_message": str(exp)},
            status_code=400,
        )
    except Exception as exp:
        logger.exception("Error in get jobs")
        return JSONResponse(
            content={"error_type": "server", "error_message": str(exp)},
            status_code=500,
        )


@app.get("/jobs/{job_uuid}", response_class=JSONResponse)
async def get_job(
    job_uuid: str, token: str = Depends(verify_token)
) -> JSONResponse:
    try:
        logger.debug("Get all jobs called.")

        return JSONResponse(
            content=await domain.get_job_from_scheduler(job_uuid=job_uuid)
        )
    except ValueError as exp:
        return JSONResponse(
            content={"error_type": "client", "error_message": str(exp)},
            status_code=400,
        )
    except Exception as exp:
        logger.exception("Error in get job")
        return JSONResponse(
            content={"error_type": "server", "error_message": str(exp)},
            status_code=500,
        )
