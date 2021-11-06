import inspect

from structlog._frames import _find_first_app_frame_and_name
from structlog.types import EventDict, WrappedLogger


class ModuleInfoProcessor:
    """
    Using the stdlib logging library automatically gives us some execution context, such as line number,
    module name and function name. This processor adds some of this information to structlog logs.

    Attributes from stdlib logging: https://docs.python.org/3/library/logging.html#logrecord-attributes
    This class is heavily inspired by
        https://stackoverflow.com/questions/54872447/how-to-add-code-line-number-using-structlog
    """

    def __init__(self, add_lineno: bool = False, add_module: bool = False, add_funcname: bool = False):
        self.add_lineno = add_lineno
        self.add_module = add_module
        self.add_funcname = add_funcname

    def __call__(self, _: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
        # If by any chance the record already contains a `modline` key,
        # (very rare) move that into a 'modline_original' key
        if "modline" in event_dict:
            event_dict["modline_original"] = event_dict["modline"]

        f, name = _find_first_app_frame_and_name(
            additional_ignores=[
                "logging",
                __name__,  # could just be __name__
            ]
        )

        if not f:
            return event_dict

        frameinfo = inspect.getframeinfo(f)

        if not frameinfo:
            return event_dict

        module = inspect.getmodule(f)

        if not module:
            return event_dict

        if self.add_lineno:
            event_dict["lineno"] = frameinfo.lineno

        if self.add_module:
            event_dict["module"] = module.__name__

        if self.add_funcname:
            event_dict["funcName"] = frameinfo.function

        return event_dict


def prefix_logger_name_on_message(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
    """
    On dev, append the logger name in the message for extra readibility
    """
    logger_name = event_dict.pop("logger", "None")

    event_dict["event"] = f'[{logger_name.split(".")[-1]}] ' + event_dict["event"]
    return event_dict


def rename_event_to_msg(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
    """
    When not in prod, rename "event" (structlog default) to "message" (GCP convention)
    https://cloud.google.com/logging/docs/structured-logging#special-payload-fields
    """
    event = event_dict.pop("event", None)

    if event:
        event_dict["message"] = event

    return event_dict
