"""
Provides the data and file handling for muonic
"""
import os
import datetime
import shutil

class MuonicFile(object):
    """
    Defines the basic file class for muonic. Use ''MuonicFile.muonic_file'' to access the file properties. 
    """

    def __init__(self, mfile, mode = 'r'):
        if not isinstance(mfile, str):
            raise ValueError, "Wrong file name / path"
        self.muonic_file_name = mfile
        self._mode = 'r'
        self.mode(mode)
        self.muonic_file = file(self.muonic_file_name, self._mode)
        self.datapath = os.getenv('HOME')+os.sep+'muonic_data'
    
    def muonic_file(self):
        """
        access the file properties, inherits from file
        """
        return self.muonic_file

    def muonic_file_name(self):
        """
        returns the file name
        """
        return self.muonic_file_name

    def mode(self, mode = None):
        """
        Access the file mode: if a value for the mode is given it overwrites the exisiting mode flag, else it returns the mode flag.
        """
        if mode is not None:
            mode = str(mode)            
            if mode in ['r', 'rw', 'a', 'r+', 'w+', 'a+', 'rb', 'rwb', 'ab', 'r+b', 'w+b', 'a+b']:
                self._mode = mode
            else:
                raise ValueError, "Unsupported file mode: %s" % mode
        return self._mode

    def comment_file(self, comment = ''):
        """
        Writes a comment about the measurment run start with date and time
        """
        if not self._mode in ['rw', 'a', 'w+', 'a+', 'rwb', 'ab', 'w+b', 'a+b']:
            raise IOError, "File not writeable!"
        if not isinstance(comment, str):
            raise ValueError, "Comment is not a valid string!"
        self.muonic_file.write(comment.strip())
        return True
    
    def flush(self):
        """
        Shortform of flush
        """
        self.muonic_file.flush()
        os.fsync(self.muonic_file)
        return True

    def __del__(self):
        if not self.muonic_file.closed:
            self.muonic_file.flush()
            os.fsync(self.muonic_file)
            self.muonic_file.close()
        del self.muonic_file
        del self._mode
        print "Successfully closed the file: %s" % self.muonic_file_name
        del self.muonic_file_name

class MuonicRateFile(MuonicFile):
    """
    Class which holds rate files. Contains rates in the format:

    """
    def __init__(self, filename, logger, mode = 'a'):
        self.filename = str(filename)
        self.logger = logger
        self._rate_mes_start = datetime.datetime.now()
        MuonicFile.__init__(self,self.filename, mode)

    def start_run(self, measurement = 'rate'):
        """
        Writes a comment about the measurment run start with date and time
        """
        date = datetime.now()        
        __comment_file = '# new %s measurement run from: %i-%i-%i %i-%i-%i\n' %(measurement, date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def stop_run(self):
        """
        Writes a comment about the measurment run stop with date and time
        """
        date = datetime.now()
        __comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def write(self, msg):
        """
        Replace the default write method
        """
        if msg is None:
            raise ValueError, "Missing something to write to the file."
        self.muonic_file.write(str(msg)+'\n')
        return True

    def close(self):
        """
        Closes the file and moves it to its proper place.
        """
        self.flush()
        self.muonic_file.close()
        __mtime = datetime.datetime.now() - self._rate_mes_start
        __mtime = round(__mtime.seconds/(3600.),2) + __mtime.days*86400
        self.logger.info("The rate measurement was active for %f hours" % __mtime)
        _newratefilename = self.filename.replace("HOURS",str(__mtime))
        shutil.move(self.filename,_newratefilename)
        return True


class MuonicPulseFile(MuonicFile):
    """
    Class which holds pulse files. Contains pulses in the format:
    lasttriggertime,pulses["ch0"],pulses["ch1"],pulses["ch2"],pulses["ch3"]
    """
    def __init__(self, filename, logger, mode = 'a'):
        self.filename = str(filename)
        self.logger = logger
        self._pulse_mes_start = datetime.datetime.now()
        MuonicFile.__init__(self,self.filename, mode)

    def start_run(self, measurement = 'rate'):
        """
        Writes a comment about the measurment run start with date and time
        """
        date = datetime.now()        
        __comment_file = '# new %s measurement run from: %i-%i-%i %i-%i-%i\n' %(measurement, date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def stop_run(self):
        """
        Writes a comment about the measurment run stop with date and time
        """
        date = datetime.now()
        __comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def write(self, msg):
        """
        Replace the default write method. The expected type of msg is a tuple with the content:
        (lasttriggertime,pulses["ch0"],pulses["ch1"],pulses["ch2"],pulses["ch3"])
        """
        if msg is None or not isinstance(msg, tuple):
            raise ValueError, "Missing something valid to write to the file."
        self.muonic_file.write(str(msg.__repr__())+'\n')
        return True

    def close(self):
        """
        Closes the file and moves it to its proper place.
        """
        self.flush()
        self.muonic_file.close()
        __mtime = datetime.datetime.now() - self._pulse_mes_start
        __mtime = round(__mtime.seconds/(3600.),2) + __mtime.days*86400
        self.logger.info("The rate measurement was active for %f hours" % __mtime)
        _newfilename = self.filename.replace("HOURS",str(__mtime))
        shutil.move(self.filename,_newfilename)
        return True


class MuonicVelocityFile(MuonicFile):
    """
    Class which holds velocity files. Contains dt values in ns in the format:

    """
    def __init__(self, filename, mode = 'r'):
        self.filename = filename
        # magic file renaming here
        MuonicFile.__init__(self.filename, mode)
    def close(self):
        # magic close moves here
        pass


class MuonicDecayFile(MuonicFile):
    """
    Class which holds decay measurment files. Decay dts in the format:

    """
    def __init__(self, filename, logger, mode = 'a'):
        self.filename = str(filename)
        self.logger = logger
        self._pulse_mes_start = datetime.datetime.now()
        MuonicFile.__init__(self,self.filename, mode)

    def start_run(self, measurement = 'rate'):
        """
        Writes a comment about the measurment run start with date and time
        """
        date = datetime.now()        
        __comment_file = '# new %s measurement run from: %i-%i-%i %i-%i-%i\n' %(measurement, date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def stop_run(self):
        """
        Writes a comment about the measurment run stop with date and time
        """
        date = datetime.now()
        __comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def write(self, msg):
        """
        Replace the default write method
        """
        if msg is None or len(msg) < 2:
            raise ValueError, "Missing something to write to the file."
        __msg = 'Decay ' + muondecay[1].replace(' ','_').__repr__() + ' ' + muondecay[0].__repr__()
        self.muonic_file.write(str(__msg)+'\n')
        return True

    def close(self):
        """
        Closes the file and moves it to its proper place.
        """
        self.flush()
        self.muonic_file.close()
        __mtime = datetime.datetime.now() - self._pulse_mes_start
        __mtime = round(__mtime.seconds/(3600.),2) + __mtime.days*86400
        self.logger.info("The rate measurement was active for %f hours" % __mtime)
        _newfilename = self.filename.replace("HOURS",str(__mtime))
        shutil.move(self.filename,_newfilename)
        return True


class MuonicRawFile(MuonicFile):
    """
    Class which holds raw data files. Raw data stream saved in the format:

    """
    def __init__(self, filename, logger, mode = 'a'):
        self.filename = str(filename)
        self.logger = logger
        self._pulse_mes_start = datetime.datetime.now()
        MuonicFile.__init__(self,self.filename, mode)

    def start_run(self, measurement = 'rate'):
        """
        Writes a comment about the measurment run start with date and time
        """
        date = datetime.now()        
        __comment_file = '# new %s measurement run from: %i-%i-%i %i-%i-%i\n' %(measurement, date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def stop_run(self):
        """
        Writes a comment about the measurment run stop with date and time
        """
        date = datetime.now()
        __comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def write(self, msg, nostatus = False):
        """
        Replace the default write method
        """
        if msg is None:
            raise ValueError, "Missing something to write to the file."
        if nostatus:
            fields = msg.rstrip("\n").split(" ")
            if ((len(fields) == 16) and (len(fields[0]) == 8)):
                self.muonic_file.write(str(msg)+'\n')
            else:
                self.logger.debug("Not writing line '%s' to file because it does not contain trigger data" %msg)
        else:
            self.muonic_file.write(str(msg)+'\n')
        return True

    def close(self):
        """
        Closes the file and moves it to its proper place.
        """
        self.flush()
        self.muonic_file.close()
        __mtime = datetime.datetime.now() - self._pulse_mes_start
        __mtime = round(__mtime.seconds/(3600.),2) + __mtime.days*86400
        self.logger.info("The rate measurement was active for %f hours" % __mtime)
        _newfilename = self.filename.replace("HOURS",str(__mtime))
        shutil.move(self.filename,_newfilename)
        return True
