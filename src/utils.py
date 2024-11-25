import os
import subprocess
import shlex

from typing import TypeVar, Type, Callable, Optional, cast
from jinja2 import Environment, FileSystemLoader

from src.logging import logger


T = TypeVar('T')


def render_template(name: str, **kwargs) -> str:
    """Render a Jinja template."""
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))
    template = env.get_template(name)
    return template.render(**kwargs)

def run_subprocess(
    command: str,
    shell: bool = False,
    input: Optional[str] = None,
    streaming: bool = False
) -> int:
    """Run a subprocess, print its output (either stdout or stderr), and return its exit code."""
    if streaming:
        process = subprocess.Popen(
            shlex.split(command) if not shell else command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"\033[90m| {output.strip()}\033[0m")
        stderr = process.stderr.read()
        if stderr:
            print(f"\033[91m{stderr.strip()}\033[0m")
        return process.returncode
    else:
        process = subprocess.run(
            shlex.split(command) if not shell else command,
            shell=shell,
            input=input.encode() if input is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.stdout, process.stderr

        for line in stdout.decode().splitlines():
            print(f"\033[90m| {line}\033[0m")
        if stderr:
            print(f"\033[91m{stderr.decode()}\033[0m")

        return process.returncode


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