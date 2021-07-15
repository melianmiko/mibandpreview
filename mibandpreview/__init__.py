from . import loader_miband4
from . import loader_miband5
from . import loader_miband6
from .generator import MiBandPreview


def open_dir(directory):
    return MiBandPreview(target=directory)
