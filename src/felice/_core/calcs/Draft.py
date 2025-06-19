import importlib.resources

from felice._core.calcs.Calc import Calc


class Draft(Calc):
    def _calc(self, name):
        return importlib.resources.read_text("felice.drafts", "%s.txt" % name)
