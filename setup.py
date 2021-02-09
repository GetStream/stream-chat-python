import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

install_requires = [
    "pycryptodomex>=3.8.1,<4",
    "requests>=2.22.0,<3",
    "chardet>=2.0.0,<4",
    "aiodns>=2.0.0",
    "aiohttp>=3.6.0,<4",
    "aiofile>=3.1,<4",
    "pyjwt>=2.0.0,<3",
]
long_description = open("README.md", "r").read()
tests_require = ["pytest", "pytest-asyncio"]
ci_require = ["black", "flake8", "pytest-cov"]

about = {}
with open("stream_chat/__pkg__.py") as fp:
    exec(fp.read(), about)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        pytest_cmd = ["stream_chat/", "-v"]

        try:
            pytest_cmd += [
                "--cov=stream_chat/",
                "--cov-report=xml",
            ]
        except ImportError:
            pass

        errno = pytest.main(pytest_cmd)
        sys.exit(errno)


setup(
    name="stream-chat",
    cmdclass={"test": PyTest},
    version=about["__version__"],
    author=about["__maintainer__"],
    author_email=about["__email__"],
    url="http://github.com/GetStream/chat-py",
    description="Client for Stream Chat.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    extras_require={"test": tests_require, "ci": ci_require},
    tests_require=tests_require,
    include_package_data=True,
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
