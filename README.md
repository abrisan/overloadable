# Overloadable

This code is the result of a musing on how we could use metaclasses and type annotations to build overloads into Python classes.

I would not recommend using this in any way shape or form as it is not complete. Hence, the package name is `this_is_stupid`, to remind the reader
that using this code is a **BAD** idea.

## Installing

```sh
(python312) ➜  overload ✗ git clone git@github.com:abrisan/overloadable
(python312) ➜  overload ✗ cd overloadable
(python312) ➜  overload ✗ python3.12 -m pip install -e .
```

## Limitations:

1. Only works with 1-argument functions.
2. *May* not work across import boundaries.
3. Whipped up on a weekend afternoon.

## Examples:

You will find the examples in the `examples` directory, but they are laid out here for ease of read.

### Builtin types:

```
from this_is_stupid import Overloadable


class Handler(metaclass=Overloadable):
    
    @Overloadable.overload
    def onCallback(self, value: int):
        print(f"{value} is an int!")

    @Overloadable.overload 
    def onCallback(self, value: str):
        print(f"{value} is a str!")


if __name__ == "__main__":
    handler = Handler()
    handler.onCallback(2)
```

If we run this, we get:

```
(python312) ➜  overload git:(main) ✗ python examples/simple_example.py 
2 is an int!
```

### User-defined types

`Overloadable` also works with user-defined types.

```
from this_is_stupid import Overloadable

class Base:
    pass

class SpecificHandler(Overloadable):

    @Overloadable.overload
    def onCallback(self, value: Base):
        print(f"{value} is Base!")


if __name__ == "__main__":
    handler = SpecificHandler()
    handler.onCallback(Base())
```

Running, we get:

```
(python312) ➜  overload git:(main) ✗ python examples/user_defined_types.py
<__main__.Base object at 0x103536420> is Base!
```

### Argument Inheritance

Because of the implementation of the code, we can only support argument inheritance if we turn on the 
`slow_overloads` flag in the class declaration. This is because our fast path uses type names to define which overload
to use, whereas `slow_overloads` uses run-time type introspection as a fallback.

```
from this_is_stupid import Overloadable

class Base:
    pass

class Derived(Base):
    pass

class SpecificHandler(metaclass=Overloadable):

    @Overloadable.overload
    def onCallback(self, value: Base):
        print(f"{value} is Base!")


if __name__ == "__main__":
    handler = SpecificHandler()
    handler.onCallback(Derived())
```

Running without `slow_overloads`, we get:

```
(python312) ➜  overload git:(main) ✗ python examples/argument_inheritance.py
Traceback (most recent call last):
  File "/Users/abrisan/Experiments/overload/examples/argument_inheritance.py", line 18, in <module>
    handler.onCallback(Derived())
  File "/Users/abrisan/Experiments/overload/src/this_is_stupid/_overloadable.py", line 56, in __inner
    return __inner_fast(slf, arg, typ)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/abrisan/Experiments/overload/src/this_is_stupid/_overloadable.py", line 32, in __inner_fast
    raise OverloadNotFound("No valid overload found!")
this_is_stupid._overloadable.OverloadNotFound: No valid overload found!
```

If we flip the flag, we get:

```
class SpecificHandler(metaclass=Overloadable, slow_overloads=True):
```

and running:

```
(python312) ➜  overload git:(main) ✗ python3.12 examples/argument_inheritance.py 
<__main__.Derived object at 0x1037c65d0> is Base!
```

When the `slow_overload` flag is enabled, the following rules are used for picking an overload:

1. First, the string-based fast path is tried. If that does not yield anything, we go to step 2.
2. We attempt to choose an overload based on the liskov substitution principle. There may be multiple applicable overloads, we pick the one where the type defined in the overload is "closest" to the argument type provided, based on the MRO. Suppose we have a class C with the following MRO:

```
C -> B -> A -> object
```

and we have two overloads, one defined on type `B` and one defined on type `A`. Our code will pick the `B` overload, as it is closer to `C` in its MRO.
3. If all the above fail, we look for an overload on the `object` typ.

For example, consider:

```
from this_is_stupid import Overloadable

class Base:
    pass

class Derived(Base):
    pass


class SecondDerived(Derived):
    pass

class OtherDerived(Base):
    pass


class SomethingUnrelated:
    pass


class BaseHandler(metaclass=Overloadable, slow_overloads=True):

    @Overloadable.overload
    def onCallback(self, value: object):
        print(f"{value} fell into the catch-all!")

    @Overloadable.overload
    def onCallback(self, value: Base):
        print(f"{value} is a Base!")
    
    @Overloadable.overload
    def onCallback(self, value: Derived):
        print(f"{value} is a Derived!")


if __name__ == "__main__":
    handler = BaseHandler()
    handler.onCallback(SecondDerived())
    handler.onCallback(OtherDerived())
    handler.onCallback(SomethingUnrelated())
```

If we run, we get:

```
(python312) ➜  overload git:(main) ✗ python3.12 examples/inheritance.py          
<__main__.SecondDerived object at 0x1051dacf0> is a Derived!
<__main__.OtherDerived object at 0x1051dacf0> is a Base!
<__main__.SomethingUnrelated object at 0x1051dacf0> fell into the catch-all!
```

### Handler inheritance

This code also works across handler inheritance.

```
from this_is_stupid import Overloadable

class Base:
    pass

class Derived(Base):
    pass

class BaseHandler(metaclass=Overloadable, slow_overloads=True):

    @Overloadable.overload
    def onCallback(self, value: Base):
        print(f"{value} is Base!")


class SpecificHandler(BaseHandler, slow_overloads=True):
    pass


if __name__ == "__main__":
    handler = SpecificHandler()
    handler.onCallback(Derived())
```

If we run this, we get:

```
(python312) ➜  overload git:(main) ✗ python3.12 examples/handler_inheritance.py
<__main__.Derived object at 0x104efe720> is Base!
```
