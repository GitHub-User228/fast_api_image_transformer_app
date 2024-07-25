from pathlib import Path

from pydantic_settings import BaseSettings


class PathConfig(BaseSettings):
    app_root_path: Path
    app_path: Path
    config_path: Path
    log_path: Path
    static_path: Path
    templates_path: Path
    fast_api_endpoint: str

    class Config:
        env_file = ".env"

    @classmethod
    def from_env(cls) -> "PathConfig":
        """
        Create a new instance of PathConfig by loading environment
        variables.

        This class method initializes a new instance of PathConfig
        by loading environment variables from the specified .env file.
        It then validates the loaded environment variables to ensure
        that all required paths are set.

        Returns:
            PathConfig:
                A new instance of PathConfig with loaded and validated
                environment variables.

        Raises:
            ValueError:
                If any required environment variable is not set.
        """
        config = cls()
        config.validate_env_vars()
        return config

    def validate_env_vars(self) -> None:
        """
        Validate that all required environment variables are set.

        This method iterates through the fields of the PathConfig class
        and checks if each corresponding environment variable is set.
        If any required environment variable is not set, a ValueError
        is raised.

        Parameters:
            self (PathConfig):
                An instance of PathConfig to validate.

        Raises:
            ValueError:
                If any required environment variable is not set.
        """
        for field in self.model_fields:
            path = getattr(self, field)
            if path is None:
                raise ValueError(f"Environment variable '{field}' is not set.")
            if (field != "fast_api_endpoint") and (not path.exists()):
                raise ValueError(
                    f"The path '{path}' specified for '{field}' does not exist."
                )


path_vars = PathConfig.from_env()
