import abc
import asyncio
from typing import Any, Dict, Optional, Text

import aiohttp
from loguru import logger

from job_scheduler.models import JobAction


class Command(metaclass=abc.ABCMeta):
    def __init__(self, type: str) -> None:
        self.type = type

    def __str__(self) -> str:
        return f"Command<{self.type}>"

    def __repr__(self) -> str:
        return str(self)

    @abc.abstractmethod
    async def execute(self, context: Dict[Text, Any]):
        ...

    @staticmethod
    def get_command(action: JobAction) -> "Command":
        if action.http:
            return HTTPCommand(
                url=action.http.url,
                method=action.http.method,
                headers=action.http.headers,
                body=action.http.body,
                timeout=action.http.timeout,
            )
        else:
            raise ValueError(f"Unsupported job action: {action}")


class HTTPCommand(Command):
    DEFAULT_TIMEOUT = 360

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: Dict[Text, Any] = {},
        body: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        super().__init__(type="http")
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body
        self.timeout = timeout

    def __str__(self) -> str:
        return f"HTTPCommand<{self.url}, {self.method}, {self.headers}, {self.body}>"

    async def execute(self, context: Dict[Text, Any]):
        logger.debug(
            f"Executing HTTP command in context={repr(context)}: {self}"
        )

        session_timeout = aiohttp.ClientTimeout(
            total=self.timeout
            if self.timeout
            else self.__class__.DEFAULT_TIMEOUT
        )

        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            try:
                async with session.request(
                    method=self.method,
                    url=self.url,
                    headers=self.headers,
                    data=self.body,
                ) as response:
                    status = response.status

                    if not (200 <= status < 300):
                        raise ValueError(
                            f"HTTP command for context={repr(context)} failed with status={status}"
                        )

                    response_body = await response.text()
                    logger.debug(
                        f"HTTP response for context={repr(context)}: {response.status}, {response_body}"
                    )
            except asyncio.exceptions.TimeoutError as exp:
                logger.exception(
                    f"HTTP command for context={repr(context)} timed out"
                )
                raise exp
