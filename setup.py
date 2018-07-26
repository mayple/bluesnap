# Always prefer setuptools over distutils
# To use a consistent encoding
from setuptools import setup, find_packages
from os import path

from codecs import open

here = path.abspath(path.dirname(__file__))
__version__ = None
with open('bluesnap/version.py') as f:
    exec(f.read())
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.readlines()

setup(
    name='bluesnap',
    version=__version__,
    author='Alon Diamant',
    author_email='alon@selectom.com',
    url='https://github.com/selectom/bluesnap',
    license='LICENSE',
    description='A Python 3 module to interact with the Bluesnap API.',
    long_description=long_description,
    packages=find_packages(),
    install_requires=requires,
    setup_requires=requires,
    test_suite='nose.collector',
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers = [  # Optional
                  'Development Status :: 3 - Alpha',
                  'Intended Audience :: Developers',
                  'License :: OSI Approved :: MIT License',
                  'Programming Language :: Python :: 3',
                  'Programming Language :: Python :: 3.4',
                  'Programming Language :: Python :: 3.5',
                  'Programming Language :: Python :: 3.6',
                  'Programming Language :: Python :: 3.7',
              ],

)
