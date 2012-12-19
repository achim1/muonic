#! /usr/bin/env python

from distutils.core import setup

import os
import shlex
import subprocess as sub

datapath = (os.getenv('HOME') + os.sep + 'muonic_data')

setup(name='muonic',
      version='1.0',
      description='Software to work with QNet DAQ cards',
      long_description='Software is able to manage DAQ comunications and shows e.g. a rate plot...',
      author='Robert Franke',
      url='http://code.google.com/p/muonic/',
      license="GPL",
      platforms=["Ubuntu 10.10"],
      keywords=["QNET","QuarkNET","Fermilab","DESY"],
      packages=['muonic','muonic.analysis','muonic.gui','muonic.daq'],
      scripts=['bin/muonic','bin/which_tty_daq'],
      package_data={'' : ['docs/*','README'], 'muonic': ['daq/simdaq.txt','daq/which_tty_daq']}, 
      data_files=[(datapath,[])]
      )

# setting correct permissions of created muonic_data dir

userid = os.stat(os.getenv("HOME"))[4]
cline = "chown -R " + str(userid) + ":" + str(userid) + " " + datapath
sub.Popen(shlex.split(cline),stdout=sub.PIPE).communicate()

