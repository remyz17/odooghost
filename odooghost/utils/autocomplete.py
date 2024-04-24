import os
from typing import Generator

from odooghost.constant import STACK_CONFIG_FILE_EXTENSIONS
from odooghost.services.base import BaseService
from odooghost.stack import Stack


def ac_stacks_lists(incomplete: str) -> Generator:
    for stack in Stack.list():
        if stack.name.lower().startswith(incomplete.lower()):
            yield stack.name


def ac_stack_configs(incomplete: str) -> Generator:
    for file in os.listdir():
        if any(
            file.endswith(ext) for ext in STACK_CONFIG_FILE_EXTENSIONS
        ) and file.startswith(incomplete):
            yield file


def ac_stacks_services(incomplete: str) -> Generator:
    for service in BaseService.list(only_name=True):
        if service.startswith(incomplete) or not incomplete:
            yield service
