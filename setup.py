from distutils.core import Command
from setuptools import setup, find_packages

class build_manpages_proxy(Command):
    description = 'Generate set of man pages from setup().'
    user_options = [('manpages=', 'O', 'list man pages specifications')]

    def __init__(self, dist):
        import build_manpages
        self._instance = build_manpages.build_manpages(dist)
        Command.__init__(self, dist)

    def initialize_options(self):
        self.manpages = None
        self._instance.initialize_options()

    def finalize_options(self):
        self._instance.manpages = self.manpages
        self._instance.finalize_options()

    def run(self):
        self._instance.run()

setup(
    cmdclass={
        'build_manpages': build_manpages_proxy,
    },
)
