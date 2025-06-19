import os
import subprocess

from felice._core.calcs.Calc import Calc


class Git(Calc):
    def __call__(self, *args, force=False):
        for a in args:
            if type(a) is not str:
                raise TypeError(a)
        if not (force or self.is_repo()):
            return
        args = ["git"] + list(args)
        return subprocess.run(args)

    def _calc_author(self):
        a = self.prog.kwargs["author"]
        e = self.prog.kwargs["email"]
        if {a, e} == {None}:
            return None
        if a is None:
            return e
        if e is None:
            return a
        return f"{a} <{e}>"

    def init(self):
        if self.is_repo():
            return
        self("init", os.getcwd(), force=True)
        self.commit("Initial Commit")

    def commit_version(self):
        m = "Version %s" % self.prog.project.version
        self.commit(m)

    def commit(self, message):
        if message is None:
            message = "a"
        else:
            message = str(message)
        try:
            self("add", "-A").check_returncode()
        except:
            return
        args = ["commit", "--allow-empty", "-m", message]
        if self.author is not None:
            args += ["--author", self.author]
        self(*args)

    def push(self):
        pass  # self("push").returncode and self("push", "-u")

    def is_repo(self):
        called = self("rev-parse", force=True)
        if called is None:
            return False
        return not called.returncode

    def move(self, a, b, /):
        try:
            self("mv", a, b).check_returncode()
        except:
            pass
        else:
            return
        os.rename(a, b)
