from setuptools import setup

setup(
    name='trivia',
    version='0.1.0',
    url='https://github.com/namoscato/live-trivia',
    packages=['trivia'],
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-Migrate',
        'Flask-SQLAlchemy',
        'psycopg2-binary',
    ],
)
