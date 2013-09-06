from setuptools import setup
# setuptools used instead of distutils.core so that 
# dependencies can be handled automatically

setup(
    name='resync-simulator',
    version='0.7',
    packages=['simulator'],
    package_data={'simulator': ['static/*','templates/*']},
    scripts=['resync-simulator'],
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "Operating System :: OS Independent", #is this true? know Linux & OS X ok
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2.7",
                 "Topic :: Internet :: WWW/HTTP",
                 "Environment :: Web Environment"],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author='Bernhard Haslhofer',
    author_email='bernhard.haslhofer@univie.ac.at',
    description='ResourceSync source simulator',
    long_description=open('README').read(),
    url='http://github.com/resync/simulator',
    install_requires=[
        "resync>=0.9.3",
        "tornado>=2.2.1"
    ],
    test_suite="simulator.test",
)
