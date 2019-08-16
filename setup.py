from io import open
from setuptools import find_packages, setup

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='dinglehopper',
    author_email='qurator@sbb.spk-berlin.de',
    description='The OCR evaluation tool',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    keywords='qurator ocr',
    license='Apache',
    namespace_packages=['qurator'],
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    install_requires=install_requires,
    package_data={
        '': ['*.json', '*.yml', '*.yaml'],
    },
    entry_points={
      'console_scripts': [
        'dinglehopper=qurator.dinglehopper.cli:main',
        'ocrd-dinglehopper=qurator.dinglehopper.ocrd_cli:ocrd_dinglehopper',
      ]
    }
)
