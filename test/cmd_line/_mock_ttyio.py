import sys
import contextlib
import io
from mock import patch
import fulgurate._cmd_line._ttyio

@contextlib.contextmanager
def Unbuffered(out_file):
    yield out_file

class _MockedTtyio:
    def __init__(self, input_keys, clear_output):
        self._input_keys = iter(input_keys)
        self._clear_output = clear_output

    def _getch(self):
        return next(self._input_keys)

    def _clear(self):
        print self._clear_output

@contextlib.contextmanager
def mock_ttyio(input_keys, clear_output=""):
    mock = _MockedTtyio(input_keys, clear_output)
    with patch.object(fulgurate._cmd_line._ttyio, 'getch', mock._getch), \
         patch.object(fulgurate._cmd_line._ttyio, 'clear', mock._clear), \
         patch.object(fulgurate._cmd_line._ttyio, 'Unbuffered', Unbuffered):
        yield None
