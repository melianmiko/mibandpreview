from setuptools import setup

setup(
    name='mibandpreview',
    version='0.7.4',
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
