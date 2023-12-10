from setuptools import setup, find_packages

setup(
    name='file_renamer',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'rename-files = file_renamer.rename_files:main',
        ],
    },
)
