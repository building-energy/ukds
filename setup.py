# -*- coding: utf-8 -*-


from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(  
    name='ukds', 
    version='0.0.1',  
    author='Steven K Firth',  # Optional
    author_email='s.k.firth@lboro.ac.uk',  # Optional
    description='A Python package for working with datasets from the UK Data Service (UKDS)',  # Required
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/building-energy/ukds',  # Optional
    packages=find_packages(), # Required
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    )
