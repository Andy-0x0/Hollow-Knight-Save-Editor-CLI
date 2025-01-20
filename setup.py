from setuptools import setup, find_packages

setup(
    name='hollow',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pycryptodome',
    ],
    entry_points={
        'console_scripts': [
            'hollow = hollow.cli:main'
        ]
    },
    author="Tianyi Ma",
    author_email="tym.andy777@gmail.com",
    license="GPL-3.0",
    description="Hollow Knight Save Modifier CLI",
    python_requires='>=3.7',
)
