import json
from datetime import datetime
from typing import Annotated, Any, Dict, Optional, Text

import requests
import typer

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


DEFAULT_URL = "http://localhost"
DEFAULT_PORT = 8176


@app.command()
def check_health(
    server_url: str = DEFAULT_URL, server_port: int = DEFAULT_PORT
) -> None:
    resp = requests.get(f"{server_url}:{server_port}/health")
    typer.echo(resp.json())


@app.command()
def get_num_jobs(
    server_token: Annotated[str, typer.Option(..., "--token", "-t")],
    server_url: str = DEFAULT_URL,
    server_port: int = DEFAULT_PORT,
) -> None:
    resp = requests.get(
        f"{server_url}:{server_port}/jobs/number",
        headers={"x-token": server_token},
    )
    typer.echo(resp.json())


@app.command(help="Currently not supporting success and failure actions")
def create_http_job(
    url: str,
    server_token: Annotated[str, typer.Option(..., "--token", "-t")],
    server_url: str = DEFAULT_URL,
    server_port: int = DEFAULT_PORT,
    method: str = "GET",
    headers: str = "{}",
    body: Optional[str] = None,
    run_at: Optional[str] = datetime.now().isoformat(),
) -> None:
    headers_obj = json.loads(headers)
    body_obj = json.loads(body) if body else None
    run_at_dt = datetime.fromisoformat(run_at) if run_at else datetime.now()

    job: Dict[Text, Any] = {
        "job": {
            "name": "http_job",
            "run_at": run_at_dt.isoformat(),
            "action": {
                "http": {
                    "url": url,
                    "method": method,
                    "headers": headers_obj,
                    "body": body_obj,
                },
            },
        }
    }

    response = requests.post(
        f"{server_url}:{server_port}/jobs/create",
        json=job,
        headers={"x-token": server_token},
    )
    typer.echo(response.json())


@app.command()
def remove_job(
    job_uuid: str,
    server_token: Annotated[str, typer.Option(..., "--token", "-t")],
    server_url: str = DEFAULT_URL,
    server_port: int = DEFAULT_PORT,
) -> None:
    response = requests.delete(
        f"{server_url}:{server_port}/jobs/{job_uuid}",
        headers={"x-token": server_token},
    )
    typer.echo(response.json())


@app.command()
def get_all_jobs(
    server_token: Annotated[str, typer.Option(..., "--token", "-t")],
    server_url: str = DEFAULT_URL,
    server_port: int = DEFAULT_PORT,
) -> None:
    response = requests.get(
        f"{server_url}:{server_port}/jobs",
        headers={"x-token": server_token},
    )
    typer.echo(json.dumps(response.json(), indent=2))


@app.command()
def get_job(
    job_uuid: str,
    server_token: Annotated[str, typer.Option(..., "--token", "-t")],
    server_url: str = DEFAULT_URL,
    server_port: int = DEFAULT_PORT,
) -> None:
    response = requests.get(
        f"{server_url}:{server_port}/jobs/{job_uuid}",
        headers={"x-token": server_token},
    )
    typer.echo(json.dumps(response.json(), indent=2))


@app.command()
def clear_all_jobs(
    server_token: Annotated[str, typer.Option(..., "--token", "-t")],
    server_url: str = DEFAULT_URL,
    server_port: int = DEFAULT_PORT,
) -> None:
    response = requests.delete(
        f"{server_url}:{server_port}/jobs",
        headers={"x-token": server_token},
    )
    typer.echo(response.json())


if __name__ == "__main__":
    app()
