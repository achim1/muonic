#! /usr/bin/env python

#from distutils.core import setup
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os
import shlex
import subprocess as sub
from glob import glob

# build the documentation
#man_make  = "make man -C docs"
#html_make = "make html -C docs"

#man_success  = sub.Popen(shlex.split(man_make),stdout=sub.PIPE).communicate()
#html_success = sub.Popen(shlex.split(html_make),stdout=sub.PIPE).communicate()

datapath = (os.getenv('HOME') + os.sep + 'muonic_data')

setup(name='muonic',
      version='1.1.0',
      description='Software to work with QNet DAQ cards',
      long_description='Software is able to manage DAQ comunications and shows e.g. a rate plot...',
      author='Robert Franke,Achim Stoessl',
      author_email="achim.stoessl@desy.de",
      url='http://code.google.com/p/muonic/',
      download_url="http://muonic.googlecode.com/files/muonic_1.0.tar.gz",
      # can only be used with setuptools
      #install_requires=['numpy','scipy','pyserial','matplotlib','PyQt'],
      license="GPL",
      platforms=["Ubuntu 10.10"],
      classifiers=[
          "License :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Development Status :: Beta",
          "Intended Audience :: Developers :: Students :: Physicists :: Teachers ",
          "Topic :: Cosmic Ray Physics",
      ],
      keywords=["QNET","QuarkNET","Fermilab","DESY","DAQ"],
      packages=['muonic','muonic.analysis','muonic.gui','muonic.daq'],
      scripts=['bin/muonic','bin/which_tty_daq'],
      package_data={'muonic': ['daq/simdaq.txt'],'':['*.txt','*.rst']}, 
      #package_data={'' : ['docs/*','README'], 'muonic': ['daq/simdaq.txt','daq/which_tty_daq']}, 
      data_files=[(datapath,[]),(datapath,["docs/build/man/muonic.1"]),(os.path.join(datapath,"docs/html"),glob("docs/build/html/*html")),(os.path.join(datapath,"docs/html/_static"),glob("docs/build/html/_static/*")),(os.path.join(datapath,"docs/html/_modules"),glob("docs/build/html/_modules/*html")),(os.path.join(datapath,"docs/html/_sources"),glob("docs/build/html/_sources/*html")),(os.path.join(datapath,"docs/html/_modules/muonic/"), glob("docs/build/html/_modules/muonic/*html")),(os.path.join(datapath,"docs/html/_modules/muonic/gui"),glob("docs/build/html/_modules/muonic/*html")),(os.path.join(datapath,"docs/html/_modules/muonic/daq"),glob("docs/build/html/_modules/muonic/daq/*html")),(os.path.join(datapath,"docs/html/_modules/muonic/analysis"), glob("docs/build/html/_modules/muonic/analysis/*html"))])

# setting correct permissions of created muonic_data dir

userid = os.stat(os.getenv("HOME"))[4]
cline = "chown -R " + str(userid) + ":" + str(userid) + " " + datapath

chown_success = sub.Popen(shlex.split(cline),stdout=sub.PIPE).communicate()

#print man_success[0]
#print html_success[0]
#if chown_success[1] is None:
#    print "Successfully changed owner of %s to %s" %(datapath,str(userid))
#    print "---------------------------"
#
#if man_success[1] is None:
#    print "Built manpages succesfully"
#    print "---------------------------"
#if html_success[1] is None:
#    print "Buitl html docs succesfully"
#    print "---------------------------"
#
#print "MUONIC succesfully installed!"

