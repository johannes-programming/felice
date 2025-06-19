import os

from felice._core import utils
from felice._core.calcs.Calc import Calc


class File(Calc):
    def _calc_core(self):
        n = self.prog.project.name
        return os.path.join("src", n, "core", "__init__.py")

    def _calc_gitignore(self):
        return ".gitignore"

    def _calc_license(self):
        ans = self.prog.pp.get("project", "license", "file")
        if type(ans) is str:
            return ans
        return self._find("LICENSE.txt")

    def _calc_main(self):
        n = self.prog.project.name
        return os.path.join("src", n, "__main__.py")

    def _calc_init(self):
        n = self.prog.project.name
        return os.path.join("src", n, "__init__.py")

    def _calc_manifest(self):
        return "MANIFEST.in"

    def _calc_pp(self):
        return "pyproject.toml"

    def _calc_readme(self):
        ans = self.prog.pp.get("project", "readme")
        if type(ans) is str and os.path.exists(ans):
            return ans
        return self._find("README.rst")

    def _calc_setup(self):
        return "setup.cfg"

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
