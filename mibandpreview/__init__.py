"""This class is a preview generator for Mi Band 4-6 watch face"""
from .generator import MiBandPreview


def open_dir(directory):
    """
    Open project directory

    :param directory: directory path
    :return: new MiBandPreview object
    """
    return MiBandPreview(target=directory)
