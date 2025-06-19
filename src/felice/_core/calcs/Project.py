import inspect
import os
import string
import sys

from felice._core import utils
from felice._core.calcs.Calc import Calc


class Project(Calc):
    def __post_init__(self): ...

    def _calc_authors(self):
        ans = self.get("authors", default=[])
        if type(ans) is not list:
            return ans
        ans = list(ans)
        author = dict()
        a = dict()
        a["name"] = self.prog.kwargs["author"]
        a["email"] = self.prog.kwargs["email"]
        for k, v in a.items():
            if v:
                author[k] = v
        author = self.prog.easy_dict(author)
        used = False
        for i in range(len(ans)):
            try:
                ans[i] = dict(ans[i])
            except:
                continue
            fit = utils.dict_match(ans[i], author)
            if fit and not used:
                ans[i].update(author)
            ans[i] = self.prog.easy_dict(ans[i])
            used |= fit
        if not used:
            ans.insert(0, author)
        return ans

    def _calc_classifiers(self):
        preset = self.get("classifiers", default=[])
        if type(preset) is not list:
            return preset
        if utils.isfile(self.prog.file.license):
            mit = ""
        else:
            mit = "License :: OSI Approved :: MIT License"
        kwarg = self.prog.kwargs["classifiers"]
        if kwarg == "":
            preset = utils.easy_list(preset)
            return preset
        ans = kwarg
        preset = ", ".join(preset)
        ans = ans.format(preset=preset, mit=mit)
        ans = ans.split(",")
        ans = self.format_classifiers(ans)
        if self.prog.development_status == "":
            ans = self.prog.easy_list(ans)
            return ans
        prefix = "Development Status :: "
        cleaned = list()
        for x in ans:
            if x.lower().startswith(prefix.lower()):
                continue
            cleaned.append(x)
        ans = cleaned
        status = prefix + self.prog.development_status
        ans.append(status)
        ans = self.format_classifiers(ans)
        ans = self.prog.easy_list(ans)
        return ans

    def _calc_dependencies(self):
        ans = self.get("dependencies", default=[])
        if type(ans) is not list:
            return ans
        ans = [utils.fix_dependency(x) for x in ans]
        ans = self.prog.easy_list(ans)
        return ans

    def _calc_description(self):
        if self.prog.kwargs["description"]:
            return self.prog.kwargs["description"]
        if self.get("description") is not None:
            return self.get("description")
        return self.name

    def _calc_keywords(self):
        return self.get("keywords", default=[])

    def _calc_license(self):
        ans = self.get("license")
        if ans is None:
            ans = dict()
        if type(ans) is not dict:
            return ans
        if "file" not in ans.keys():
            ans["file"] = self.prog.file.license
        return ans

    def _calc_name(self):
        basename = os.path.basename(os.getcwd())
        raw = self.get("name") or basename
        raw = str(raw)
        ans = ""
        for x in raw:
            if x in (string.ascii_letters + string.digits):
                ans += x
            else:
                ans += "_"
        return ans

    def _calc_readme(self):
        return self.prog.file.readme

    def _calc_requires_python(self):
        kwarg = self.prog.kwargs["requires_python"]
        preset = self.get("requires-python", default="")
        current = ">={0}.{1}.{2}".format(*sys.version_info)
        if kwarg == "":
            return preset
        kwarg = kwarg.format(preset=preset, current=current)
        kwarg = kwarg.split("\\|")
        kwarg = [x.strip() for x in kwarg]
        for x in kwarg:
            if x:
                return x
        return None

    def _calc_urls(self):
        ans = self.get("urls")
        if ans is None:
            ans = dict()
        if type(ans) is not dict:
            return ans
        if self.prog.github:
            ans.setdefault("Source", self.prog.github)
        p = f"https://pypi.org/project/{self.name}/"
        ans.setdefault("Index", p)
        p = f"https://pypi.org/project/{self.name}/#files"
        ans.setdefault("Download", p)
        ans = self.prog.easy_dict(ans)
        return ans

    def _calc_version(self):
        return self.prog.version_formatted

    @classmethod
    def format_classifiers(cls, ans, /):
        ans = [x.replace("::", " :: ") for x in ans]
        ans = [" ".join(x.split()) for x in ans]
        ans = [x.strip() for x in ans]
        ans = [x for x in ans if x]
        return ans

    def get(self, *args, default=None):
        return self.prog.pp.get("project", *args, default=default)

    def todict(self) -> None:
        ans = self.get(default={})
        prefix = "_calc_"
        for n, m in inspect.getmembers(self):
            if not n.startswith(prefix):
                continue
            k = n[len(prefix) :]
            v = getattr(self, k)
            if v is None:
                continue
            k = k.replace("_", "-")
            ans[k] = v
        ans = self.prog.easy_dict(ans)
        return ans
