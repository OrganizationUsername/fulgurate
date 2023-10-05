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
    name="fulgurate",
    version="2.0.0",
    python_requires=">=2.7",
    url="https://github.com/theq629/fulgurate",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "fulgurate-run=fulgurate._cmd_line.run:main",
            "fulgurate-import-cards=fulgurate._cmd_line.import_cards:main",
            "fulgurate-show-schedule=fulgurate._cmd_line.show_schedule:main",
        ],
    },
    install_requires=[
        "python-dateutil ~= 2.8",
        "contextlib2 ~= 0.6",
        "tabulate ~= 0.8",
    ],
    cmdclass={
        'build_manpages': build_manpages_proxy,
    },
)
