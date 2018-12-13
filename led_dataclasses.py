error_dict = {
    "LedGroups": [],
    "Sequencers": [
        {
            "Name": "Steady",
            "Group": "Hilt",
            "Sequence": [
                {"Name": "Step1", "Brightness": [100, 0, 0], "Wait": 500, "yasha": 3},
                {"Name": "Step2", "Brightness": [0, 100, 0], "Wait": 500},
                {"Name": "Step3", "Brightness": [0, 0, 100], "Wait": 500},
                {"Repeat": {"StartingFrom": "Step1", "Count": "forever"}},
            ],
        },
        {"Name": "ClashBlasterStab", "Group": "crystal", "Sequence": []},
        {
            "Name": "WorkingHilt",
            "Group": "hilt",
            "Sequence": [
                {"Name": "56Step1", "Brightness": [100, 0, 100], "Wait": 150},
                {"Name": "Step2", "Brightness": [0, 10, 0], "Wait": 150},
                {"Repeat": {"StartingFrom": "56Step1", "Count": "forever"}},
            ],
        },
        {
            "Name": "PowerOffHilt",
            "Group": "Hilt",
            "Sequence": [
                {"Name": "Step1", "Brightness": [0, 0, 100], "Wait": 100},
                {"Name": "Step2", "Brightness": [0, 100, 0], "Wait": 100},
                {"Name": "Step3", "Brightness": [100, 0, 0], "Wait": 100},
                {"Name": "Step1", "Brightness": [0, 0, 100], "Wait": 100},
                {"Name": "Step2", "Brightness": [0, 100, 0], "Wait": 100},
                {"Name": "Step3", "Brightness": [100, 0, 0], "Wait": 100},
                {"Name": "Step1", "Brightness": [0, 0, 100], "Wait": 100},
                {"Name": "Step2", "Brightness": [0, 100, 0], "Wait": 100},
                {"Name": "Step3", "Brightness": [100, 0, 0], "Wait": 100},
            ],
        },
    ],
}

led_raw_dict = {
    "LedGroups": [
        {"Name": "Crystal", "Leds": [1, 2, 3]},
        {"Name": "HILT", "Leds": [4, 5, 6]},
    ],
    "Sequencers": [
        {
            "Name": "PowerOnCrystal",
            "Group": "Crystal",
            "Sequence": [
                {"Smooth": 50, "Brightness": ["Copyred", "CopyGreen", "Copyblue"]}
            ],
        },
        {
            "Name": "Steady",
            "Group": "Hilt",
            "Sequence": [
                {"Name": "Step1", "Brightness": [100, 0, 0], "Wait": 500},
                {"Name": "Step2", "Brightness": [0, 100, 0], "Wait": 500},
                {"Name": "Step3", "Brightness": [0, 0, 100], "Wait": 500},
                {"Repeat": {"StartingFrom": "Step1", "Count": "forever"}},
            ],
        },
        {
            "Name": "PowerOnHilt",
            "Group": "hilt",
            "Sequence": [
                {"Name": "Step1", "Brightness": [100, 0, 0], "Wait": 100},
                {"Name": "Step2", "Brightness": [0, 100, 0], "Wait": 100},
                {"Name": "Step3", "Brightness": [0, 0, 100], "Wait": 100},
                {"Name": "Step1", "Brightness": [100, 0, 0], "Wait": 100},
                {"Name": "Step2", "Brightness": [0, 100, 0], "Wait": 100},
                {"Name": "Step3", "Brightness": [0, 0, 100], "Wait": 100},
                {"Name": "Step1", "Brightness": [100, 0, 0], "Wait": 100},
                {"Name": "Step2", "Brightness": [0, 100, 0], "Wait": 100},
                {"Name": "Step3", "Brightness": [0, 0, 100], "Wait": 100},
            ],
        },
        {
            "Name": "ClashBlasterStab",
            "Group": "crystal",
            "Sequence": [{"Name": "Step2", "Brightness": [100, 100, 100], "Wait": 50}],
        },
        {
            "Name": "WorkingCrystal",
            "Group": "crystal",
            "Sequence": [
                {
                    "Name": "Step1",
                    "Brightness": ["Copyred", "CopyGreen", "Copyblue"],
                    "Wait": 100,
                },
                {"Repeat": {"StartingFrom": "Step1", "Count": "forever"}},
            ],
        },
        {
            "Name": "WorkingHilt",
            "Group": "hilt",
            "Sequence": [
                {"Name": "56Step1", "Brightness": [100, 0, 100], "Wait": 150},
                {"Name": "Step2", "Brightness": [0, 10, 0], "Wait": 150},
                {"Repeat": {"StartingFrom": "56Step1", "Count": "forever"}},
            ],
        },
        {
            "Name": "PowerOffCrystal",
            "Group": "crystal",
            "Sequence": [
                {"Smooth": 150, "Brightness": [0, 0, 0]},
                {"Name": "Step1", "Brightness": [0, 0, 0], "Wait": 999_750},
            ],
        },
        {
            "Name": "PowerOffHilt",
            "Group": "Hilt",
            "Sequence": [
                {"Name": "Step", "Brightness": [0, 0, 100], "Wait": 100},
                {"Name": "Step", "Brightness": [0, 100, 0], "Wait": 100},
                {"Name": "Step", "Brightness": [100, 0, 0], "Wait": 100},
                {"Name": "Step", "Brightness": [0, 0, 100], "Wait": 100},
                {"Name": "Step", "Brightness": [0, 100, 0], "Wait": 100},
                {"Name": "Step", "Brightness": [100, 0, 0], "Wait": 100},
                {"Name": "Step", "Brightness": [0, 0, 100], "Wait": 100},
                {"Name": "Step", "Brightness": [0, 100, 0], "Wait": 100},
                {"Name": "Step", "Brightness": [100, 0, 0], "Wait": 100},
            ],
        },
        {
            "Name": "lockup",
            "Group": "Crystal",
            "Sequence": [
                {
                    "Name": "Step1",
                    "Brightness": ["CopyRed", "CopyGreen", "CopyBlue"],
                    "Wait": 1000,
                },
                {"Repeat": {"StartingFrom": "Step1", "Count": "forever"}},
            ],
        },
    ],
}

import dataclasses
from dataclasses import dataclass, field
from typing import *
from loguru import logger

logger.start("abc.log")


@dataclass
class AuxLed:
    LedGroups: List["LedGroup"] = field(default_factory=list)
    Sequencers: List["Sequencer"] = field(default_factory=list)

    @staticmethod
    def VerifyLength(src_json):
        if len(src_json.get("LedGroups", [])) == 0:
            print(
                """Warning!
                Your LedGroups seemingly contains 0 entries!
                """
            )
        if len(src_json.get("Sequencers", [])) == 0:
            print(
                """Warning!
                Your Sequencers seemingly contains 0 entries!
                """
            )


@dataclass
class LedGroup:
    Name: str
    Leds: List[int]

    @staticmethod
    def CreationError(src_dict, e):
        print(
            f"""
                        Missing requirement in LedGroup description.
                        expecting: 
                        Name: somename, Leds[x,y,z]
                        got
                        {json_dumps(src_dict)}
                        """
        )

    @staticmethod
    def VerifyLength(src_json):
        if len(src_json.get("Leds", [])) == 0:
            print(
                """Warning!
                Your Leds seemingly contains 0 entries!
                """
            )


@dataclass
class Sequencer:
    Name: str
    Group: str
    Sequence: List[Union["Step", "Repeater"]] = field(default_factory=list)

    @staticmethod
    def CreationError(src_dict, e):
        print(
            f"""
                    Missing requirement in Sequencer description.
                    expecting: 
                    Name: somename, Group: somegroup, Steps: [...
                    got
                    {json_dumps(src_dict)}
                    """
        )

    def RemoveDuplicates(self):
        names: Dict[str, int] = dict()
        for step in self.Sequence:
            if isinstance(step, Repeater):
                continue
            name = step.Name
            if not isinstance(step, Repeater) and (name != ''):
                if name not in names:
                    names[name] = 1
                else:
                    names[name] += 1
        for step in self.Sequence:
            if isinstance(step, Repeater):
                continue
            name = step.Name
            if name and (names[name] > 1):
                names[name] -= 1
                step.Name = name + f"({names[name]})"
        pass


@dataclass
class Step:
    Brightness: List[Union[int, str]]
    Name: str = field(default_factory=str)
    Wait: int = 0
    Smooth: int = 0

    @staticmethod
    def CreationError(src_dict, e):
        print(
            f"""
            Missing requirement in Step description.
            expecting: 
            Brightness: [...], [Smooth: x,] [Wait :y]
            got
            {json_dumps(src_dict)}
            """
        )


@dataclass
class Repeater:
    Repeat: Dict[str, str]


import AuxChecker
import sys
from json import dumps as json_dumps

sequencer_keys = ["config", "sequence"]


def DataLoad(json: Dict) -> AuxLed:
    auxleds = AuxLed()
    AuxLed.VerifyLength(json)

    for led in json.get("LedGroups", []):
        try:
            ledgroup = LedGroup(**led)
            auxleds.LedGroups.append(ledgroup)
            LedGroup.VerifyLength(led)
        except Exception as e:
            LedGroup.CreationError(led, e)
    for sequencer in json.get("Sequencers", []):
        try:
            name, group, sequence = sequencer.values()
            auxleds.Sequencers.append(Sequencer(Name=name, Group=group))
        except Exception as e:
            Sequencer.CreationError(sequencer, e)

        for step in sequencer.get("Sequence", []):
            current_sequence = auxleds.Sequencers[-1].Sequence
            if "Repeat" not in step:
                try:
                    current_sequence.append(Step(**step))
                except Exception as e:
                    Step.CreationError(step, e)
            else:
                current_sequence.append(Repeater(**step))
            auxleds.Sequencers[-1].RemoveDuplicates()
    return auxleds


def ValidateAux(data: AuxLed) -> Tuple[Optional[AuxLed], Optional[str], str]:
    # new_data, error = IniToJson.get_json(text)
    error = None
    new_data = data
    if error:
        return None, error, ""
    warning = ""
    Checker = AuxChecker.AuxChecker()
    try:
        wrong_effects = []
        for effect in new_data.keys():

            # check if effect data is a list
            if not isinstance(new_data[effect], list):
                wrong_effects.append(effect)
                warning += "%s effect data is wrong, effect is not loaded.\n" % effect
                continue
            leds_used = []

            for sequencer in new_data[effect]:
                i_seq = new_data[effect].index(sequencer) + 1

                # check if sequencer is a dict
                if not isinstance(sequencer, dict):
                    warning += (
                            "'%s' effect, %i sequencer: Wrong sequencer data, "
                            "sequencer is not loaded.\n" % (effect, i_seq)
                    )
                    new_data[effect].remove(sequencer)
                    continue

                # check sequencer keys and remove wrong
                wrong_keys = []
                for key in sequencer.keys():
                    if key.lower() not in sequencer_keys:
                        warning += (
                                "'%s' effect, %i sequencer: Wrong sequencer data, "
                                "sequencer is not loaded.\n" % (effect, i_seq)
                        )
                        wrong_keys.append(key)
                for key in wrong_keys:
                    sequencer.pop(key)

                # check config part of sequencer
                error, leds_count, leds_used = Checker.check_config(
                    sequencer, leds_used
                )
                if error:
                    warning += (
                            "'%s' effect, %i sequencer: %s "
                            "This sequencer is not loaded.\n" % (effect, i_seq, error)
                    )
                    new_data[effect].remove(sequencer)
                    continue

                # check sequence part of sequencer
                error = Checker.check_sequence(sequencer)
                if error:
                    warning += (
                            "Error: '%s' effect, %i sequencer: %s "
                            "Step for this sequencer are not loaded.\n"
                            % (effect, i_seq, error)
                    )
                    sequencer["Sequence"] = {}
                    continue
                namelist = []
                for step in sequencer["Sequence"]:
                    i_step = sequencer["Sequence"].index(step) + 1

                    # check if step is a dictionary
                    if not isinstance(step, dict):
                        warning += (
                                "Error: '%s' effect, %i sequencer, %i step):"
                                " step data is incorrect, step is skipped.\n"
                                % (effect, i_seq, i_step)
                        )
                        sequencer["Sequence"].remove(step)
                        continue

                    # check if step keys are correct (no wrong steps, brightness or repeat or wait in step)
                    error, w, wrong_keys, = Checker.check_step_keys(step)
                    if error:
                        warning += (
                                "Error: '%s' effect, %i sequencer, %i step): %s "
                                "This step is not loaded.\n"
                                % (effect, i_seq, i_step, error)
                        )
                        sequencer["Sequence"].remove(step)
                        continue
                    if wrong_keys:
                        warning += (
                                "Error: '%s' effect, %i sequencer, %i step): "
                                "%s this data is not loaded.\n" % (effect, i_seq, i_step, w)
                        )
                    for key in wrong_keys:
                        step.pop(key)

                    if "Name" in step.keys():
                        if not isinstance(step["Name"], str):
                            warning += (
                                    "Error: '%s' effect, %i sequencer, %i step): "
                                    "wrong name data, name is skipped.\n"
                                    % (effect, i_seq, i_step)
                            )
                            step.pop("Name")
                        else:
                            if step["Name"] in namelist:
                                warning += (
                                        "Error: '%s' effect, %i sequencer, %i step): "
                                        "name already used, name is skipped.\n"
                                        % (effect, i_seq, i_step)
                                )
                                step.pop("Name")
                            else:
                                namelist.append(step["Name"])

                    # check step brightness correct
                    error, brightness = Checker.check_brightness(step, leds_count)
                    if error:
                        warning += (
                                "Error: '%s' effect, %i sequencer, %i step: %s "
                                "step brightness is skipped.\n"
                                % (effect, i_seq, i_step, error)
                        )
                        if brightness:
                            step.pop(brightness)

                    # check wait parameters is correcr
                    error = Checker.check_wait(step)
                    if error:
                        warning += (
                                "Error: '%s' effect, %i sequencer, %i step: %s "
                                "step wait is skipped.\n" % (effect, i_seq, i_step, error)
                        )
                        step.pop("Wait")

                    # check if smooth parameter is correct
                    error, smooth = Checker.check_smooth(step)
                    if error:
                        warning += (
                                "Error: '%s' effect, %i sequencer, %i step: %s "
                                "step smooth is skipped.\n "
                                % (effect, i_seq, i_step, error)
                        )
                        step.pop(smooth)

                    # check repeat
                    error = Checker.check_repeat(step, namelist)
                    if error:
                        warning += (
                                "Error: '%s' effect, %i sequencer, %i step: %s. "
                                "This repeat step is not loaded\n "
                                % (effect, i_seq, i_step, error)
                        )
                        sequencer["Sequence"].remove(step)

        # remove effects with not list data
        for effect in wrong_effects:
            new_data.pop(effect)
        return new_data, None, warning
    # for everything unexpected
    except Exception:
        e = sys.exc_info()[1]
        return None, e.args[0], ""


def differences(a, b, section=None):
    for [c, d], [h, g] in zip(a.items(), b.items()):
        if not isinstance(d, dict) and not isinstance(g, dict):
            if d != g:
                yield (c, d, g, section)
        else:
            for i in differences(d, g, c):
                for b in i:
                    yield b


from pprint import pprint

aux = DataLoad(led_raw_dict)
# print(aux.LedGroups[0])
# pprint(aux.Sequencers[0])

pprint(dataclasses.asdict(aux))

# a, _, warnings = LoadDataFromText()
# print(list(differences(a, led_dict)))
# print(warnings)
