import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name='myp',
        version='0.1.2',
        author='Aaron English',
        author_email='manageyourproject@protonmail.com',
        license='GNU GPL-3',
        description='Manage Your Project! A Complete Commandline Project Manager',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/manageyourproject!/manageyourproject!',
        install_requires=[
            'colorama',
            'click',
            'networkx',
            'ruamel.yaml',
            'pandas',
        ],
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3.7',
            'License :: OSI Approved :: GNU GPL-3',
            'Operating System :: OS Independant',
        ],
        py_modules=['myp'],
        entry_points={
            'console_scripts': [
                'myp = myp.scripts.cli:cli'
            ]
        },
    )


