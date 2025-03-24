import os


class Settings:
    def __init__(self):
        self.LOGURU_LEVEL = os.getenv("LOGURU_LEVEL", "DEBUG")
        self.DB_SCHEMA = os.getenv("DB_SCHEMA")
        self.DB_SCHEMA_APSCHEDULER = os.getenv("DB_SCHEMA_APSCHEDULER")
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.API_TOKEN = os.getenv("API_TOKEN")
        self.TIMEZONE = os.getenv("TIMEZONE", "Europe/Berlin")

        self._REQUIRED_ENV_VARS = [
            "DB_SCHEMA",
            "DB_SCHEMA_APSCHEDULER",
            "DB_HOST",
            "DB_PORT",
            "DB_NAME",
            "DB_USER",
            "DB_PASSWORD",
            "API_TOKEN",
            "TIMEZONE",
        ]

        for env_var in self._REQUIRED_ENV_VARS:
            if self.__dict__[env_var] is None:
                raise ValueError(f"Missing environment variable: {env_var}")


settings = Settings()
