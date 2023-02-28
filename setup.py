from io import open
from setuptools import find_packages, setup

with open("requirements.txt") as fp:
    install_requires = fp.read()

with open('requirements-dev.txt') as fp:
    tests_require = fp.read()

with open('ocrd-tool.json', 'r', encoding='utf-8') as f:
    version = load(f)['version']

setup(
    name="dinglehopper",
    version=version,
    author="Mike Gerber, The QURATOR SPK Team",
    author_email="mike.gerber@sbb.spk-berlin.de, qurator@sbb.spk-berlin.de",
    description="The OCR evaluation tool",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="qurator ocr",
    license="Apache",
    namespace_packages=["qurator"],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requires,
    tests_require=tests_require,
    package_data={
        "": ["*.json", "templates/*"],
    },
    entry_points={
        "console_scripts": [
            "dinglehopper=qurator.dinglehopper.cli:main",
            "dinglehopper-line-dirs=qurator.dinglehopper.cli_line_dirs:main",
            "dinglehopper-extract=qurator.dinglehopper.cli_extract:main",
            "ocrd-dinglehopper=qurator.dinglehopper.ocrd_cli:ocrd_dinglehopper",
        ]
    },
)
