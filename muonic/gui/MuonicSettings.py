"""
Provides the settings and constants handling for muonic
"""
import os
import datetime
from ast import literal_eval

class MuonicConstants(object):
    """
    Class which holds the constants of Muonic. Ordered in dict with key is name, value is tuple with value[0] itself and unit (value[1])
    """
    def __init__(self):
        self.__consts = dict()
        self.__consts['c'] = (29979245000, 'cm/s')
        # for the pulses 
        # 8 bits give a hex number
        # but only the first 5 bits are used for the pulses time,
        # the fifth bit flags if the pulse is considered valid
        # the seventh bit should be the triggerflag...
        self.__consts['BIT0_4'] = (31,)
        self.__consts['BIT5'] = (1 << 5,)
        self.__consts['BIT7'] = (1 << 7,)
        # For DAQ status
        self.__consts['BIT0'] = (1,) # 1 PPS interrupt pending
        self.__consts['BIT1'] = (1 << 1,) # Trigger interrupt pending
        self.__consts['BIT2'] = (1 << 2,) # GPS data possible corrupted
        self.__consts['BIT3'] = (1 << 3,) # Current or last 1PPS rate not within range
        # ticksize of tmc internal clock
        # documentation says 0.75, measurement says 1.25
        # TODO: find out if tmc is coupled to cpld!
        self.__consts['TMC_TICK'] = (1.25, 'ns')
        self.__consts['MAX_TRIGGERWINDOW'] = (9960.0,'ns') # for mudecay!
        self.__consts['DEFAULT_FREQUENCY'] = (25.0e6,'Hz')
        self.__consts['PULSE_REGEX'] = "^([A-Z0-9]{8}) ([A-Z0-9]{2}) ([A-Z0-9]{2}) ([A-Z0-9]{2}) ([0-9A-Z]{2}) ([A-Z0-9]{2}) ([A-Z0-9]{2}) ([A-Z0-9]{2}) ([A-Z0-9]{2}) ([A-Z0-9]{8}) (\d{6})\.(\d{3}) (\d{6}) ([AV]{1}) (\d{2}) (\d{1}) [+-](\d{4})$"

    def keys(self):
        """
        Returns all keys
        """
        return self.__consts.keys()

    def values(self, key = None, unit = False):
        """
        Returns all values if key is None, returns a specific key if key is given, returning the full value tuple with value and unit can be activated with unit switch
        """
        if key is None:
            if unit:
                return self.__consts.values()
            pseudovals = list()
            for val in self.__consts.values():
                pseudovals.append(val[0])
            return pseudovals
        if unit:
            return self.__consts[key]
        return self.__consts[key][0]
    

class MuonicSettings(object):
    """
    Holds the settings, changes them, dumps them to a settings file if required, reads them from there if available
    """
    def __init__(self, logger, settings_file = ''):
        self.logger = logger
        # each dict value is a tuple holding the value and a bool, allowing the user to change it or not
        self._muonic_setting = dict()
        self._muonic_setting['muonic_filenames'] = ("%s_%s_HOURS_%s%s" ,True)
        self._muonic_setting['data_folder'] = ('muonic_data',True)
        self._muonic_setting['data_path'] = (os.getenv('HOME') + os.sep + self._muonic_setting['data_folder'][0], False)
        if not self.__check_create_folder(self._muonic_setting['data_path'][0]):
            self.logger.warning('The previous warning means it can not save muonic data! All Muonic data will be thrown away!')
            self._muonic_setting['data_path'] = os.devnull
        self._muonic_setting['doc_folder'] = ('docs', True)
        self._muonic_setting['doc_path'] = (os.getenv('HOME') + os.sep + self._muonic_setting['data_folder'][0] + os.sep + self._muonic_setting['doc_folder'][0] + os.sep + 'html',False)
        self._muonic_setting['status_line'] = (True, True)
        self._muonic_setting['time_window'] = (5.0, True)
        self._muonic_setting['widget_order'] = ({'Muon Rates':0,
                                        'Pulse Analyzer':1,
                                        'Muon Decay':2,
                                        'Muon Velocity':3,
                                        'Status':4,
                                        'DAQ Output':5}, True)
        self._muonic_setting['settings_path'] = (os.getenv('HOME') + os.sep + self._muonic_setting['data_folder'][0] + os.sep + '.muonicsettings',False)
        self._daq_setting = dict()
        self._daq_setting['channels'] = (4,False)
        self._daq_setting['threshold'] = ([300]*self._daq_setting['channels'][0],True)
        self._daq_setting['active_channel'] = ([True]*self._daq_setting['channels'][0],True)
        self._daq_setting['veto'] = ([False]*self._daq_setting['channels'][0],True)
        self._daq_setting['coincidence'] = ([False]*self._daq_setting['channels'][0],True)
        self._daq_setting['gatewidth'] = (100,True)
        self._daq_setting['setup_card'] = (False, False)
        if len(settings_file) > 0 and self.read_settings_file(settings_file):
            self._muonic_setting['settings_path'] = (settings_file,False)
        else:
            self.read_settings_file(self._muonic_setting['settings_path'][0])

    def __check_create_folder(self, path):
        """
        Checks whether a folder with the given path exists. If not is tries to create it.
        """
        if os.path.isdir(path):
            return True
        else:
            try:
                os.mkdir(path, 761)
            except OSError:
                self.logger.warning("Cannot create folder with the path: %s. Maybe because the permission was denied or it is an existing file." %str(path))
                return False
            return True

    def read_settings_file(self,settings_file):
        """
        Read the settingsfile
        """
        __settings_file = None
        try:
            __settings_file = open(settings_file, 'rU')
        except IOError:
            self.logger.warning("Cannot read settings from %s. Fallback to the default settings." %str(settings_file))
            __settings_file.close()
            return False
        for line in __settings_file:
            try:
                line = literal_eval(line)
            except SyntaxError:
                self.logger.warning("Cannot read setting ''%s'' from %s. Fallback to the default setting if existing." %(line,str(settings_file)))
            if str(line[0]) == 'DAQ' or str(line[0]) == 'daq':
                if self._daq_setting.has_key(line[1]):
                    self._daq_setting[line[1]] = (literal_eval(line[2][0]),bool(line[2][1]))
                else:
                    self.logger.debug("Adding yet unknown DAQ setting: %s with values: %s" %(line[1], str(line[2])))
                    self._daq_setting[line[1]] = (literal_eval(line[2][0]),bool(line[2][1]))
            elif str(line[0]) == 'MUONIC' or str(line[0]) == 'muonic':
                if self._muonic_setting.has_key(line[0]):
                    self._muonic_setting[line[1]] = (literal_eval(line[2][0]),bool(line[2][1]))
                else:
                    self.logger.debug("Adding yet unknown MUONIC setting: %s with values: %s" %(line[1], str(line[2])))
                    self._muonic_setting[line[1]] = (literal_eval(line[2][0]),bool(line[2][1]))
            else:
                self.logger.warning("Cannot literal_evaluate a setting from ''%s'' in %s." %(line,str(settings_file)))
        __settings_file.close()
        return True

    def daq_setting(self, key = None, value = None):
        """
        returns the daq setting named key, or overwrites it if value given
        """
        if value is None:
            return self.__read_settings(False, key)
        return self.__write_settings(True, key, value)

    def muonic_setting(self, key = None, value = None):
        """
        returns the muonic setting named key, or overwrites it if value given
        """
        if value is None:
            return self.__read_settings(False, key)
        return self.__write_settings(True, key, value)

    def __read_settings(self, daq_check, key):
        pseudoreturn = False
        __insetting = None
        if daq_check:
            __insetting = self._daq_setting
        else:
            __insetting = self._muonic_setting
        if key is None:
            for key, value in __insetting:
                pseudoreturn[key] = value[0]
        else:
            if __insetting.has_key(key):
                pseudoreturn = __insetting[key][0]
            else:
                self.logger.warning("Asked for unknown setting ''%s''." %key)
                pseudoreturn = False
        return pseudoreturn

    def __write_settings(self, daq_check, key, value):
        if isinstance(value, dict):
            for keys, vals in value.iteritems():
                if not isinstance(key, str) or not isinstance(vals, tuple):
                    self.logger.debug("Invalid setting given. was not written.")
                    continue
                if daq_check:
                    if not self._daq_setting.has_key(keys):
                        self.logger.debug("Adding new DAQ setting: %s with %s"%(keys, vals))
                    self._daq_setting[keys] = (vals[0],bool(vals[1]))
                else:
                    if not self._muonic_setting.has_key(keys):
                        self.logger.debug("Adding new MUONIC setting: %s with %s"%(keys, vals))
                    self._muonic_setting[keys] = (vals[0],bool(vals[1]))
            return True
        else:
            if not isinstance(value, tuple):
                self.logger.debug("Invalid value for setting given. Not written.")
                return False
            if daq_check:
                if not self._daq_setting.has_key(key):
                    self.logger.debug("Adding new DAQ setting: %s with %s"%(key, value))
                self._daq_setting[key] = (value[0],bool(value[1]))
            else:
                if not self._muonic_setting.has_key(key):
                    self.logger.debug("Adding new MUONIC setting: %s with %s"%(key, value))
                self._muonic_setting[key] = (value[0],bool(value[1]))
        return False

    def write_settings_file(self):
        """
        Writes the settings into a settings file
        """
# TODO: writes complete settings back, change to: reads and rewrites only changed settings
        __settings_file = None
        try:
            __settings_file = open(self._muonic_setting['settings_path'][0], 'w')
        except IOError:
            self.logger.warning("Cannot write settings to %s!" %str(self._muonic_setting['settings_path'][0]))
            __settings_file.close()
            return False
        for key, value in self._daq_setting.iteritems():
            if not isinstance(value[0], int) and not isinstance(value[0], tuple) and not isinstance(value[0], list) and not isinstance(value[0], dict) and not isinstance(value[0], bool) and not isinstance(value[0], float) and not value[0] is None:
                __writeback = ('DAQ',str(key),(str('\''+value[0]+'\''),bool(value[1])))
            else:
                __writeback = ('DAQ',str(key),(str(value[0]),bool(value[1])))
            __settings_file.write(str(__writeback)+"\n")
        for key, value in self._muonic_setting.iteritems():
            if not isinstance(value[0], int) and not isinstance(value[0], tuple) and not isinstance(value[0], list) and not isinstance(value[0], dict) and not isinstance(value[0], bool) and not isinstance(value[0], float) and not value[0] is None:
                __writeback = ('DAQ',str(key),(str('\''+value[0]+'\''),bool(value[1])))
            else:
                __writeback = ('MUONIC',str(key),(str(value[0]),bool(value[1])))
            __settings_file.write(str(__writeback)+"\n")
        __settings_file.close()
        return True

    def __del__(self):
        self.write_settings_file()
