"""
Setup script for pycas package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="pycas",
    version="0.1.1",
    author="Aykut Kılıç",
    author_email="battalaykut@gmail.com",
    description="Pure Python library for reading and converting Atari 8-bit cassette (CAS) files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aykutkilic/pycas",
    project_urls={
        "Bug Tracker": "https://github.com/aykutkilic/pycas/issues",
        "Documentation": "https://github.com/aykutkilic/pycas#readme",
        "Source Code": "https://github.com/aykutkilic/pycas",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    py_modules=["cas_reader"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Emulators",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # No external dependencies
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "pycas=cas_reader:main",
        ],
    },
    keywords="atari cas cassette tape retro emulation converter",
    include_package_data=True,
    zip_safe=False,
)
