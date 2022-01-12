from setuptools import setup

version = "0.10"

setup(
    name='mibandpreview',
    version=version,
    packages=['mibandpreview'],
    url='https://github.com/melianmiko/mibandpreview',
    download_url="https://github.com/melianmiko/mibandpreview/archive/refs/tags/v" + version + ".tar.gz",
    license='Apache 2.0',
    install_requires=[
        "Pillow",
        "PyQt5"
    ],
    author='MelianMiko',
    author_email='melianmiko@gmail.com',
    description='Mi Band 4-6 watchface preview library',
    include_package_data=True
)
