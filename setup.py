#! /usr/bin/env python3


from setuptools import find_packages, setup

setup(
    name="canonicalwebteam.blog",
    version="6.6.0",
    description=("Flask extension to add a nice blog to your website"),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Canonical webteam",
    author_email="webteam@canonical.com",
    packages=find_packages(),
    install_requires=[
        "flask",
        "feedgen",
        "requests",
        "beautifulsoup4",
        "canonicalwebteam.image-template",
    ],
)
