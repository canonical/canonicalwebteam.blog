#! /usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="canonicalwebteam.blog",
    version="1.3.5",
    author="Canonical webteam",
    author_email="webteam@canonical.com",
    url="https://github.com/canonical-webteam/blog-extension",
    description=(
        "Flask extension and Django App to add a nice blog to your website"
    ),
    packages=find_packages(),
    long_description=open("README.md").read(),
    install_requires=["canonicalwebteam.http==1.0.1"],
    tests_require=["Flask>=1.0.2", "django>=2.0.11"],
    extra_require={"flask": ["Flask>=1.0.2"], "django": ["django>=2.0.11"]},
    test_suite="tests",
)
