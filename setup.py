from setuptools import setup
from setuptools import find_packages
from setuptools.command.install import install
import os
import shutil
import glob


class CustomInstallCommand(install):
    def run(self):
        pass

setup(
    name = "adsy-autotest",
    version = "0.1.0",
    package_dir = {'' : 'src'},
    py_modules = ['adsy_autotest'],
    entry_points = {
        'console_scripts': [
            'autotest = adsy_autotest:main',
        ]
    },

    install_requires = [
        'argparse'
    ],

    cmdclass = {
        'install': CustomInstallCommand,
    },

    author = "Adfinis-Sygroup AG",
    author_email = "http://adfinis-sygroup.ch/contact",
    description = "Adfinis-Sygroup Minimalistic Continuous Integration",
    license = "Modified BSD",
    long_description = """
Adfinis-Sygroup Minimalistic Continuous Integration with automatic notification
by reading the git-log and only informing authors of changes that failed.""",
    keywords = "adfinis-sygroup continuous integration",
    url = "http://adfinis-sygroup.ch",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Testing",
    ]
)
