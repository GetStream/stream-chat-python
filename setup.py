from setuptools import find_packages, setup

install_requires = [
    "requests>=2.22.0,<3",
    "aiodns>=2.0.0",
    "aiohttp>=3.6.0,<4",
    "aiofile>=3.1,<4",
    "pyjwt>=2.0.0,<3",
    "typing_extensions; python_version < '3.8'",
]
tests_require = ["pytest", "pytest-asyncio"]
ci_require = [
    "black",
    "flake8",
    "flake8-isort",
    "flake8-bugbear",
    "pytest-cov",
    "mypy",
    "types-requests",
]

with open("README.md", "r") as f:
    long_description = f.read()

about = {}

with open("stream_chat/__pkg__.py") as fp:
    exec(fp.read(), about)

setup(
    name="stream-chat",
    version=about["__version__"],
    author=about["__maintainer__"],
    author_email=about["__email__"],
    url="https://github.com/GetStream/stream-chat-python",
    project_urls={
        "Bug Tracker": "https://github.com/GetStream/stream-chat-python/issues",
        "Documentation": "https://getstream.io/activity-feeds/docs/python/?language=python",
        "Release Notes": "https://github.com/GetStream/stream-chat-python/releases/tag/v{}".format(
            about["__version__"]
        ),
    },
    description="Client for Stream Chat.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*tests*"]),
    zip_safe=False,
    install_requires=install_requires,
    extras_require={"test": tests_require, "ci": ci_require},
    include_package_data=True,
    python_requires=">=3.7",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
