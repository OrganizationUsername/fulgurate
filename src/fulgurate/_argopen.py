"""
Utility for opening files, handling both the '-' as stdin/out convention and
optional atomic writing.
"""

# pylint: disable=redefined-builtin,invalid-name

import sys
import __builtin__
import tempfile
import shutil
import os
import os.path

class open(object):
    """
    Open file with handling of stdin/out convention.
    """

    def __init__(self, filename, mode='r', atomic=False):
        self.filename = filename
        self.mode = mode
        self.atomic = atomic
        self.using_std = False
        self.using_temp = False
        self.file = None

    def __enter__(self):
        writing = 'w' in self.mode
        if self.filename == '-':
            if writing:
                self.file = sys.stdout
            else:
                self.file = sys.stdin
            self.using_std = True
        else:
            if self.atomic and writing:
                self.file = tempfile.NamedTemporaryFile(
                    prefix=os.path.basename(self.filename),
                    delete=False,
                )
                self.using_temp = True
            else:
                self.file = __builtin__.open(self.filename, self.mode)
        return self.file

    def __exit__(self, _type, _value, _traceback):
        self.close()

    def close(self):
        """
        Close the file.
        """
        if self.file is not None:
            if not self.using_std:
                self.file.close()
            if self.using_temp:
                shutil.move(self.file.name, self.filename)

    def write(self, string):
        """
        Write to the file.
        """
        if self.file is None:
            self.__enter__()
        self.file.write(string)
