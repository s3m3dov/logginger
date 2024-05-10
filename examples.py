import logging
import os
from platform import python_version

from logginger.fmts import DEFAULT_FMT
from logginger.formatters import NoStacktraceFormatter, DefaultFormatter
from logginger.slack import SlackLogHandler, SlackLogFilter
from logginger.utils import add_handlers
from logginger.uvicorn import ColorizedFormatter

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logger = logging.getLogger("debug_application")
logger.setLevel(logging.DEBUG)

default_formatter = DefaultFormatter(fmt=DEFAULT_FMT)
no_stacktrace_formatter = NoStacktraceFormatter(fmt=DEFAULT_FMT)

default_handler = logging.StreamHandler()
default_handler.setFormatter(default_formatter)

slack_handler_level = SlackLogHandler(webhook_url=WEBHOOK_URL)
slack_handler_level.setFormatter(no_stacktrace_formatter)
slack_handler_level.setLevel(logging.ERROR)

slack_handler_manual = SlackLogHandler(webhook_url=WEBHOOK_URL)
slack_handler_manual.setFormatter(no_stacktrace_formatter)
slack_handler_manual.addFilter(SlackLogFilter())

handlers = [default_handler, slack_handler_level, slack_handler_manual]
add_handlers(logger, handlers)

# Main code
logger.info("Python version is {}".format(python_version()))

logger.debug("Test DEBUG", extra={"notify_slack": True})
logger.info("Test INFO")
logger.warning("Test WARNING")
logger.error("Test ERROR")
logger.fatal("Test FATAL")
logger.critical("Test CRITICAL")

try:
    raise Exception("Test exception" * 2000)
except Exception as e:
    logger.exception(e)

# Change formatter
for handler in logger.handlers:
    logger.removeHandler(handler)

logger.addHandler(default_handler)

for handler in logger.handlers:
    handler.formatter = ColorizedFormatter(fmt=DEFAULT_FMT, use_colors=True)

logger.debug("Test DEBUG", extra={"notify_slack": True})
logger.info("Test INFO")
logger.warning("Test WARNING")
logger.error("Test ERROR")
logger.fatal("Test FATAL")
logger.critical("Test CRITICAL")

try:
    raise Exception("Test exception")
except Exception as e:
    logger.exception(e)
