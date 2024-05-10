from __future__ import annotations

import http
import logging
import sys
from copy import copy
from logging import Formatter, LogRecord
from typing import Literal

import click

from ._config import TRACE_LOG_LEVEL


class DefaultFormatter(Formatter):
    def format(self, record: LogRecord):
        level_name = record.levelname
        seperator = " " * (8 - len(record.levelname))
        record.levelprefix = level_name + ":" + seperator
        return super().format(record)


class NoStacktraceFormatter(DefaultFormatter):
    """
    By default, the stacktrace will be formatted as part of the message.
    Since we want the stacktrace to be in the attachment of the Slack message,
        we need a custom formatter to leave it out of the message
    """

    def formatException(self, ei):
        return None

    def format(self, record: LogRecord):
        # Work-around for https://bugs.python.org/issue29056
        saved_exc_text = record.exc_text
        record.exc_text = None
        try:
            return super(NoStacktraceFormatter, self).format(record)
        finally:
            record.exc_text = saved_exc_text


class ColorizedFormatter(logging.Formatter):
    """
    A custom log formatter class that:

    * Outputs the LOG_LEVEL with an appropriate color.
    * If a log call includes an `extras={"color_message": ...}` it will be used
      for formatting the output, instead of the plain text message.
    """

    level_name_colors = {
        TRACE_LOG_LEVEL: lambda level_name: click.style(str(level_name), fg="blue"),
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
    ):
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        def default(level_name: str) -> str:
            return str(level_name)  # pragma: no cover

        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def should_use_colors(self) -> bool:
        return True  # pragma: no cover

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)
        levelname = record_copy.levelname
        seperator = " " * (8 - len(record_copy.levelname))
        if self.use_colors:
            levelname = self.color_level_name(levelname, record_copy.levelno)
            if "color_message" in record_copy.__dict__:
                record_copy.msg = record_copy.__dict__["color_message"]
                record_copy.__dict__["message"] = record_copy.getMessage()
        record_copy.__dict__["levelprefix"] = levelname + ":" + seperator
        return super().formatMessage(record_copy)


class DefaultFormatter(ColorizedFormatter):
    def should_use_colors(self) -> bool:
        return sys.stderr.isatty()  # pragma: no cover


class AccessFormatter(ColorizedFormatter):
    status_code_colours = {
        1: lambda code: click.style(str(code), fg="bright_white"),
        2: lambda code: click.style(str(code), fg="green"),
        3: lambda code: click.style(str(code), fg="yellow"),
        4: lambda code: click.style(str(code), fg="red"),
        5: lambda code: click.style(str(code), fg="bright_red"),
    }

    def get_status_code(self, status_code: int) -> str:
        try:
            status_phrase = http.HTTPStatus(status_code).phrase
        except ValueError:
            status_phrase = ""
        status_and_phrase = f"{status_code} {status_phrase}"
        if self.use_colors:

            def default(code: int) -> str:
                return status_and_phrase  # pragma: no cover

            func = self.status_code_colours.get(status_code // 100, default)
            return func(status_and_phrase)
        return status_and_phrase

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)
        (
            client_addr,
            method,
            full_path,
            http_version,
            status_code,
        ) = record_copy.args  # type: ignore[misc]
        status_code = self.get_status_code(int(status_code))  # type: ignore[arg-type]
        request_line = f"{method} {full_path} HTTP/{http_version}"
        if self.use_colors:
            request_line = click.style(request_line, bold=True)
        record_copy.__dict__.update(
            {
                "client_addr": client_addr,
                "request_line": request_line,
                "status_code": status_code,
            }
        )
        return super().formatMessage(record_copy)
