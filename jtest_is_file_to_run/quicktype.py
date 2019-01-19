# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = coordinate_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import List, Any, Optional, Union, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_none(x: Any) -> Any:
    assert x is None
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class LEDGroup:
    leds: List[int]
    name: str

    @staticmethod
    def from_dict(obj: Any) -> 'LEDGroup':
        assert isinstance(obj, dict)
        leds = from_list(from_int, obj.get("Leds"))
        name = from_str(obj.get("Name"))
        return LEDGroup(leds, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Leds"] = from_list(from_int, self.leds)
        result["Name"] = from_str(self.name)
        return result


@dataclass
class Repeat:
    count: str
    starting_from: str

    @staticmethod
    def from_dict(obj: Any) -> 'Repeat':
        assert isinstance(obj, dict)
        count = from_str(obj.get("Count"))
        starting_from = from_str(obj.get("StartingFrom"))
        return Repeat(count, starting_from)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Count"] = from_str(self.count)
        result["StartingFrom"] = from_str(self.starting_from)
        return result


@dataclass
class Step:
    brightness: Optional[List[Union[int, str]]]
    name: Optional[str]
    smooth: Optional[int]
    wait: Optional[int]
    repeat: Optional[Repeat]

    @staticmethod
    def from_dict(obj: Any) -> 'Step':
        assert isinstance(obj, dict)
        brightness = from_union([lambda x: from_list(lambda x: from_union([from_int, from_str], x), x), from_none], obj.get("Brightness"))
        name = from_union([from_str, from_none], obj.get("Name"))
        smooth = from_union([from_int, from_none], obj.get("Smooth"))
        wait = from_union([from_int, from_none], obj.get("Wait"))
        repeat = from_union([Repeat.from_dict, from_none], obj.get("Repeat"))
        return Step(brightness, name, smooth, wait, repeat)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Brightness"] = from_union([lambda x: from_list(lambda x: from_union([from_int, from_str], x), x), from_none], self.brightness)
        result["Name"] = from_union([from_str, from_none], self.name)
        result["Smooth"] = from_union([from_int, from_none], self.smooth)
        result["Wait"] = from_union([from_int, from_none], self.wait)
        result["Repeat"] = from_union([lambda x: to_class(Repeat, x), from_none], self.repeat)
        return result


@dataclass
class Sequencer:
    group: str
    name: str
    sequence: List[Step]

    @staticmethod
    def from_dict(obj: Any) -> 'Sequencer':
        assert isinstance(obj, dict)
        group = from_str(obj.get("Group"))
        name = from_str(obj.get("Name"))
        sequence = from_list(Step.from_dict, obj.get("Sequence"))
        return Sequencer(group, name, sequence)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Group"] = from_str(self.group)
        result["Name"] = from_str(self.name)
        result["Sequence"] = from_list(lambda x: to_class(Step, x), self.sequence)
        return result


@dataclass
class Coordinate:
    led_groups: List[LEDGroup]
    sequencers: List[Sequencer]

    @staticmethod
    def from_dict(obj: Any) -> 'Coordinate':
        assert isinstance(obj, dict)
        led_groups = from_list(LEDGroup.from_dict, obj.get("LedGroups"))
        sequencers = from_list(Sequencer.from_dict, obj.get("Sequencers"))
        return Coordinate(led_groups, sequencers)

    def to_dict(self) -> dict:
        result: dict = {}
        result["LedGroups"] = from_list(lambda x: to_class(LEDGroup, x), self.led_groups)
        result["Sequencers"] = from_list(lambda x: to_class(Sequencer, x), self.sequencers)
        return result


def coordinate_from_dict(s: Any) -> Coordinate:
    return Coordinate.from_dict(s)


def coordinate_to_dict(x: Coordinate) -> Any:
    return to_class(Coordinate, x)
