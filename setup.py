#! /usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="canonicalwebteam.blog",
    version="0.1.4",
    author="Canonical webteam",
    author_email="webteam@canonical.com",
    url="https://github.com/canonical-webteam/blog-flask-extension",
    description=(
        "Flask extension to add a nice blog to your website"
    ),
    packages=find_packages(),
    long_description=open("README.md").read(),
    install_requires=[
        "canonicalwebteam.http==1.0.1",
        "Flask==1.0.2",
    ],
)
