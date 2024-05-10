import logging
import os
from platform import python_version

from logginger.fmts import DEFAULT_FMT
from logginger.formatters import NoStacktraceFormatter, DefaultFormatter
from logginger.slack import SlackLogHandler
from logginger.utils import add_handlers
from logginger.uvicorn import ColorizedFormatter

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logger = logging.getLogger("debug_application")
logger.setLevel(logging.DEBUG)

default_formatter = DefaultFormatter(
    "%(levelprefix)s %(asctime)s (%(name)s) %(message)s"
)
no_stacktrace_formatter = NoStacktraceFormatter(
    "%(levelprefix)s %(asctime)s (%(name)s) %(message)s"
)

default_handler = logging.StreamHandler()
default_handler.setFormatter(default_formatter)

slack_handler = SlackLogHandler(webhook_url=WEBHOOK_URL, stack_trace=True)
slack_handler.setFormatter(no_stacktrace_formatter)
slack_handler.setLevel(logging.ERROR)

handlers = [default_handler, slack_handler]
add_handlers(logger, handlers)

# Main code
logger.info("Python version is {}".format(python_version()))

logger.debug("Test DEBUG")
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

logger.debug("Test DEBUG")
logger.info("Test INFO")
logger.warning("Test WARNING")
logger.error("Test ERROR")
logger.fatal("Test FATAL")
logger.critical("Test CRITICAL")

try:
    raise Exception("Test exception")
except Exception as e:
    logger.exception(e)
