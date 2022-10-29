#!/usr/bin/env python3
from pathlib import Path
import setuptools

long_description = Path('README.md').read_text()

setuptools.setup(
    name='vnv',
    author='Gramkraxor',
    author_email='gram@krax.dev',
    url='https://codeberg.org/gramkraxor/vnv',
    description='The little shortcut for virtualenv',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['virtual', 'environments', 'isolated', 'virtualenv'],
    license='Unlicense',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: The Unlicense (Unlicense)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.7',
    scripts=setuptools.findall('bin'),
    entry_points={
        'console_scripts': [
            'vnv.cli = vnv:main',
        ],
    },
)
