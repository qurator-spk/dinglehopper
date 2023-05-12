from io import open
from setuptools import find_namespace_packages, find_packages, setup

with open("requirements.txt") as fp:
    install_requires = fp.read()

with open("requirements-dev.txt") as fp:
    tests_require = fp.read()

setup(
    name="dinglehopper",
    author="Mike Gerber, The QURATOR SPK Team",
    author_email="mike.gerber@sbb.spk-berlin.de, qurator@sbb.spk-berlin.de",
    description="The OCR evaluation tool",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="qurator ocr",
    license="Apache",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requires,
    tests_require=tests_require,
    package_data={
        "": ["*.json", "templates/*"],
    },
    entry_points={
        "console_scripts": [
            "dinglehopper=dinglehopper.cli:main",
            "dinglehopper-line-dirs=dinglehopper.cli_line_dirs:main",
            "dinglehopper-extract=dinglehopper.cli_extract:main",
            "dinglehopper-summarize=dinglehopper.cli_summarize:main",
            "ocrd-dinglehopper=dinglehopper.ocrd_cli:ocrd_dinglehopper",
        ]
    },
)
