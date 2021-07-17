from setuptools import setup
from mibandpreview_qt.app_info import VERSION, APP_VERSION

setup(
    name='mibandpreview',
    version=VERSION + ".1.2",
    packages=['mibandpreview', 'mibandpreview_qt'],
    url='https://github.com/melianmiko/mibandpreview',
    download_url="https://github.com/melianmiko/mibandpreview/archive/refs/tags/" + APP_VERSION + ".tar.gz",
    license='Apache 2.0',
    install_requires=[
        "Pillow"
    ],
    extras_require={
        "qt": ["PyQt5"]
    },
    author='MelianMiko',
    author_email='melianmiko@gmail.com',
    description='Mi Band Preview',
    include_package_data=True
)
