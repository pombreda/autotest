from setuptools import setup
from setuptools.command.install import install


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
    description = "Autotest tool - Minimalistic Continuous Integration",
    license = "Modified BSD",
    long_description = """
Minimalistic Continuous Integration for git

On failure it sends a notification to all users who have contributed to the
branch since the last sucessful test.
""",
    keywords = "adfinis-sygroup continuous integration",
    url = "https://github.com/adfinis-sygroup/autotest",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Testing",
    ]
)
