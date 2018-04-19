#!/usr/bin/python
'''Routines for manipulating the TouchBar'''

import os
import subprocess

# pylint: disable=E0611
from Foundation import NSURL
from Foundation import CFPreferencesAppSynchronize
from Foundation import CFPreferencesCopyAppValue
from Foundation import CFPreferencesSetAppValue
# pylint: enable=E0611


class TouchBarError(Exception):
    '''Basic exception'''
    pass


class TouchBar():
    '''Class to handle TouchBar operations'''
    _DOMAIN = 'com.apple.controlstrip'
    _TOUCHBAR_PLIST = os.path.expanduser('~/Library/Preferences/com.apple.controlstrip.plist')
    _SECTIONS = ['FullCustomized', 'MiniCustomized']
    items = {}
    default_settings = {
        'FullCustomized': (
            "com.apple.system.group.brightness",
            "com.apple.system.mission-control",
            "com.apple.system.launchpad",
            "com.apple.system.group.keyboard-brightness",
            "com.apple.system.group.media",
            "com.apple.system.group.volume",
            "com.apple.system.siri",
        ),
        'MiniCustomized': (
            "com.apple.system.brightness",
            "com.apple.system.volume",
            "com.apple.system.mute",
            "com.apple.system.siri",
        ),
    }


    def __init__(self):
        for key in self._SECTIONS:
            try:
                section = CFPreferencesCopyAppValue(key, self._DOMAIN)
                self.items[key] = section.mutableCopy()
            except AttributeError:
                self.items[key] = self.default_settings[key]
            except Exception:
                raise


    def isDefault(self):
        return bool(self.items == self.default_settings)


    def save(self):
        '''saves our (modified) TouchBar preferences'''

        for key in self._SECTIONS:
            try:
                CFPreferencesSetAppValue(key,
                                         self.items[key],
                                         self._DOMAIN)
            except Exception:
                raise TouchBarError
        if not CFPreferencesAppSynchronize(self._DOMAIN):
            raise TouchBarError

        # restart the TouchBar
        subprocess.call(['/usr/bin/killall', 'ControlStrip'])


    def findExistingItem(self, test_identifier, section='FullCustomized'):
        '''returns index of item with identifier matching test_identifier
            or -1 if not found'''
        for index in range(len(self.items[section])):
            if (self.items[section][index] == test_identifier):
                return index
        return -1


    def addItem(self, identifier, section='FullCustomized', index=None):
        '''Adds a TouchBar item with the specified identifier.'''
        found_index = self.findExistingItem(identifier, section=section)
        if found_index == -1:
            if index:
                self.items[section].insert(index, identifier)
            else:
                self.items[section].append(identifier)


    def removeItem(self, identifier, section=None):
        '''Removes a TouchBar item with matching identifier, if any'''
        if section:
            sections = [section]
        else:
            sections = self._SECTIONS
        for section in sections:
            found_index = self.findExistingItem(identifier, section=section)
            if found_index > -1:
                del self.items[section][found_index]


    def replaceItem(self, old_identifier, new_identifier, section='FullCustomized'):
        '''Replaces a TouchBar item. The new item replaces an item with the given
        identifier'''
        found_index = self.findExistingItem(old_identifier, section=section)
        if found_index > -1:
            self.items[section][found_index] = new_identifier
