from setuptools import setup
# setuptools used instead of distutils.core so that 
# dependencies can be handled automatically

setup(
    name='simulator',
    version='0.7',
    packages=['simulator'], #FIXME - change to resync-simulator
    scripts=['simulate-source'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author='Bernhard Haslhofer',
    author_email='bernhard.haslhofer@univie.ac.at',
    long_description=open('README.md').read(),
    install_requires=[
        "resync>=0.9.3",
        "tornado"
    ],
    test_suite="simulator.test",
)
