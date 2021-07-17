from setuptools import setup
from mibandpreview_qt import app_info

setup(
    name='mibandpreview',
    version=app_info.VERSION,
    packages=['mibandpreview', 'mibandpreview_qt'],
    url='https://melianmiko.ru/en/mibandpreview',
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
