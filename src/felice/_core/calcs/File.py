import os

from felice._core import utils
from felice._core.calcs.Calc import Calc


class File(Calc):

    def _calc_gitignore(self):
        return ".gitignore"

    def exists(self, name):
        f = getattr(self, name)
        return os.path.exists(f)

    @staticmethod
    def _find(file):
        if utils.isfile(file):
            return file
        t = os.path.splitext(file)[0]
        l = os.listdir()
        l = list(l)
        l.sort(reverse=True)
        for x in l:
            if t == os.path.splitext(x)[0]:
                return x
        return file
