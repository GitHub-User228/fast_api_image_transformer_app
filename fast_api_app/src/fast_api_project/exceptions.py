from jinja2 import Undefined


class EnvironmentVariableUndefined(Undefined):
    """
    Custom Undefined class for Jinja2 templates to handle
    undefined environment variables.

    Attributes:
        name : str
            The name of the undefined environment variable.
    """

    def __str__(self) -> str:
        return f"Environment variable '{self.name}' is not defined"
