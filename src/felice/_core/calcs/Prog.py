import datetime
import os
import shutil
import string
import subprocess
import sys

import tomlhold
import v440

from felice._core import utils
from felice._core.calcs.Calc import Calc
from felice._core.calcs.Draft import Draft
from felice._core.calcs.File import File
from felice._core.calcs.Git import Git
from felice._core.calcs.Text import Text


class Prog(Calc):
    _CORE = "kwargs"
    INPUTS = {
        "author": "The author of the project.",
        "classifiers": "The classifiers of the project. Comma separated. You may include {mit} or {preset}. Recommended value is '{preset}, {mit}, Programming Language :: Python, Programming Language :: Python :: 3, Programming Language :: Python :: 3 :: Only'.",
        "description": "The description of the project.",
        "development_status": "The projects development status. Communicated as a classifier. May be 'infer'.",
        "email": "Email of the author.",
        "requires_python": "The python version of the project. A list separated by '\\|'. The first non empty item is used. You may use {preset} and {current}. Recommended value is '{preset} \\| {current}'.",
        "github": "The github username for linking the source.",
        "token": "The PyPI token.",
        "v": "Version string for the project. Recommended is 'bump(2, 1)'.",
        "vformat": "Format of the version string, i.e. how many numerals in the release string. Recommended is '3'.",
        "year": "Year of creating the project. Recommended is '{current}'.",
    }

    def __post_init__(self):
        self.git.init()
        if self.git.is_repo():
            self.save("gitignore")
        for p in self.packages:
            self.tests(p)
        self.pp["project"] = self.project.todict()
        self.pp["build-system"] = self.build_system
        self.pp.data = self.easy_dict(self.pp.data)
        self.text.pp = self.pp.dumps()
        self.save("license")
        self.save("manifest")
        self.save("pp")
        self.save("readme")
        self.save("setup")
        utils.run_isort()
        utils.run_black(os.getcwd())
        utils.run_html_prettifier(os.getcwd())
        self.git.commit_version()
        self.git.push()
        self.pypi()

    def _calc_author(self):
        f = lambda z: str(z).strip()
        n = f(self.kwargs["author"])
        e = f(self.kwargs["email"])
        x = n, e
        authors = self.project.authors
        if type(authors) is not list:
            return x
        for a in authors:
            if type(a) is not dict:
                continue
            n = f(a.get("name", ""))
            e = f(a.get("email", ""))
            y = n, e
            if y != ("", ""):
                return y
        return x

    def _calc_draft(self):
        return Draft(self)

    def _calc_file(self):
        return File(self)

    def _calc_git(self):
        return Git(self)

    def _calc_github(self):
        u = self.kwargs["github"]
        if u == "":
            return ""
        return f"https://github.com/{u}/{self.project.name}/"

    def _calc_packages(self):
        self.mkdir("src")
        ans = []
        for x in os.listdir("src"):
            y = os.path.join("src", x)
            if self.ispkg(y):
                ans.append(y)
        if len(ans):
            return self.easy_list(ans)
        for x in os.listdir():
            if self.ispkg(x, todir=False):
                ans.append(x)
        if len(ans):
            return self.easy_list(ans)
        if self.file.exists("pp"):
            return list()
        pro = os.path.join("src", self.project.name)
        if not self.ispkg(pro):
            self.save("core")
            self.save("init")
            self.save("main")
        return [pro]

    def _calc_pp(self):
        return tomlhold.Holder.loads(self.text.pp)

    def _calc_text(self):
        return Text(self)

    def _calc_version_default(self):
        return "0.0.0.dev0"

    def _calc_version_formatted(self):
        ans = self.version_unformatted
        kwarg = self.kwargs["vformat"]
        try:
            ans = v440.Version(ans)
            ans = ans.format(kwarg)
        except v440.VersionError:
            pass
        return str(ans)

    def _calc_version_unformatted(self):
        a = self.kwargs["v"]
        b = self.project.get("version")
        if a == "":
            if b is None:
                return self.version_default
            else:
                return b
        try:
            args = self.parse_bump(a)
        except ValueError:
            return a
        if b is None:
            return self.version_default
        try:
            c = v440.Version(b)
            c.release.bump(*args)
        except v440.VersionError as e:
            print(e, file=sys.stderr)
            return b
        return str(c)

    def _calc_year(self):
        ans = self.kwargs["year"]
        current = str(datetime.datetime.now().year)
        ans = ans.format(current=current)
        return ans

    @staticmethod
    def easy_dict(dictionary, *, purge=False):
        d = dict(dictionary)
        keys = sorted(list(d.keys()))
        ans = {k: d[k] for k in keys}
        return ans

    @staticmethod
    def easy_list(iterable):
        ans = list(set(iterable))
        ans.sort()
        return ans

    def ispkg(self, path, *, todir=True):
        root, name = os.path.split(path)
        tr, ext = os.path.splitext(name)
        if os.path.isdir(path):
            init = os.path.join(path, "__init__.py")
            if not os.path.exists(init):
                return False
            if not os.path.isfile(init):
                raise FileExistsError
            if ext != "":
                raise Exception(ext)
            return True
        if os.path.isfile(path):
            if ext != ".py":
                return False
            if not todir:
                return True
            pro = os.path.join(root, tr)
            init = os.path.join(pro, "__init__.py")
            if os.path.exists(init):
                raise FileExistsError
            self.mkdir(pro)
            self.git.move(path, init)
            return True
        return False

    @classmethod
    def mkdir(cls, path):
        if utils.isdir(path):
            return
        os.mkdir(path)

    def mkpkg(self, path):
        if self.ispkg(path):
            return
        self.mkdir(path)
        f = os.path.join(path, "__init__.py")
        self.touch(f)

    @staticmethod
    def parse_bump(line):
        line = line.strip()
        if not line.startswith("bump"):
            raise ValueError
        line = line[4:].lstrip()
        if not line.startswith("("):
            raise ValueError
        line = line[1:].lstrip()
        if not line.endswith(")"):
            raise ValueError
        line = line[:-1].rstrip()
        if line.endswith(","):
            line = line[:-1].rstrip()
        chars = string.digits + string.whitespace + ",-"
        if line.strip(chars):
            raise ValueError
        line = line.split(",")
        line = [int(x.strip()) for x in line]
        return line

    @staticmethod
    def py(*args):
        args = [sys.executable, "-m"] + list(args)
        return subprocess.run(args)

    def save(self, n, /):
        file = getattr(self.file, n)
        text = getattr(self.text, n)
        roots = list()
        root = file
        while True:
            root = os.path.dirname(root)
            if not root:
                break
            if os.path.exists(root):
                break
            roots.append(root)
        while roots:
            root = roots.pop()
            os.mkdir(root)
        with open(file, "w") as s:
            s.write(text)

    def tests(self, pkg):
        a = os.path.join(pkg)
        b = os.path.join(pkg, "tests")
        self.mkpkg(a)
        if self.ispkg(b):
            return
        self.mkdir(b)
        f = os.path.join(b, "__init__.py")
        if not utils.isfile(f):
            text = self.draft.tests
            base = os.path.basename(pkg)
            text = text.format(pkg=base)
            with open(f, "w") as s:
                s.write(text)
        for f in os.listdir(b):
            if f == "__init__.py":
                continue
            if f.startswith("."):
                continue
            return
        f = os.path.join(b, "test_1984.py")
        with open(f, "w") as s:
            s.write(self.draft.test_1984)

    @staticmethod
    def touch(file):
        if utils.isfile(file):
            return
        with open(file, "w"):
            pass
