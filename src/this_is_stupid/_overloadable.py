from __future__ import annotations

from typing import get_type_hints
from collections import defaultdict
from typing import Generic, TypeVar

T = TypeVar("T")

class OverloadNotFound(Exception):
    pass


class Overloadable(type):
    overload_map = defaultdict(lambda: defaultdict(list))

    @classmethod
    def overload(cls, func):
        classname = func.__qualname__.split(".")[0]
        funcname = func.__qualname__.split(".")[1]
        type_hints = get_type_hints(func)
        typ = next(iter(type_hints.values()))
        map_key = f"{func.__module__}_{classname}"
        cls.overload_map[map_key][funcname].append((typ, func))
        return func

    @staticmethod
    def dynamic_dispatch(func, slow_overloads=None):
        def __inner_fast(slf, arg, typ):
            typ_name = typ.__qualname__.replace(".", "_")
            probable_handler = f"{func}_{typ_name}"
            if not hasattr(slf, probable_handler):
                raise OverloadNotFound("No valid overload found!")
            return getattr(slf, probable_handler)(arg)

        def __inner_slow(slf, arg, typ):
            candidate = None
            candidate_depth = float("inf")
            for overload_typ in slow_overloads:
                if overload_typ == object:
                    # Handle object serparately
                    continue
                if issubclass(typ, overload_typ):
                    typ_mro = typ.mro()
                    for idx, super_typ in enumerate(typ_mro):
                        if super_typ == overload_typ:
                            if idx < candidate_depth:
                                candidate = super_typ
                                candidate_depth = idx
            if candidate is not None:
                return __inner_fast(slf, arg, candidate)
            return __inner_fast(slf, arg, object)

        def __inner(slf, arg):
            typ = type(arg)
            try:
                return __inner_fast(slf, arg, typ)
            except OverloadNotFound:
                if slow_overloads is None:
                    raise
                return __inner_slow(slf, arg, typ)

        return __inner

    def __new__(mcl, name, bases, attrs, **kwargs):
        module = attrs["__module__"]
        qualname = attrs["__qualname__"]
        map_key = f"{module}_{qualname}"
        attrs_to_add = {}
        slow_overloads = {}
        use_slow_overloads = kwargs.get("slow_overloads", False)
        for func, overloads in mcl.overload_map[map_key].items():
            func_overloads = []
            if use_slow_overloads:
                for base in bases:
                    if hasattr(base, "__overloader_overloads"):
                        base_overloads = getattr(base, "__overloader_overloads")
                        func_overloads.extend(base_overloads.get(func, []))
            if func in attrs:
                attrs.pop(func)
            for overload_typ, overload_handler in overloads:
                func_suffix = overload_typ.__qualname__.replace(".", "_")
                attrs_to_add[f"{func}_{func_suffix}"] = overload_handler
                func_overloads.append(overload_typ)
            if kwargs.get("slow_overloads", False):
                attrs_to_add[func] = mcl.dynamic_dispatch(func, func_overloads)
            else:
                attrs_to_add[func] = mcl.dynamic_dispatch(func)
            slow_overloads[func] = func_overloads
        attrs_to_add[f"__overloader_overloads"] = slow_overloads
        attrs |= attrs_to_add
        return super().__new__(mcl, name, bases, attrs)
