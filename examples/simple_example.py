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
