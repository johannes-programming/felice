class Calc:
    _CORE = "prog"

    def __delattr__(self, name):
        self.__check(name)
        object.__delattr__(self, name)

    def __getattr__(self, name):
        name = str(name)
        if name.startswith("_"):
            raise AttributeError(name)
        if not hasattr(self, "_lock"):
            self._lock = set()
        if name in self._lock:
            raise Exception
        self._lock.add(name)
        try:
            ans = self._calc(name)
            object.__setattr__(self, name, ans)
        finally:
            self._lock.remove(name)
        return ans

    def __init__(self, core, /) -> None:
        object.__setattr__(self, type(self)._CORE, core)
        getattr(self, "__post_init__", int)()

    def __setattr__(self, name, value):
        self.__check(name)
        object.__setattr__(self, name, value)

    def __check(self, name):
        if name.startswith("_"):
            return
        if not hasattr(super(), name):
            return
        raise AttributeError("readonly")

    def _calc(self, name):
        return getattr(self, f"_calc_{name}")()
