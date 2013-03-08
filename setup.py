from setuptools import setup, find_packages


VERSION = __import__("sherlock").__version__

CLASSIFIERS = [
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
]

install_requires = [
    'Django>=1.4.0',
    'redis'
]

setup(
    name="django-sherlock",
    description="A pluggable app for notifications",
    version=VERSION,
    author="Nam Ngo",
    author_email="nam@namis.me",
    url="https://github.com/geeknam/django-sherlock",
    packages=find_packages(exclude=["tests"]),
    install_requires=install_requires,
    classifiers=CLASSIFIERS,
)
