from this_is_stupid import Overloadable

class Base:
    pass

class SpecificHandler(metaclass=Overloadable):

    @Overloadable.overload
    def onCallback(self, value: Base):
        print(f"{value} is Base!")


if __name__ == "__main__":
    handler = SpecificHandler()
    handler.onCallback(Base())
