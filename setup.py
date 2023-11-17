from setuptools import setup, find_packages

setup(
    name='pymaf',
    version='0.1.0',
    description='An internal Python utility package for MAF',
    author='Fibinse Xavier',
    author_email='fibinse.xavier@maf.ae',
    url='https://github.com/maf/pymaf',
    packages=find_packages(),
    py_modules=['pymaf'],
    python_requires='>=3.8',
    install_requires=[
        'pandas==1.5.3',
        'sqlalchemy-vertica-python==0.6.3',
        'vertica-python==1.3.2',
        'hvac==1.1.1',
        'diskcache'
    ],
    # classifiers=[
    #     'Development Status :: 3 - Alpha',
    #     'Intended Audience :: Developers',
    #     'Programming Language :: Python :: 3.8',
    #     'Programming Language :: Python :: 3.9',
    #     'Operating System :: OS Independent',
    # ],
)