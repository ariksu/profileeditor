# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = welcome_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import List, Any, Optional, Union, TypeVar, Callable, Type, cast
from enum import Enum


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class LEDGroup:
    name: str
    leds: List[int]

    @staticmethod
    def from_dict(obj: Any) -> 'LEDGroup':
        assert isinstance(obj, dict)
        name = from_str(obj.get("Name"))
        leds = from_list(from_int, obj.get("Leds"))
        return LEDGroup(name, leds)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Name"] = from_str(self.name)
        result["Leds"] = from_list(from_int, self.leds)
        return result


class Name(Enum):
    STEP1 = "Step1"
    STEP2 = "Step2"
    STEP3 = "Step3"
    THE_56_STEP1 = "56Step1"


@dataclass
class Repeat:
    starting_from: Name
    count: str

    @staticmethod
    def from_dict(obj: Any) -> 'Repeat':
        assert isinstance(obj, dict)
        starting_from = Name(obj.get("StartingFrom"))
        count = from_str(obj.get("Count"))
        return Repeat(starting_from, count)

    def to_dict(self) -> dict:
        result: dict = {}
        result["StartingFrom"] = to_enum(Name, self.starting_from)
        result["Count"] = from_str(self.count)
        return result


@dataclass
class Sequence:
    smooth: Optional[int]
    brightness: Optional[List[Union[int, str]]]
    name: Optional[Name]
    wait: Optional[int]
    repeat: Optional[Repeat]

    @staticmethod
    def from_dict(obj: Any) -> 'Sequence':
        assert isinstance(obj, dict)
        smooth = from_union([from_int, from_none], obj.get("Smooth"))
        brightness = from_union([lambda x: from_list(lambda x: from_union([from_int, from_str], x), x), from_none], obj.get("Brightness"))
        name = from_union([Name, from_none], obj.get("Name"))
        wait = from_union([from_int, from_none], obj.get("Wait"))
        repeat = from_union([Repeat.from_dict, from_none], obj.get("Repeat"))
        return Sequence(smooth, brightness, name, wait, repeat)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Smooth"] = from_union([from_int, from_none], self.smooth)
        result["Brightness"] = from_union([lambda x: from_list(lambda x: from_union([from_int, from_str], x), x), from_none], self.brightness)
        result["Name"] = from_union([lambda x: to_enum(Name, x), from_none], self.name)
        result["Wait"] = from_union([from_int, from_none], self.wait)
        result["Repeat"] = from_union([lambda x: to_class(Repeat, x), from_none], self.repeat)
        return result


@dataclass
class Sequencer:
    name: str
    group: str
    sequence: List[Sequence]

    @staticmethod
    def from_dict(obj: Any) -> 'Sequencer':
        assert isinstance(obj, dict)
        name = from_str(obj.get("Name"))
        group = from_str(obj.get("Group"))
        sequence = from_list(Sequence.from_dict, obj.get("Sequence"))
        return Sequencer(name, group, sequence)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Name"] = from_str(self.name)
        result["Group"] = from_str(self.group)
        result["Sequence"] = from_list(lambda x: to_class(Sequence, x), self.sequence)
        return result


@dataclass
class Welcome:
    led_groups: List[LEDGroup]
    sequencers: List[Sequencer]

    @staticmethod
    def from_dict(obj: Any) -> 'Welcome':
        assert isinstance(obj, dict)
        led_groups = from_list(LEDGroup.from_dict, obj.get("LedGroups"))
        sequencers = from_list(Sequencer.from_dict, obj.get("Sequencers"))
        return Welcome(led_groups, sequencers)

    def to_dict(self) -> dict:
        result: dict = {}
        result["LedGroups"] = from_list(lambda x: to_class(LEDGroup, x), self.led_groups)
        result["Sequencers"] = from_list(lambda x: to_class(Sequencer, x), self.sequencers)
        return result


def welcome_from_dict(s: Any) -> Welcome:
    return Welcome.from_dict(s)


def welcome_to_dict(x: Welcome) -> Any:
    return to_class(Welcome, x)