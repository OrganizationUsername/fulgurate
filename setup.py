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
            "fulgurate-run=fulgurate._cmd_line.run:main",
            "fulgurate-import-cards=fulgurate._cmd_line.import_cards:main",
            "fulgurate-show-schedule=fulgurate._cmd_line.show_schedule:main",
        ],
    },
    install_requires=[
        "python-dateutil ~= 2.8",
    ],
)
