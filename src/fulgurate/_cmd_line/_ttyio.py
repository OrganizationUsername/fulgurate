"""
Unbuffered IO.
"""

from typing import Any, Optional, IO
import os
import sys
import tty
import termios

_CLEAR = os.popen("clear").read()

class Unbuffered:
    """
    Context manager providing unbuffered IO.
    """

    def __init__(self, out_file: IO[Any]) -> None:
        self._out_file_fd: Optional[int] = None
        self._old_attr: Optional[list[int]] = None
        self._out_file = out_file

    def __enter__(self) -> IO[bytes]:
        try:
            self._out_file_fd = self._out_file.fileno()
            self._old_attr = termios.tcgetattr(self._out_file_fd)
            tty.setraw(self._out_file_fd)
        except termios.error:
            pass
        return self._out_file

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        try:
            if self._out_file_fd is not None and self._old_attr is not None:
                termios.tcsetattr(
                    self._out_file_fd,
                    termios.TCSADRAIN,
                    self._old_attr, # type: ignore
                )
        except (termios.error, AttributeError):
            pass

def getch() -> str:
    """
    Read single character from terminal.
    """
    in_char = sys.stdin.read(1)
    if in_char == '\x03':
        raise KeyboardInterrupt()
    return in_char

def clear() -> None:
    """
    Clear terminal.
    """
    sys.stdout.write(_CLEAR)
