import contextlib
import functools
import inspect
import logging
import sys
from typing import Any, Callable, Iterator

import structlog

from investmentstk.utils.environment import is_in_cloud_run
from investmentstk.utils.logger_processors import (
    prefix_logger_name_on_message,
    rename_event_to_msg,
    ModuleInfoProcessor,
)


def _initialize_stlib_logger() -> None:
    """
    We use still use the stdlib logging module as a medium for structlog. Structlog is only formatting
    the messages, and stdlib logging module prints it on the console.
    """
    stdlib_logger = logging.getLogger("investmentstk")
    stdlib_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)

    stdlib_logger.addHandler(console_handler)
    # stdlib_logger.propagate = False


def _initialize_structlog() -> None:
    """
    If running locally, use a console renderer with colors and human-friendly.
    If running on GCP, use a JSON renderer and add some extra information
    """
    _initialize_stlib_logger()

    if not is_in_cloud_run():
        extra_processors = [
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
            prefix_logger_name_on_message,
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        extra_processors = [
            structlog.processors.TimeStamper(fmt="iso"),
            ModuleInfoProcessor(add_lineno=True, add_module=True),
            rename_event_to_msg,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=[
            structlog.threadlocal.merge_threadlocal,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            *extra_processors,  # type: ignore
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(*args, **kwargs) -> Any:
    """
    To be called by our code anywhere a logger is needed
    """
    return structlog.get_logger(*args, **kwargs)


def bind_on_logger(**kwargs) -> None:
    """
    Alias for structlog thread local binding.

    :param kwargs: kwargs to be bound on logger
    :return:
    """
    structlog.threadlocal.bind_threadlocal(**kwargs)


@contextlib.contextmanager
def logger_unbind(*args) -> Iterator[None]:
    """
    Similar to autobind_on_logger(), but only does unbinding. Useful when
    the binding uses values that are not available in the decorator context (such as an argument
    to the wrapped function), and only auto unbinding is needed.

    Usually paired with a manual `bind_on_logger` call inside the context.

    :param args: kwargs to be bound on logger
    :return:
    """
    try:
        yield
    finally:
        structlog.threadlocal.unbind_threadlocal(*args)


@contextlib.contextmanager
def logger_autobind(**kwargs) -> Iterator[None]:
    """
    Binds and automatically unbinds values on the logger, similar to the built in `tmp_bind` on structlog, but using
    thread local. Should be used either as a context manager or a decorator.

    :param kwargs: kwargs to be bound on logger
    """
    bind_on_logger(**kwargs)

    with logger_unbind(*kwargs.keys()):
        yield


class logger_autobind_from_args:
    """
    A decorator that temporarily binds values on structlog loggers (thread local) by extracting the values
    from the wrapped function arguments.

    It accepts named arguments where the argument name is the key to be used when binding to the logger and the value
    is the name of the parameter of the wrapped function where the value is extracted from

    Example:
        @logger_autobind_from_args(name="n")
        def func(n):
            logger.info("Inside function")

        func('Joe')

    Will bind `name=Joe` on the logged line.
    """

    def __init__(self, **bind_config):
        self.bind_config = bind_config

    def __call__(self, wrapped: Callable) -> Callable:
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs):
            # Extracts the actual values used in the wrapped function call
            callargs = inspect.getcallargs(wrapped, *args, **kwargs)
            bind_key_pair = {bind_name: callargs[arg_name] for bind_name, arg_name in self.bind_config.items()}

            with logger_autobind(**bind_key_pair):
                return wrapped(*args, **kwargs)

        return wrapper


# Initializes the logger
# If every log caller loads this file to use get_logger(), the line below is guaranteed to be executed and
# Python only executes it once
_initialize_structlog()
