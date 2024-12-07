import io
from os import path
from setuptools import setup, find_packages

pwd = path.abspath(path.dirname(__file__))
with io.open(path.join(pwd, 'README.md'), encoding='utf-8') as readme:
    desc = readme.read()

setup(
    name='uro',
    version=__import__('uro').__version__,
    description='A python tool to declutter url lists for crawling/pentesting',
    long_description=desc,
    long_description_content_type='text/markdown',
    author='s0md3v',
    license='Apache-2.0 License',
    url='https://github.com/s0md3v/uro',
    download_url='https://github.com/s0md3v/uro/archive/v%s.zip' % __import__(
        'uro').__version__,
    packages=find_packages(),
    classifiers=[
        'Topic :: Security',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'uro = uro.uro:main'
        ]
    },
    keywords=['declutter', 'crawling', 'pentesting']
)
