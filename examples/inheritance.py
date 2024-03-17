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
