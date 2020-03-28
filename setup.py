import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

requests = "requests>=2.22.0,<3"

install_requires = [
    "pycryptodomex>=3.8.1,<4",
    requests,
    "pyjwt==1.7.1",
    "six>=1.12.0",
]
long_description = open("README.md", "r").read()
tests_require = ["pytest"]

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
            import pytest_cov
            pytest_cmd += ["--cov=stream_chat/", "--cov-report=html",  "--cov-report=annotate"]
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
    extras_require={"test": tests_require},
    tests_require=tests_require,
    include_package_data=True,
    python_requires='>=3.5',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
