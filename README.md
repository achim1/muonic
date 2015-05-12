
muonic - a python gui for QNET experiments
================================================

The muonic project provides an interface to communicate with QuarkNet DAQ cards and to perform simple analysis of the generated data.
Its goal is to ensure easy and stable access to the QuarkNet cards and visualize some of the features of the cards. It is meant to be used in school projects, so it should be easy to use even by people who do not have lots LINUX backround or experience with scientific software. Automated data taking ensure no measured data is lost.

License and terms of agreement
----------------------------------

Muonic is distributed under the terms of GPL (GNU Public License). With the use of the software you accept the conditions of the GPL. This means also that the authors can not be made responsible for any damage of any kind to hard- or software.

muonic setup and installation
-----------------------------------

Muonic consists of two main parts:
1. the python package `muonic`
2. a python executable

###prerequisites

muonic needs the following packages to be installed (list may not be complete!)

* python-scipy
* python-matplotlib
* python-numpy
* python-qt4
* python-serial


###installation with the setup.py script

Run the following command in the directory where you checked out the source code:

`python setup.py install`

This will install the muonic package into your python site-packages directory and also the executuables `muonic` and `which_tty_daq` to your usr/bin directory. It also generates a new directory in your home dir: `$HOME/muonic_data`

The use of python-virtualenv is recommended.

###installing muonic without the setup script

You just need the script `./bin/muonic` to the upper directory and rename it to `muonic.py`.
You can do this by typing

`mv bin/muonic muonic.py`

while being in the muonic main directory.

Afterwards you have to create the folder `muonic_data` in your home directory.

`mkdir ~/muonic_data`


How to use muonic
========================

start muonic
------------

If you have setup muonic via the provided setup.py script or if you have put the package somewhere in your PYTHONPATH, simple call from the terminal

``muonic [OPTIONS] xy``

where ``xy`` are two characters which you can choose freely. You will find this two letters occurring in automatically generated files, so that you can identify them.

For help you can call

``muonic --help``

which gives you also an overview about the options::

    muonic

    [OPTIONS]

    -s
    use the simulation mode of muonic (no real data, so no physics behind!). This should only used for testing and developing the software

    -d
    debug mode. Use it to generate more log messages on the console.

    -t sec
    change the time window for the calculation of the rates. If you expect very low rates, you might consider to change it to larger values.
    default is 5 seconds.

    -p
    automatically write a file with pulse times in a non hexadecimal representation

    -n
    suppress any status messages in the output raw data file, might be useful if you want use muonic only for data taking and use another script afterwards for analysis.


Saving files with muonic
------------------------

All files which are saved by muonic are ASCII files. The filenames are as follows:

*currently all files are saved under $HOME/muonic_data. This directory must exist. If you use the provided setup script, it is created automatically*

`YYYY-MM-DD_HH-MM-SS_TYPE_MEASUREMENTTME_xy`

* `YYYY-MM-DD` is the date of the measurement start
* `HH-MM-SS` is the GMT time of the measurement start
* `MEASUREMENTTIME` if muonic is closed, each file gets is corresponding measurement time (in hours) assigned.
* `xy` the two letters which were specified at the start of muonic
* `TYPE` might be one of the following:
* `RAW` the raw ASCII output of the DAQ card, this is only saved if the 'Save to file' button in clicked in the 'Daq output' window of muonic
* `R` is an automatically saved ASCII file which contains the rate measurement data, this can then be used to plot with e.g. gnuplot later on
* `L` specifies a file with times of registered muon decays. This file is automatically saved if a muon decay measurement is started.
* `P` stands for a file which contains a non-hex representation of the registered pulses. This file is only save if the `-p` option is given at the start of muonic

Representation of the pulses:

`(69.15291364, [(0.0, 12.5)], [(2.5, 20.0)], [], [])`

This is a python-tuple which contains the trigger time of the event and four lists with more tuples. The lists represent the channels (0-3 from left to right) and each tuple stands for a leading and a falling edge of a registered pulse. To get the exact time of the pulse start, one has to add the pulse LE and FE times to the triggertime

_For calculation of the LE and FE pulse times a TMC is used. It seems that for some DAQs cards a TMC bin is 1.25 ns wide, although the documentation says something else.
   The trigger time is calculated using a CPLD which runs in some cards at 25MHz, which gives a bin width of the CPLD time of 40 ns.
   Please keep this limited precision in mind when adding CPLD and TMC times._


Performing measurements with muonic
-----------------------------------

###Setting up the DAQ

For DAQ setup it is recommended to use the 'settings' menu, although everything can also be setup via the command line in the DAQ output window (see below.)
Muonic translates the chosen settings to the corresponding DAQ commands and sends them to the DAQ. So if you want to change things like the coincidence time window, you have to issue the corresponding DAQ command in the DAQ output window.

Two menu items are of interest here:
* Channel Configuration: Enable the channels here and set coincidence settings. A veto channel can also be specified.

*You have to ensure that the check boxes for the channels you want to use are checked before you leave this dialogue, otherwise the channel gets deactivated.*

*The coincidence is realized by the DAQ in a way that no specific channels can be given. Instead this is meant as an 'any' condition.
   So 'twofold' means that 'any two of the enabled channels' must claim signal instead of two specific ones (like 1 and 2).*

*Measurements at DESY indicated that the veto feature of the DAQ card might not work properly in all cases.*

* Thresholds: For each channel a threshold (in milliVolts) can be specified. Pulse which are below this threshold are rejected. Use this for electronic noise supression. One can use for the calibration the rates in the muon rates tab.

**A proper calibration of the individual channels is the key to a successful measurement!**


###Muon Rates

In the first tab a plot of the measured muon rates is displayed. A trigger rate is only shown if a coincidence condition is set.
In the block on the right side of the tab, the average rates are displayed since the measurement start. Below you can find the number of counts for the individual channels. On the bottom right side is also the maximum rate of the measurement. The plot and the shown values can be reset by clicking on 'Restart'. The 'Stop' button can be used to temporarily hold the plot to have a better look at it.

*You can use the displayed 'max rate' at the right bottom to check if anything with the measurement went wrong.*

*Currently the plot shows only the last 200 seconds. If you want to have a longer time range, you can use the information which is automatically stored in the 'R' file (see above).*

###Muon Lifetime

A lifetime measurement of muons can be performed here. A histogram of time differences between succeeding pulses in the same channel is shown. It can be fit with an exponential by clicking on 'Fit!'. The fit lifetime is then shown in the above right of the plot, for an estimate on the errors you have to look at the console.

The measurement can be activated with the check box. In the following popup window the measurement has to be configured. It depends mainly on the detector you use and influences the quality of the measurement. The signal is accepted if more than one pulse appears in the single pulse channel or if one pulse appears in the single pulse channel and >= 2 pulses appear in the double pulse channel. The coincidence time is set to ?microseconds for this measurement. The signal are vetoed with the veto channel: only events are accepted if no pulse occurs there. If the self veto is activated it accepts only events if:
* more than one pulse appears in the single pulse channel and none pulse is measured in the double pulse channel
* one pulse in the single pulse channel appears and exactly two pulses in the double pulse channel.

**The error of the fit might be wrong!**

###Muon Velocity

In this tab the muon velocity can be measured. The measurement can be started with activating the check box. In the following popup window it has to be configured.

**The error of the fit might be wrong!**

###Pulse Analyzer

You can have a look at the pulse widths in this plot. The height of the pulses is lost during the digitization process, so all pulses have the same height here.
On the left side is an oscilloscope of the pulse widths shown and on the right side are the pulse widths collected in an histogram.

###GPS Output

In this tab you can read out the GPS information of the DAQ card. It requires a connected GPS antenna. The information are summarized on the bottom in a text box, from where they can be copied.

###Raw DAQ data

The last tab of muonic displays the raw ASCII DAQ data.
This can be saved to a file. If the DAQ status messages should be suppressed in that file, the option `-n` should be given at the start of muonic.
The edit field can be used to send messages to the DAQ. For an overview over the messages, look here (link not available yet!).
To issue such an command periodically, you can use the button 'Periodic Call'

_The two most important DAQ commands are 'CD' ('counter disable') and 'CE' ('counter enable'). Pulse information is only given out by the DAQ if the counter is set to enabled. All pulse related features may not work properly if the counter is set to disabled._

