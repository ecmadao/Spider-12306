from setuptools import setup, find_packages

setup(
    name='spider_12306',
    version="beta 0.1",
    packages=find_packages(),
    author='ecmadao',
    author_email='wlec@outlook.com',
    url='https://github.com/ecmadao/Spider-12306',
    description='simple python application to get 12306 tickets',
    platforms='any',
    install_requires=[
        'prettytable',
        'Click'
    ],
    entry_points={
        'console_scripts': ['train=run:get_args']
    },
    license='MIT',
    py_modules=['run'],
    include_package_data=True
)
