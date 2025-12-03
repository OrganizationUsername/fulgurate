"""
Unbuffered IO.
"""

import os
import sys
import tty
import termios

_CLEAR = os.popen("clear").read()

class Unbuffered:
    """
    Context manager providing unbuffered IO.
    """

    def __init__(self, out_file):
        self._out_file_fd = None
        self._old_attr = None
        self._out_file = out_file

    def __enter__(self):
        try:
            self._out_file_fd = self._out_file.fileno()
            self._old_attr = termios.tcgetattr(self._out_file_fd)
            tty.setraw(self._out_file_fd)
        except termios.error:
            pass
        return self._out_file

    def __exit__(self, _type, _value, _traceback):
        try:
            termios.tcsetattr(self._out_file_fd, termios.TCSADRAIN, self._old_attr)
        except (termios.error, AttributeError):
            pass

def getch():
    """
    Read single character from terminal.
    """
    in_char = sys.stdin.read(1)
    if in_char == '\x03':
        raise KeyboardInterrupt()
    return in_char

def clear():
    """
    Clear terminal.
    """
    sys.stdout.write(_CLEAR)
