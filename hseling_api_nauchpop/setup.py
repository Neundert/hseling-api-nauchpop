from setuptools import setup, find_packages

setup(
    name='',
    version='0.1',
    description='A description.',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    package_data={'': ['license.txt']},
    include_package_data=True,
    install_requires=[],
)