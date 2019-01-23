# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = coordinate_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import List, Any, Optional, Union, TypeVar, Callable, Type, cast
import functools

T = TypeVar("T")
T1 = TypeVar("T1")
warnings = ""


def dummylogger(*args: Any) -> str:
    return ""


def from_list(f: Callable[..., T]) -> Callable[..., List[T]]:
    def _from_list(f: Callable[..., T], x: Any, err_callback=dummylogger) -> List[T]:
        import sys
        if isinstance(x, list):
            global warnings
            parsedlist: List[T] = []
            for item in x:
                try:
                    parsedlist.append(f(item))
                except Exception as e:
                    warnings += err_callback(item, sys.exc_info()[1].args[0])
        raise ValueError(f"{x} is not instance of list")

    return functools.partial(_from_list, f)


def from_int(x: Any) -> int:
    if isinstance(x, int) and not isinstance(x, bool):
        return x
    raise ValueError(f"{x} is not instance of int")


def from_str(x: Any) -> str:
    if isinstance(x, str):
        return x
    raise ValueError(f"{x} is not instance of str")


def union(f1: Callable[..., T], f2: Callable[..., T1]) -> Callable[..., Union[T, T1]]:
    def _from_union(f1: Callable[..., T], f2: Callable[..., T1], x: Any) -> Union[T, T1]:
        fs: List[Callable[..., Union[T, T1]]] = [f1, f2]
        for f in fs:
            try:
                r = f(x)
                return r
            except:
                pass
        raise ValueError(f"{x} cannot be parsed by any {[str(f.__qualname__) for f in [f1, f2]]}")

    return functools.partial(_from_union, f1, f2)


def optional(f: Callable[..., T]):
    return union(f, from_none)


def zeroable(f: Callable[..., T]):
    return union(f, zero)


def stringable(f: Callable[..., T]):
    return union(f, empty_string)


def from_none(x: Any) -> None:
    if x is None:
        return x
    raise ValueError(f"{x} is not None")


def zero(x: Any) -> int:
    return 0


def empty_string(x: Any) -> str:
    return ""


def to_class(c: Type[T], x: Any) -> dict:
    if isinstance(x, c):
        return cast(Any, x).to_dict()
    raise ValueError(f"{x} is not instance of {c.__name__}")


@dataclass
class LEDGroup:
    leds: List[int]
    name: str

    @staticmethod
    def parse(obj: dict) -> 'LEDGroup':
        assert isinstance(obj, dict)
        leds = from_list(from_int)(obj.get("Leds"))
        name = from_str(obj.get("Name"))
        return LEDGroup(leds, name)

    # def to_dict(self) -> dict:
    #     result: dict = {}
    #     result["Leds"] = from_list(from_int)(self.leds)
    #     result["Name"] = from_str(self.name)
    #     return result


@dataclass
class Repeater:
    Count: str
    StartingFrom: str

    @staticmethod
    def parse(obj: Any) -> 'Repeater':
        assert isinstance(obj, dict)
        count = from_str(obj["Repeat"].get("Count"))
        starting_from = from_str(obj["Repeat"].get("StartingFrom"))
        return Repeater(count, starting_from)

    def to_dict(self) -> dict:
        result: dict = {"Repeat": {}}
        result["Repeat"]["Count"] = from_str(self.Count)
        result["Repeat"]["StartingFrom"] = from_str(self.StartingFrom)
        return result


@dataclass
class Step:
    Brightness: List[Union[int, str]]
    Name: str = ""
    Smooth: int = 0
    Wait: int = 0

    @staticmethod
    def parse(obj: Any) -> 'Step':
        if not isinstance(obj, dict):
            raise ValueError(f"{obj} is not a dict")
        # if "Repeat" in obj:
        #     raise ValueError(f"{obj} is a Repeater")
        brightness = from_list(zeroable(union(from_int, from_str)))(obj.get("Brightness"))
        name = stringable(from_str)(obj.get("Name"))
        smooth = zeroable(from_int)(obj.get("Smooth"))
        wait = zeroable(from_int)(obj.get("Wait"))
        return Step(brightness, name, smooth, wait)

    # def to_dict(self) -> dict:
    #     result: dict = {}
    #     result["Brightness"] = from_list(zeroable(union(from_int, from_str)))(self.Brightness)
    #     result["Name"] = stringable(from_str)(self.Name)
    #     result["Smooth"] = zeroable(from_int)(self.Smooth)
    #     result["Wait"] = zeroable(from_int)(self.Wait)
    #     return result


@dataclass
class Sequencer:
    Group: str
    Name: str
    Sequence: List[Union[Step, Repeater]]

    @staticmethod
    def parse(obj: Any) -> 'Sequencer':
        assert isinstance(obj, dict)
        group = from_str(obj.get("Group"))
        name = from_str(obj.get("Name"))
        sequence = from_list(union(Step.parse, Repeater.parse))(obj.get("Sequence"))
        return Sequencer(group, name, sequence)

    # def to_dict(self) -> dict:
    #     result: dict = {}
    #     result["Group"] = from_str(self.Group)
    #     result["Name"] = from_str(self.Name)
    #     result["Sequence"] = from_list(union(Step.to_dict, Repeater.to_dict))(self.Sequence)
    #     return result


@dataclass
class AuxEffects:
    LedGroups: List[LEDGroup]
    Sequencers: List[Sequencer]

    @staticmethod
    def parse(obj: Any) -> 'AuxEffects':
        assert isinstance(obj, dict)
        # led_groups = None
        led_groups = from_list(LEDGroup.parse)(obj.get("LedGroups"))
        sequencers = from_list(Sequencer.parse)(obj.get("Sequencers"))
        return AuxEffects(led_groups, sequencers)

    # def to_dict(self) -> dict:
    #     """
    #     This is serialization of object. No typing provided for returned dictionary.
    #     For use *STRICTLY* on jsoning.
    #     :return:
    #     """
    #     result: dict = {}
    #     result["LedGroups"] = from_list(lambda x: to_class(LEDGroup, x))(self.LedGroups)
    #     result["Sequencers"] = from_list(lambda x: to_class(Sequencer, x))(self.Sequencers)
    #     return result


def auxeffects_from_dict(s: Any) -> AuxEffects:
    global warnings
    warnings = ""
    parsed = AuxEffects.parse(s)
    return parsed, warnings
