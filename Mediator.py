from typing import Tuple, Sequence
import json
import re
import Auxledsdata
import CommonData

import profiledata

# auxledsdata
leds_list = ["Led1", "Led2", "Led3", "Led4", "Led5", "Led6", "Led7", "Led8"]
config_key = 'Config'
seq_key = "Sequence"
repeat_key = "Repeat"
start_key = "StartingFrom"
count_key = "Count"
name_key = "Name"
brightness_key = "Brightness"
smooth_key = "Smooth"
wait_key = "Wait"

# commondata
main_sections_default = ['Blade', 'Blade2', 'Volume', 'PowerOffTimeout', 'DeadTime', 'ClashFlashDuration', 'Motion']
main_sections = ['Blade', 'Blade2', 'Volume', 'DeadTime', 'General']
blade_keys = ['BandNumber', 'PixPerBand']
volume_keys = ['Common', 'CoarseLow', 'CoarseMid', 'CoarseHigh']
deadtime_keys = ['AfterPowerOn', 'AfterBlaster', 'AfterClash']
motion_keys = ['Swing', 'Spin', 'Clash', 'Stab', 'Screw']
swing_keys = ['HighW', 'WPercent', 'Circle', 'CircleW']
spin_keys = ['Enabled', 'Counter', 'W', 'Circle', 'WLow']
clash_keys = ['HighA', 'Length', 'HitLevel', 'LowW']
stab_keys = ['Enabled', 'HighA', 'LowW', 'HitLevel', 'Length', 'Percent']
screw_keys = ['Enabled', 'LowW', 'HighW']
other_keys = ['PowerOffTimeout', 'ClashFlashDuration']
connection = {'Blade': blade_keys, 'Blade2': blade_keys, 'Volume': volume_keys, 'Deadtime': deadtime_keys,
              'Motion': motion_keys}
motion_connection = {'Swing': swing_keys, 'Spin': spin_keys, 'Clash': clash_keys, 'Stab': stab_keys,
                     'Screw': screw_keys}
main_list = [blade_keys, blade_keys, volume_keys, deadtime_keys, other_keys]
motion_list = [swing_keys, spin_keys, clash_keys, stab_keys, screw_keys]
motion_key = 'Motion'

# profiledata
poweron_keys = [['Blade', 'Speed']]
working_keys = [['Color'], ['Flaming'], ['FlickeringAlways']]
poweroff_keys = [['Blade', 'Speed'], ['Blade', 'MoveForward']]
flaming_keys = [['Size', 'Min'], ['Size', 'Max'], ['Speed', 'Min'], ['Speed', 'Max'], ['Delay_ms', 'Min'],
                ['Delay_ms', 'Max']]
flaming_color_path = ['Flaming', 'Colors']
flickering_keys = [['Time', 'Min'], ['Time', 'Max'], ['Brightness', 'Min'], ['Brightness', 'Max']]
blaster_keys = [['Color'], ['Duration_ms'], ['SizePix']]
clash_keys = [['Color'], ['Duration_ms'], ['SizePix']]
stab_keys = [['Color'], ['Duration_ms'], ['SizePix']]
lockup_keys = [['Flicker', 'Color'], ['Flicker', 'Time', 'Min'], ['Flicker', 'Time', 'Max'],
               ['Flicker', 'Brightness', 'Min'], ['Flicker', 'Brightness', 'Max'], ['Flashes', 'Period', 'Min'],
               ['Flashes', 'Period', 'Max'], ['Flashes', 'Color'], ['Flashes', 'Duration_ms'], ['Flashes', 'SizePix']]
profile_list = [poweron_keys, working_keys, poweroff_keys, flaming_keys, flickering_keys, blaster_keys, clash_keys,
                stab_keys, lockup_keys]
tab_list = ['PowerOn', 'WorkingMode', 'PowerOff', 'Flaming', 'Flickering', 'Blaster', 'Clash', 'Stab', 'Lockup']


def get_leds_from_config(config: str) -> Sequence[str]:
    """
    gets leds list from config string
    :param config: string with config
    :return: leds list
    """
    return config.split(", ")


def get_config_name_from_leds(leds: Sequence[str]) -> str:
    """
    creates name for config string using leds names
    :param leds: list of leds
    :return: config name
    """
    return ', '.join(leds)


def get_step_name(name: str, brightnesses: list, wait: int, smooth: int) -> str:
    """
    gets step name for item tree using parameters values
    :param name: name of step
    :param brightnesses: list of leds brightnesses
    :param wait: wait value
    :param smooth: smooth value
    :return: parameter string
    """
    step_text = []
    if name:
        step_text.append('Name: %s' % name)
    if brightnesses:
        brightnesses = list(map(str, brightnesses))
        brightnesses = ', '.join(brightnesses)
        step_text.append("Brightness: [%s]" % brightnesses)
    if wait > 0:
        step_text.append('Wait: %i' % wait)
    if smooth > 0:
        step_text.append('Smooth: %i' % smooth)
    step_text = ', '.join(step_text)
    return step_text


def get_repeat_name(startstep: str, count: str) -> str:
    """
    create name for repeat step using parameters
    :param startstep: name of step to start repeat
    :param count: number of repeats
    :return: step name
    """
    return "Repeat: StartFrom: %s, Count: %s" % (startstep, count)


def get_currrent_step_name(name: str) -> str:
    """
    gets step name from name with parameters
    :param name: name wit parameters
    :return: step_name
    """
    text_items = name.split(', ')
    step_name = ""
    for item in text_items:
        words = item.split(": ")
        if words[0] == 'Name':
            step_name = words[1]
    return step_name


def get_param_from_repeat(name: str) -> Tuple[str, str]:
    """
    gets startstep and count from step name
    :param name: step name
    :return: start step, count
    """
    start_step = name.split(', ')[0].split(": ")[2]
    count = name.split(', ')[1].split(": ")[1]
    if count != 'forever':
        count = int(count)
    return start_step, count


def get_param_from_name(name: str) -> Tuple[str, list, int, int]:
    """
    get name, brightness, smooth and wait from step
    :param name: step name
    :return: name, brightness, smooth, wait
    """
    name = re.sub(r'([A-Za-z0-9]\w*)', r'"\1"', name)
    name = re.sub(r'"([0-9]+)"', r'\1', name)
    name = "{" + name + "}"
    parts = json.loads(name)
    step_name = parts.get(name_key, "")
    brightness = parts.get(brightness_key, "")
    wait = parts.get(wait_key, 0)
    smooth = parts.get(smooth_key, 0)
    return step_name, brightness, wait, smooth


def translate_json_to_tree_structure(data: str) -> Tuple[dict, str, str]:
    """
    translate data from file to tree view
    :param data: dict with data
    :return: dict fot tree,  error and warning
    """
    data_for_loading = dict()
    auxdata = Auxledsdata.AuxEffects()
    data, error, warning = auxdata.LoadDataFromText(data)
    if error:
        return None, error, warning
    for effect in data.keys():
        data_for_loading[effect] = dict()
        for sequencer in data[effect]:
            name = get_config_name_from_leds(sequencer[config_key])
            led_dict = {name: []}
            data_for_loading[effect] = led_dict
            for step in sequencer[seq_key]:
                if repeat_key in step.keys():
                    startstep = step[repeat_key][start_key]
                    count = step[repeat_key][count_key]
                    data_for_loading[effect][name].append(get_repeat_name(startstep, count))
                else:
                    step_name = step.get(name_key, "")
                    brightness = step.get(brightness_key, [])
                    wait = step.get(wait_key, 0)
                    smooth = step.get(smooth_key, 0)
                    data_for_loading[effect][name].append(get_step_name(step_name, brightness, wait, smooth))

    return data_for_loading, "", warning


def change_keylist(key_list: Sequence[str]):
    """
    changes  keylist moving general settings to their right place
    :param key_list: path of keys
    :return: new path of keys
    """
    if 'General' in key_list:
        key_list.remove('General')
    return key_list


def get_common_data(text: str) -> Tuple[dict, str, str]:
    """
    gets common data using common data file parsing from corresponding module
    :param text: text of file
    :return: data, error, warning
    """
    commondata = Commondata.CommonData()
    return commondata.load_data_from_text(text)


def color_data_to_str(color: Sequence[int]) -> str:
    """
    converts rgb list to string
    :param color: rgb list [0, 255, 0]
    :return: strint ("0, 255, 0"
    """
    return ', '.join(list(map(str, color)))


def str_to_color_data(color: str) -> Sequence[int]:
    """
    parces str to list with rgb components
    :param color: str "0, 255, 0"
    :return: list [0, 255, 0]
    """
    return list(map(int, color.split(', ')))
