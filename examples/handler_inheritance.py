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
