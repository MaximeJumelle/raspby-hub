import os

from typing import TypeVar, Type, Callable, Optional, cast
from jinja2 import Environment, FileSystemLoader

from src.logging import logger


T = TypeVar('T')


def render_template(name: str, **kwargs) -> str:
    """Render a Jinja template."""
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))
    template = env.get_template(name)
    return template.render(**kwargs)

def input_challenge(
    prompt: str,
    expected_type: Type[T] = str,
    validator: Optional[Callable[[T], bool]] = None
) -> T:
    """Prompt the user for input until the expected type is entered."""
    while True:
        raw_input = input(prompt)
        if len(raw_input) == 0:
            logger.warning("You must enter a value. Please try again.")
            continue

        try:
            value = cast(expected_type, expected_type.__call__(raw_input))
            if validator is not None and not validator(value):
                logger.warning("The value you entered is not valid. Please try again.")
                continue
            return value
        except ValueError:
            logger.warning("The value you entered is not valid. Please try again.")