from felice._core.calcs.Calc import Calc


class Text(Calc):
    def _calc(self, name):
        f = getattr(self.prog.file, name)
        try:
            with open(f, "r") as s:
                lines = s.readlines()
        except FileNotFoundError:
            lines = None
        if lines is not None:
            lines = [x.rstrip() for x in lines]
            lines = "\n".join(lines)
            return lines
        try:
            f = getattr(self, "_calc_" + name)
        except:
            return ""
        return f()

    def _calc_core(self):
        n = self.prog.project.name
        return self.prog.draft.core.format(project=n)

    def _calc_gitignore(self):
        return self.prog.draft.gitignore

    def _calc_init(self):
        n = self.prog.project.name
        return self.prog.draft.init.format(project=n)

    def _calc_license(self):
        d = dict()
        d["year"] = self.prog.year
        d["author"] = self.prog.author[0]
        ans = self.prog.draft.license.format(**d)
        return ans

    def _calc_main(self):
        n = self.prog.project.name
        return self.prog.draft.main.format(project=n)

    def _calc_readme(self):
        return self.prog.block.text
