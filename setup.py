from setuptools import find_packages, setup

setup(
    name='tempo',
    packages=find_packages(include=['tempo']),
    version='1.0.0',
    description='A python library to interact with the TEMPO online database',
    author='Mark Vereș',
    author_email='mark@markveres.ro',
    install_requires=['requests_cache'],
)