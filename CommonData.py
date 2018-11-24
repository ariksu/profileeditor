import json
defaults = {'Blade': {'BandNumber': 3, 'PixPerBand': 70},
            'Blade2': {'BandNumber': 1, 'PixPerBand': 12},
            'Volume': {'Common': 100, 'CoarseLow': 50, 'CoarseMid': 93, 'CoarseHigh': 100},
            'PowerOffTimeout': 300,
            'DeadTime': {'AfterPowerOn': 500, 'AfterBlaster': 500, 'AfterClash': 500},
            'ClashFlashDuration': 72,
            'Motion':
                {'Swing': {'HighW': 6, 'WPercent': 50, 'Circle': 640, 'CircleW': 15},
                 'Spin': {'Enabled': 1, 'Counter': 4, 'W': 70, 'Circle': 640, 'WLow': 40},
                 'Clash': {'HighA': 3500, 'Length': 15, 'HitLevel': -200, 'LowW': 7},
                 'Stab': {'Enabled': 1, 'HighA': 150, 'LowW': 7, 'HitLevel': -200, 'Length': 30, 'Percent': 90},
                 'Screw': {'Enabled': 0, 'LowW': 5, 'HighW': 200}}}

main_sections_default = ['Blade', 'Blade2', 'Volume', 'PowerOffTimeout', 'DeadTime', 'ClashFlashDuration', 'Motion']
main_sections = ['Blade', 'Blade2', 'Volume', 'DeadTime', 'Motion']
blade_keys = ['BandNumber', 'PixPerBand']
volume_keys = [['Common', 'CoarseLow', 'CoarseMid', 'CoarseHigh']]
deadtime_keys = ['AfterPowerOn', 'AfterBlaster', 'AfterClash']
motion_keys = ['Swing', 'Spin', 'Clash', 'Stab', 'Screw']
swing_keys = ['HighW', 'WPercent', 'Circle', 'CircleW']
spin_keys = ['Enabled', 'Counter', 'W', 'Circle', 'WLow']
clash_keys = ['HighA', 'Length', 'HitLevel', 'LowW']
stab_keys = ['Enabled', 'HighA', 'LowW', 'HitLevel', 'Length', 'Percent']
screw_keys = ['Enabled', 'LowW', 'HighW']
other_keys = ['PowerOffTimeout', 'ClashFlashDuration']
connection = {'Blade': blade_keys, 'Blade2': blade_keys, 'Volume': volume_keys, 'Deadtime': deadtime_keys, 'Motion': motion_keys}
motion_connection = {'Swing': swing_keys, 'Spin': spin_keys, 'Clash': clash_keys, 'Stab': stab_keys, 'Screw': screw_keys}


class CommonData:

    def __init__(self):
        self.data = defaults

    def update_value(self, key_list: [str], value):
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
        print(data)

    def save_to_file(self, filename):
        f = open(filename, 'w')
        f.write(json.dumps(self.data))
