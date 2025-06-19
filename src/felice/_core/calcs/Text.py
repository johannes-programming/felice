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

    def _calc_gitignore(self):
        return self.prog.draft.gitignore
