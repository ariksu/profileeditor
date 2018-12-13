from typing import Sequence
import json

default_profile = {'AfterWake': {},
                   'PowerOn': {'Blade': {'Speed': 144}},
                   'WorkingMode': {'Color': [0, 255, 0], 'Flaming': 0, 'FlickeringAlways': 1},
                   'PowerOff': {'Blade': {'Speed': 144, 'MoveForward': 0}},
                   'Flaming': {'Size': {'Min': 2, 'Max': 9}, 'Speed': {'Min': 12, 'Max': 27},
                               'Delay_ms': {'Min': 54, 'Max': 180},
                               'Colors': []},
                   'Flickering': {'Time': {'Min': 90, 'Max': 360}, 'Brightness': {'Min': 50, 'Max': 100}},
                   'Blaster': {'Color': 'random', 'Duration_ms': 720, 'SizePix': 7},
                   'Clash': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 11},
                   'Stab': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 11},
                   'Lockup': {'Flicker': {'Color': [255, 0, 0], 'Time': {'Min': 45, 'Max': 80},
                                          'Brightness': {'Min': 50, 'Max': 100}},
                              'Flashes': {'Period': {'Min': 15, 'Max': 25}, 'Color': [255, 0, 0], 'Duration_ms': 50,
                                          'SizePix': 7}},
                   'Blade2': {
                       'IndicateBlasterClashLockup': 1, 'DelayBeforeOn': 200,
                       'WorkingMode': {'Color': [0, 255, 0]},
                        'Flaming': {'AlwaysOn': 1, 'Size': {'Min': 2, 'Max': 9}, 'Speed': {'Min': 12, 'Max': 27},
                                    'Delay_ms': {'Min': 54, 'Max': 180},
                                    'Colors': []},
                        'Flickering': {'AlwaysOn': 1, 'Time': {'Min': 90, 'Max': 360},
                                       'Brightness': {'Min': 50, 'Max': 100}}}}


class Profiles:

    def __init__(self):
        self.data = dict()

    def get_profiles_list(self):
        """
        returns list of profile keys
        :return:
        """
        return self.data.keys()

    def add_profile(self, name: str):
        """
        adds profile with given name and default values
        :param name: name of profile
        :return:
        """
        self.data[name] = {'AfterWake': {},
                           'PowerOn': {'Blade': {'Speed': 144}},
                           'WorkingMode': {'Color': [0, 0, 255], 'Flaming': 0, 'FlickeringAlways': 1},
                           'PowerOff': {'Blade': {'Speed': 144, 'MoveForward': 0}},
                           'Flaming': {'Size': {'Min': 2, 'Max': 9}, 'Speed': {'Min': 12, 'Max': 27},
                                       'Delay_ms': {'Min': 54, 'Max': 180},
                                       'Colors': []},
                           'Flickering': {'Time': {'Min': 90, 'Max': 360}, 'Brightness': {'Min': 50, 'Max': 100}},
                           'Blaster': {'Color': 'random', 'Duration_ms': 720, 'SizePix': 7},
                           'Clash': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 11},
                           'Stab': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 11},
                           'Lockup': {'Flicker': {'Color': [255, 0, 0], 'Time': {'Min': 45, 'Max': 80},
                                                  'Brightness': {'Min': 50, 'Max': 100}},
                                      'Flashes': {'Period': {'Min': 15, 'Max': 25}, 'Color': [255, 0, 0],
                                                  'Duration_ms': 50,
                                                  'SizePix': 7}},
                           'Blade2':{
                               'IndicateBlasterClashLockup': 1, 'DelayBeforeOn': 200,
                               'WorkingMode': {'Color': [0, 0, 255]},
                                'Flaming': {'AlwaysOn': 1, 'Size': {'Min': 2, 'Max': 9},
                                            'Speed': {'Min': 12, 'Max': 27},
                                            'Delay_ms': {'Min': 54, 'Max': 180},
                                            'Colors': []},
                                'Flickering': {'AlwaysOn': 1, 'Time': {'Min': 90, 'Max': 360},
                                               'Brightness': {'Min': 50, 'Max': 100}}}
        }

    def delete_profile(self, name: str):
        """
        deletes profile by key
        :param name: name of profile
        :return:
        """
        self.data.pop(name)

    def get_default(self, path: Sequence[str]) -> object:
        """
        gets default value for key path
        :param path: pat of keys
        :return: default value
        """
        data = default_profile
        for key in path:
            data = data[key]
        return data

    def get_value(self, path: Sequence[str], profile: str) -> object:
        """
        gets value of field configured with pat for profile
        :param path: path of keys
        :param profile: profile key
        :return: value
        """
        data = self.data[profile]
        for key in path:
            data = data[key]
        return data

    def update_value(self, path: Sequence[str], profile: str, value: object):
        """
        updates field for given keys in given profile, makes in given value
        :param path: key path
        :param profile: profile
        :param value: given new value
        :return:
        """
        try:
           data = self.data[profile]
           for key in path[:-1]:
                data = data[key]
           data[path[-1]] = value
        except (KeyError, IndexError):
            print("no such key or keypath is empty") # to do logging
        print(data)

    def save_color(self, path: Sequence[str], color: Sequence[int], profile: str):
        """
        saves color given as a list of rgb components to path in profiledata dict
        :param path: path of keys
        :param color: rgb components
        :param profile: current profile
        :return:
        """
        try:
            data = self.data[profile]
            for key in path[:-1]:
                data = data[key]
            data[path[-1]].append(color)
        except (IndexError, TypeError, ValueError):
            print ("wrong keypath or color data") # to do logging
        print(data)

    def get_colors(self, path: Sequence[str], profile: str)->Sequence[str]:
        """
        gets colors list for profile and path
        :param path: list of keys
        :param profile: current profile
        :return: list of colors
        """
        try:
            data = self.data[profile]
            for key in path:
                data = data[key]
            return data
        except (KeyError):
            print("Wrong keys used") #to do logging
            return None

    def delete_color(self, path: Sequence[int], color: Sequence[int], profile: str):
        """
        deletes color given as a list of rgb components from path in profiledata dict
        :param path: path of keys
        :param color: rgb components
        :param profile: current profile
        :return:
        """
        try:
            data = self.data[profile]
            for key in path[:-1]:
                data = data[key]
            data[path[-1]].remove(color)
        except (IndexError, TypeError, ValueError):
            print("wrong keypath or color data")  # to do logging
        print(data)

    def save_to_file(self, filename:str):
        """
        saves to filename as pseudo-json (no quotes)
        :param filename: name of file to save
        :return:
        """
        text = json.dumps(self.data)
        text = text.replace(r'"', "")
        text = text[1:-1]
        f = open(filename, "w")
        f.write(text)

