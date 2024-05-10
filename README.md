# logginger

Logginger is a simple logging library that includes tools to extend the logging module.

[![image](https://img.shields.io/pypi/v/logginger.svg?style=flat-square)](https://pypi.python.org/pypi/logginger)
[![image](https://img.shields.io/pypi/wheel/logginger.svg?style=flat-square)](https://pypi.python.org/pypi/logginger)
[![image](https://img.shields.io/pypi/format/logginger.svg?style=flat-square)](https://pypi.python.org/pypi/logginger)
[![image](https://img.shields.io/pypi/pyversions/logginger.svg?style=flat-square)](https://pypi.python.org/pypi/logginger)
[![image](https://img.shields.io/pypi/status/logginger.svg?style=flat-square)](https://pypi.python.org/pypi/logginger)

## Description

A python package that provides logging tools such as handlers and formatter for logging.
This allows developers to use these tools to use in their python logging, and they have more control over the logging.

Additional features include:

1. Logging to Slack (via webhook or token)
2. Logging to File

## Installation

``` bash
pip install logginger
```

## Arguments

- slack_token (str): The Slack API token if not using `webhook_url`
  Generate a key at <https://api.slack.com/>
- channel (str): The Slack channel to post to if not using `webhook_url`
- webhook_url (str): The Slack webhook URL if using `webhook_url`
- is_webhook (bool): Whether to use webhook_url or not (Defaults to `True`)
- is_debug (bool): Doesn't send Slack messages if True (Defaults to `False`)
- stack_trace (bool): Whether to include the stacktrace in the Slack message (Defaults to `True`)
- username (str): The username to use for the Slack message (Not usable if using `webhook_url`)
- icon_url (str): The icon URL to use for the Slack message (Not usable if using `webhook_url`)
- icon_emoji (str): The icon emoji to use for the Slack message (Not usable if using `webhook_url`)
- msg_len (int): The maximum length of the Slack message (Defaults to `1300`)
- traceback_len (int): The maximum length of the stack_trace (Defaults to `700`)
- fail_silent (bool): Whether to fail silently if the Slack API returns an error (Defaults to `False`)
  Defaults to `False`. If your API key is invalid or for some other reason
  the API call returns an error, this option will silently ignore the API
  error. If you enable this setting, **make sure you have another log
  handler** that will also handle the same log events, or they may be lost
  entirely.

## Example Python logging handler

This is how you use log_to_slack as a regular Python
logging handler. This example will send a error message to a slack
channel.

``` python
import logging
import os

from logginger import SlackLogHandler
from logginger.formatters import NoStacktraceFormatter, DefaultFormatter

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logger = logging.getLogger("debug_application")
logger.setLevel(logging.DEBUG)

default_formatter = DefaultFormatter("%(levelprefix)s %(asctime)s (%(name)s) %(message)s")
no_stacktrace_formatter = NoStacktraceFormatter("%(levelprefix)s %(asctime)s (%(name)s) %(message)s")

default_handler = logging.StreamHandler()
default_handler.setFormatter(default_formatter)
logger.addHandler(default_handler)

slack_handler = SlackLogHandler(webhook_url=WEBHOOK_URL, stack_trace=True)
slack_handler.setFormatter(no_stacktrace_formatter)
slack_handler.setLevel(logging.ERROR)
logger.addHandler(slack_handler)

# Main code
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

```

## Slack message formatting

This example use a subclass that will send a formatted message to a
Slack channel. [Learn More](https://api.slack.com/reference/surfaces/formatting)

``` python
class CustomLogHandler(SlackLogHandler):
    def build_msg(self, record):
        message = "> New message :\n" + record.getMessage()
        return message
```

## License

Apache 2.0

See also: 
- <https://api.slack.com/terms-of-service>
