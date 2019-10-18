import os
from setuptools import find_packages, setup


with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    long_description = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='lite-forms',
    version='0.21',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Forms builder used for LITE',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/uktrade/lite-forms',
    author='Jan Faracik',
    author_email='',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
