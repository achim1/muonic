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
        self.muonic_file = file.open(self.mfile_name, self._mode)

    def mode(self, mode = None):
        """
        Access the file mode: if a value for the mode is given it overwrites the exisiting mode flag, else it returns the mode flag.
        """
        mode = str(mode)
        if not mode is None:
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
        if not comment != '' or isinstance(comment, str):
            raise ValueError, "Comment is not a valid string!"
        self.muonic_file.write(comment.strip())

    def __del__(self):
        self.muonic_file.flush()
        os.fsync(self.muonic_file)
        if not self.muonic_file.closed():
            self.muonic_file.close()
        del self.muonic_file
        del self._mode
        print "Successfully closed the file: %s" % self.muonic_file_name
        del self.muonic_file_name
        del self.logger

class MuonicRateFile(MuonicFile):
    """
    Class which holds rate files. Contains rates in the format:

    """
    def __init__(self, filename, mode = 'a', logger):
        self.filename = filename
        self.logger = logger
        self._rate_mes_start = datetime.datetime.now()
        # magic file renaming here
        MuonicFile.__init__(self.filename, mode)

    def start_run(self, measurement = 'rate'):
        """
        Writes a comment about the measurment run start with date and time
        """
        date = datetime.now()        
        __comment_file = '# new %s measurement run from: %i-%i-%i %i-%i-%i\n' %(measurement, date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def stop_run(self)
        """
        Writes a comment about the measurment run stop with date and time
        """
        date = datetime.now()
        __comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def close(self)
        """
        Closes the file and moves it to its proper place.
        """
        self.close()
        __mtime = datetime.datetime.now() - self._rate_mes_start
        __mtime = round(__mtime.seconds/(3600.),2) + __mtime.days*86400
        self.logger.info("The rate measurement was active for %f hours" % __mtime)
        _newratefilename = self.filename.replace("HOURS",str(__mtime))
        shutil.move(self.filename,_newratefilename)


class MuonicPulseFile(MuonicFile):
    """
    Class which holds pulse files. Contains pulses in the format:

    """
    def __init__(self, filename, mode = 'r'):
        self.filename = filename
        # magic file renaming here
        MuonicFile.__init__(self.filename, mode)
    def close(self)
        # magic close moves here
        pass

class MuonicVelocityFile(MuonicFile):
    """
    Class which holds velocity files. Contains dt values in ns in the format:

    """
    def __init__(self, filename, mode = 'r'):
        self.filename = filename
        # magic file renaming here
        MuonicFile.__init__(self.filename, mode)
    def close(self)
        # magic close moves here
        pass

class MuonicDecayFile(MuonicFile):
    """
    Class which holds decay measurment files. Decay dts in the format:

    """
    def __init__(self, filename, mode = 'r'):
        self.filename = filename
        # magic file renaming here
        MuonicFile.__init__(self.filename, mode)
    def close(self)
        # magic close moves here
        pass

class MuonicRawFile(MuonicFile):
    """
    Class which holds raw data files. Raw data stream saved in the format:

    """
    def __init__(self, filename, mode = 'r'):
        self.filename = filename
        # magic file renaming here
        MuonicFile.__init__(self.filename, mode)
    def close(self)
        # magic close moves here
        pass
