#!/usr/bin/env python3
"""Setup configuration for habit_tracker package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="habit-tracker",
    version="0.1.0",
    author="Developer",
    description="A simple CLI habit tracker for daily habits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/habit-tracker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "habit-tracker=habit_tracker.main:main",
        ],
    },
)
