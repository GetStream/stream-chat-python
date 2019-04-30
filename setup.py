import sys

from stream_chat import __version__, __maintainer__, __email__, __license__
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


install_requires = [
    "pycryptodomex==3.4.7",
    "requests>=2.3.0,<3",
    "pyjwt==1.7.1",
    "six>=1.8.0",
]
long_description = open("README.md", "r").read()
tests_require = ["pytest==4.4.1", "pytest-cov", "codecov"]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(["stream_chat/", "-v", "--cov=stream_chat/", "--cov-report=html",  "--cov-report=annotate"])
        sys.exit(errno)


setup(
    name="stream-chat",
    cmdclass={"test": PyTest},
    version=__version__,
    author=__maintainer__,
    author_email=__email__,
    url="http://github.com/GetStream/chat-py",
    description="Client for Stream Chat.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=__license__,
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    extras_require={"test": tests_require},
    tests_require=tests_require,
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
