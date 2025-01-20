"""
Setup configuration for HTML Clip Maker.
Handles package configuration, dependencies, and data files.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="html-clip-maker",
    version="1.0.0",
    description="Convert clipboard content with markdown and math notation to styled HTML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/html-clip-maker",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    package_data={
        'html-clip-maker': ['templates/*.html'],
    },
    entry_points={
        'console_scripts': [
            'html-clip-maker=html-clip-maker.main:main',
        ],
    },
    install_requires=[
        'beautifulsoup4>=4.9.3',
        'markdown>=3.3.4',
        'pygments>=2.9.0',  # for code highlighting
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.9',
            'mypy>=0.910',
            'isort>=5.9',
        ],
        'test': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: Markdown',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    python_requires='>=3.8',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/html-clip-maker/issues',
        'Source': 'https://github.com/yourusername/html-clip-maker',
        'Documentation': 'https://github.com/yourusername/html-clip-maker#readme',
    },
    keywords=[
        'markdown',
        'html',
        'mathematics',
        'latex',
        'mathjax',
        'documentation',
        'clipboard',
        'converter',
    ],
    license="MIT",
    platforms=['any'],
    zip_safe=False,  # due to included template files
)