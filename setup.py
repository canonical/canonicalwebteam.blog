#! /usr/bin/env python3


from setuptools import setup, find_packages

setup(
    name="canonicalwebteam.blog",
    version="6.1.1",
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
    tests_require=["flask-reggie", "vcrpy", "vcrpy-unittest"],
)
