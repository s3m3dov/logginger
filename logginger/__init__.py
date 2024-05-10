import traceback
from logging import (
    Handler,
    Filter,
    LogRecord,
)
from typing import Optional, Dict, Any, Tuple
from warnings import warn

import six
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.webhook import WebhookClient

from .colors import COLORS, NOTSET_COLOR
from .formatters import NoStacktraceFormatter

DEFAULT_EMOJI = ":heavy_exclamation_mark:"
DEFAULT_MSG_LEN = 1300
DEFAULT_TRACEBACK_LEN = 700

__all__ = [
    "SlackLogHandler",
    "SlackLogFilter",
]


class SlackLogFilter(Filter):
    """
    Logging filter to decide when logging to Slack is requested, using
    the `extra` kwargs:

        `logger.info("...", extra={'notify_slack': True})`
    """

    def filter(self, record):
        return getattr(record, "notify_slack", False)


class SlackLogHandler(Handler):
    def __init__(
        self,
        slack_token: Optional[str] = None,
        channel: Optional[str] = None,
        webhook_url: Optional[str] = None,
        is_webhook: bool = True,
        is_debug: bool = False,
        stack_trace: bool = True,
        username: str = "Logging Alerts",
        icon_url: str = None,
        icon_emoji: str = None,
        fail_silent: bool = False,
        msg_len: int = DEFAULT_MSG_LEN,
        traceback_len: int = DEFAULT_TRACEBACK_LEN,
    ) -> None:
        """
        Initialize the Slack handler
        Args:
            slack_token (str): The Slack API token if not using webhook_url
            channel (str): The Slack channel to post to if not using webhook_url
            webhook_url (str): The Slack webhook URL if using webhook_url
            is_webhook (bool): Whether to use webhook_url or not
            is_debug (bool): Doesn't send Slack messages if True
            stack_trace (bool): Whether to include the stacktrace in the Slack message
            username (str): The username to use for the Slack message
            icon_url (str): The icon URL to use for the Slack message
            icon_emoji (str): The icon emoji to use for the Slack message
            fail_silent (bool): Whether to fail silently if the Slack API returns an error
            msg_len (int): The maximum length of the Slack message
            traceback_len (int): The maximum length of the stacktrace
        Returns:
            None
        """
        Handler.__init__(self)
        self.formatter = NoStacktraceFormatter()
        self.stack_trace = stack_trace
        self.fail_silent = fail_silent
        self.username = username
        self.icon_url = icon_url
        self.icon_emoji = icon_emoji if (icon_emoji or icon_url) else DEFAULT_EMOJI
        self.is_debug = is_debug
        self.is_webhook = is_webhook

        if is_webhook:
            if not webhook_url:
                raise ValueError(
                    "webhook_url is required when webhook delivery is enabled"
                )
            self.client = WebhookClient(webhook_url)
        else:
            if not slack_token:
                raise ValueError("slack_token is required when not using webhook_url")
            if not channel:
                raise ValueError("channel is required when not using webhook_url")
            self.client = WebClient(token=slack_token)
            self.channel = channel

        self.msg_len, self.trace_len = self._verify_character_length(
            msg_len, traceback_len
        )

    @staticmethod
    def _verify_character_length(msg_len: int, trace_len: int) -> Tuple[int, int]:
        if msg_len < 1:
            msg_len = DEFAULT_MSG_LEN
            warn(
                "msg_len must be greater than 0, using default value: %d"
                % DEFAULT_MSG_LEN
            )
        if trace_len < 1:
            trace_len = DEFAULT_TRACEBACK_LEN
            warn(
                "trace_len must be greater than 0, using default value: %d"
                % DEFAULT_TRACEBACK_LEN
            )

        if trace_len + msg_len > 4000:
            warn(
                f"msg_len + trace_len must be less than 4000, using default values: %d, %d"
                % (DEFAULT_MSG_LEN, DEFAULT_TRACEBACK_LEN)
            )
            msg_len = DEFAULT_MSG_LEN
            trace_len = DEFAULT_TRACEBACK_LEN

        return msg_len, trace_len

    @staticmethod
    def build_trace(record: LogRecord, fallback: str) -> Dict[str, Any]:
        """
        Build the Slack attachment for the stacktrace
        Args:
            record (LogRecord): The log record
            fallback (str): The fallback message to use if the stacktrace is not available
        Returns:
            dict: The Slack attachment
        """
        trace = {
            "fallback": fallback,
            "color": COLORS.get(record.levelno, NOTSET_COLOR),
        }

        if record.exc_info:
            text = "\n".join(traceback.format_exception(*record.exc_info))
            text = text[:DEFAULT_TRACEBACK_LEN]
            trace["text"] = f"```{text}```"
        return trace

    def _build_msg(self, record: LogRecord) -> str:
        """
        Build the Slack message
        Args:
            record (LogRecord): The log record
        Returns:
            str: The Slack message text
        """
        msg = six.text_type(self.format(record))
        msg = msg[:DEFAULT_MSG_LEN]
        return msg

    def build_msg(self, record: LogRecord) -> Dict[str, Any]:
        msg = self._build_msg(record)
        payload = {
            "color": COLORS.get(record.levelno, NOTSET_COLOR),
            "fallback": msg,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": self.username,
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"{msg}"},
                },
            ],
        }
        return payload

    def emit(self, record: LogRecord) -> None:
        """
        Emit a record.
        Args:
            record (LogRecord): The log record
        Returns:
            None
        Raises:
            SlackApiError: If the Slack API returns an error and fail_silent is False
        """
        message = self.build_msg(record)
        attachments = [message]
        if self.stack_trace:
            trace = self.build_trace(record, fallback=record.message)
            attachments.append(trace)

        try:
            if self.is_debug:
                return

            if self.is_webhook:
                self.client: WebhookClient
                self.client.send(attachments=attachments)
            else:
                self.client: WebClient
                self.client.chat_postMessage(
                    channel=self.channel,
                    username=self.username,
                    icon_url=self.icon_url,
                    icon_emoji=self.icon_emoji,
                    attachments=attachments,
                )
        except SlackApiError as e:
            if self.fail_silent:
                pass
            else:
                raise e
