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


def from_list(f: Callable[[Any], T]) -> Callable[[Any], List[T]]:
    def _from_list(f: Callable[[Any], T], x: Any) -> List[T]:
        if isinstance(x, list):
            return [f(y) for y in x]
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


def union(fs: List[Callable[[Any], T]]) -> Callable[[Any], T]:
    def _from_union(fs: List[Callable[[Any], T]], x: Any) -> T:
        for f in fs:
            try:
                return f(x)
            except:
                pass
        raise ValueError(f"{x} cannot be parsed by any {[str(f.__qualname__) for f in fs]}")

    return functools.partial(_from_union, fs)


# def optional(fs: List[Callable[[Any],T]]):
#     params = fs.append(from_none)
#     return union(params)


def from_none(x: Any) -> None:
    if x is None:
        return x
    raise ValueError(f"{x} is not None")


def zero(x: Any) -> int:
    return 0


def empty(x: Any) -> str:
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
    def from_dict(obj: dict) -> 'LEDGroup':
        assert isinstance(obj, dict)
        leds = from_list(from_int)(obj.get("Leds"))
        name = from_str(obj.get("Name"))
        return LEDGroup(leds, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Leds"] = from_list(from_int)(self.leds)
        result["Name"] = from_str(self.name)
        return result


@dataclass
class Repeater:
    Count: str
    StartingFrom: str

    @staticmethod
    def from_dict(obj: Any) -> 'Repeater':
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
    Brightness: Optional[List[Union[int, str]]]
    Name: Optional[str]
    Smooth: Optional[int]
    Wait: Optional[int]

    @staticmethod
    def from_dict(obj: Any) -> 'Step':
        if not isinstance(obj, dict):
            raise ValueError(f"{obj} is not a dict")
        if "Repeat" in obj:
            raise ValueError(f"{obj} is a Repeater")
        brightness = \
            union([from_list(union([from_int, from_str, zero])), from_none])(obj.get("Brightness"))
        name = union([from_str, empty])(obj.get("Name"))
        smooth = union([from_int, zero])(obj.get("Smooth"))
        wait = union([from_int, zero])(obj.get("Wait"))
        return Step(brightness, name, smooth, wait)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Brightness"] = union(
            [from_list(union([from_int, from_str])), from_none])(self.Brightness)
        result["Name"] = union([from_str])(self.Name)
        result["Smooth"] = union([from_int, from_none])(self.Smooth)
        result["Wait"] = union([from_int, from_none])(self.Wait)
        return result


@dataclass
class Sequencer:
    Group: str
    Name: str
    Sequence: List[Union[Step, Repeater]]

    @staticmethod
    def from_dict(obj: Any) -> 'Sequencer':
        assert isinstance(obj, dict)
        group = from_str(obj.get("Group"))
        name = from_str(obj.get("Name"))
        sequence = from_list(union([Step.from_dict, Repeater.from_dict]))(obj.get("Sequence"))
        return Sequencer(group, name, sequence)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Group"] = from_str(self.Group)
        result["Name"] = from_str(self.Name)
        result["Sequence"] = from_list(union([Step.to_dict, Repeater.to_dict]))(self.Sequence)
        return result


@dataclass
class AuxEffects:
    LedGroups: List[LEDGroup]
    Sequencers: List[Sequencer]

    @staticmethod
    def from_dict(obj: Any) -> 'AuxEffects':
        assert isinstance(obj, dict)
        # led_groups = None
        led_groups = from_list(LEDGroup.from_dict)(obj.get("LedGroups"))
        sequencers = from_list(Sequencer.from_dict)(obj.get("Sequencers"))
        return AuxEffects(led_groups, sequencers)

    def to_dict(self) -> dict:
        """
        This is serialization of object. No typing provided for returned dictionary.
        For use *STRICTLY* on jsoning.
        :return:
        """
        result: dict = {}
        result["LedGroups"] = from_list(lambda x: to_class(LEDGroup, x))(self.LedGroups)
        result["Sequencers"] = from_list(lambda x: to_class(Sequencer, x))(self.Sequencers)
        return result


def auxeffects_from_dict(s: Any) -> AuxEffects:
    return AuxEffects.from_dict(s)


def coordinate_to_dict(x: AuxEffects) -> Any:
    return to_class(AuxEffects, x)
