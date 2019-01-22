import pprint
from typing import Tuple, Any, Callable, List, Dict

import IniToJson
import sys
import CommonChecker

defaults: Dict[str, Any] = {'Blade': {'BandNumber': 3, 'PixPerBand': 144, 'StartFlashFrom': 15},
            'Blade2': {'Enabled': 0, 'BandNumber': 1, 'PixPerBand': 25, 'StartFlashFrom': 8},
            'Volume': {'Common': 100, 'CoarseLow': 50, 'CoarseMid': 93, 'CoarseHigh': 100},
            'PowerOffTimeout': 10,
            'DeadTime': {'AfterPowerOn': 500, 'AfterBlaster': 500, 'AfterClash': 500},
            'Motion':
                {'Swing': {'HighW': 6, 'WPercent': 50, 'Circle': 640, 'CircleW': 15},
                 'Spin': {'Enabled': 1, 'Counter': 4, 'W': 70, 'Circle': 640, 'WLow': 40},
                 'Clash': {'HighA': 3500, 'Length': 15, 'HitLevel': -200, 'LowW': 7},
                 'Stab': {'Enabled': 1, 'HighA': 150, 'LowW': 7, 'HitLevel': -200, 'Length': 30, 'Percent': 90},
                 'Screw': {'Enabled': 0, 'LowW': 5, 'HighW': 200}}}

main_sections_default = ['Blade', 'Blade2', 'Volume', 'PowerOffTimeout', 'DeadTime', 'Motion']
main_sections = ['Blade', 'Blade2', 'Volume', 'DeadTime', 'Motion']
blade_keys = ['BandNumber', 'PixPerBand', 'StartFlashFrom']
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


class CommonData:

    def __init__(self):
        self.data = {'Blade': {'BandNumber': 3, 'PixPerBand': 144, 'StartFlashFrom': 15},
                     'Blade2': {'Enabled': 1, 'BandNumber': 1, 'PixPerBand': 12, 'StartFlashFrom': 8},
                     'Volume': {'Common': 100, 'CoarseLow': 50, 'CoarseMid': 93, 'CoarseHigh': 100},
                     'PowerOffTimeout': 300,
                     'DeadTime': {'AfterPowerOn': 500, 'AfterBlaster': 500, 'AfterClash': 500},
                     'Motion':
                         {'Swing': {'HighW': 6, 'WPercent': 50, 'Circle': 640, 'CircleW': 15},
                          'Spin': {'Enabled': 1, 'Counter': 4, 'W': 70, 'Circle': 640, 'WLow': 40},
                          'Clash': {'HighA': 3500, 'Length': 15, 'HitLevel': -200, 'LowW': 7},
                          'Stab': {'Enabled': 1, 'HighA': 150, 'LowW': 7, 'HitLevel': -200, 'Length': 30,
                                   'Percent': 90},
                          'Screw': {'Enabled': 0, 'LowW': 5, 'HighW': 200}}}

    def update_value(self, key_list: List[str], value: Any):
        """
        saves value to data dict to key found by path of keys
        :param key_list: path of keys
        :param value: value to set
        :return:
        """
        data = self.data
        for key in key_list[:-1]:
            data = data[key]
        data[key_list[-1]] = value

    def save_to_file(self, filename):
        data = self.data.copy()
        if data['Blade2']['Enabled']:
            data['Blade2'].pop('Enabled')
        else:
            data.pop('Blade2')
        text = pprint.pformat(data, indent=0)
        text = text.replace(r"'", "")
        f = open(filename, "w", encoding='utf-8')
        f.write(text)

    def get_default_value(self, key_list: List[str]) -> Dict[str, Any]:
        """
        get value from defaults using key path
        :param key_list: path of keys
        :return: value
        """
        temp_data = defaults
        for key in key_list:
            temp_data = temp_data[key]
        return temp_data

    def check_section(self, new_data: dict, check_function: Callable, param: str, required: bool, default: Dict[str, Any])\
            -> Tuple[str, dict]:
        """
        checks section of loaded from text data
        :param new_data: data
        :param check_function: function to check with
        :param param: key of section
        :param required: is this section required
        :param default: needed part of default dict
        :return: warning text, new_data correcter
        """
        checker = CommonChecker.CommonChecker()
        warning = ""
        e, w, wrong_data_keys, wrong_keys = check_function(new_data, param.lower())
        if required and e:
            new_data[param] = default[param]
            warning = warning + param + ': ' + e + " default values are used;\n"
        section_key = checker.get_key(new_data, param)
        if w:
            warning = warning + param + ': ' + w + "Default values are used;\n"
        for key in wrong_data_keys:
            real_key = checker.get_key(new_data[section_key], key)
            real_def_key = checker.get_key(default[param], key)
            new_data[section_key][real_key] = default[param][real_def_key]
        for key in wrong_keys:
            new_data[section_key].pop(key)
        return warning, new_data

    def get_defaults_for_absent(self, new_data):
        """
        checks if some data is absent and loads default
        :param new_data: dict with data
        :return: data updated with defaults values
        """
        checker = CommonChecker.CommonChecker()
        for key in main_sections_default:
            real_key = checker.get_key(new_data, key)
            if not real_key:
                new_data[key] = defaults[key]
        for key in connection.keys():
            real_top_key = checker.get_key(new_data, key)
            for secondlevel_key in connection[key]:
                real_key = checker.get_key(new_data[real_top_key], secondlevel_key)
                if not real_key:
                    new_data[real_top_key][secondlevel_key] = defaults[key][secondlevel_key]
        motion_key = checker.get_key(new_data, 'Motion')
        for key in motion_connection.keys():
            real_top_key = checker.get_key(new_data[motion_key], key)
            for secondlevel_key in motion_connection[key]:
                real_key = checker.get_key(new_data[motion_key][real_top_key], secondlevel_key)
                if not real_key:
                    new_data[motion_key][real_top_key][secondlevel_key] = defaults['Motion'][key][secondlevel_key]
        return new_data

    def load_data_from_text(self, text: str):
        new_data, error = IniToJson.get_json(text)
        if error or new_data is None:
            return None, error, ""
        checker = CommonChecker.CommonChecker()
        try:
            # check common keys
            warning, wrong_keys = checker.common_check_keys(new_data)
            for key in wrong_keys:
                new_data.pop(key)

            w, new_data = self.check_section(new_data, checker.check_blade, 'Blade', True, defaults)
            warning += w
            w, new_data = self.check_section(new_data, checker.check_blade, 'Blade2', False, defaults)
            warning += w
            key_blade2 = CommonChecker.get_real_key(new_data, 'blade2')
            if key_blade2:
                new_data[key_blade2]['Enabled'] = 1
            w, new_data = self.check_section(new_data, checker.check_volume, 'Volume', True, defaults)
            warning += w
            w, new_data = self.check_section(new_data, checker.check_deadtime, 'DeadTime', True, defaults)
            warning += w
            w, new_data = self.check_section(new_data, checker.check_top_number, 'PowerOffTimeout', True, defaults)
            warning += w
            motion: str = checker.get_key(new_data, 'Motion')
            w, wrong_keys = checker.motion_check_keys(new_data[motion])
            for key in wrong_keys:
                new_data[motion].pop(key)
            warning += w
            w, new_data[motion] = self.check_section(new_data[motion], checker.check_swing, 'Swing', True,
                                                     defaults[motion])
            warning += w
            w, new_data[motion] = self.check_section(new_data[motion], checker.check_spin, 'Spin', True,
                                                     defaults[motion])
            warning += w
            w, new_data[motion] = self.check_section(new_data[motion], checker.check_clash, 'Clash', True,
                                                     defaults[motion])
            warning += w
            w, new_data[motion] = self.check_section(new_data[motion], checker.check_stab, 'Stab', True,
                                                     defaults[motion])
            warning += w
            w, new_data[motion] = self.check_section(new_data[motion], checker.check_screw, 'Screw', True,
                                                     defaults[motion])
            warning += w
            new_data = self.get_defaults_for_absent(new_data)

            return new_data, "", warning

        except Exception:
            e = sys.exc_info()[1]
            return None, e.args[0], ""
