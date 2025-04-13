from setuptools import setup, find_packages

setup(
    name="SentinelPC",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies from requirements.txt here
    ],
    entry_points={
        'console_scripts': [
            'sentinelpc=src.main:main',
        ],
    },
)