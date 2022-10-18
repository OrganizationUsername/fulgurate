from setuptools import setup, find_packages

setup(
    name="fulgurate",
    version="2.0.0",
    python_requires=">=2.7",
    url="https://github.com/theq629/fulgurate",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "fulgurate-run=fulgurate.cmd_line._run:main",
            "fulgurate-import=fulgurate.cmd_line._import:main",
            "fulgurate-show-schedule=fulgurate.cmd_line._show_schedule:main",
        ],
    },
    install_requires=[
        "python-dateutil ~= 2.8",
    ],
)
