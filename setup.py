from setuptools import setup, find_packages

setup(
    name='arcgis_pro_publish',
    author='roemhildtg',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests'
    ]
)