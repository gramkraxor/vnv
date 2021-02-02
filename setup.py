from pathlib import Path
import setuptools

long_description = Path('README.md').read_text()

# https://packaging.python.org/guides/distributing-packages-using-setuptools/
setuptools.setup(
    name='vnv',
    version='1.1',
    author='Gramkraxor',
    author_email='gram@krax.dev',
    url='https://github.com/gramkraxor/vnv',
    description='The little shortcut for virtualenv',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['virtualenv', 'virtual environment', 'venv'],
    license='Unlicense',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: User Interfaces',
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
