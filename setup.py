from setuptools import setup
# setuptools used instead of distutils.core so that 
# dependencies can be handled automatically

# Extract version number from resync/_version.py. Here we
# are very strict about the format of the version string
# as an extra sanity check. (Thanks for comments in
# http://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package )
import re
VERSIONFILE="simulator/_version.py"
verfilestr = open(VERSIONFILE, "rt").read()
match = re.search(r"^__version__ = '(\d\.\d.\d+(\.\d+)?)'", verfilestr, re.MULTILINE)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))

setup(
    name='resync-simulator',
    version=version,
    packages=['simulator'],
    package_data={'simulator': ['static/*','templates/*']},
    scripts=['resync-simulator'],
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "Operating System :: OS Independent", #is this true? know Linux & OS X ok
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 3.5",
                 "Programming Language :: Python :: 3.6",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: 3.8",
                 "Topic :: Internet :: WWW/HTTP",
                 "Environment :: Web Environment"],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author='Bernhard Haslhofer',
    author_email='bernhard.haslhofer@univie.ac.at',
    description='ResourceSync source simulator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/resync/resync-simulator',
    install_requires=[
        "resync>=2.0",
        "tornado>=6.0",
        "pyyaml>=5.3"
    ],
    test_suite="tests",
)
