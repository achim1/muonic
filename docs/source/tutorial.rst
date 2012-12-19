How to use muonic
==================

start muonic
------------

If you have setup muonic via the provided setup.py script or if you hav put the package somewhere in your PYTHONPATH, simple call from the terminal

``muonic [OPTIONS] xy``

where ``xy`` are two characters which you can choose freely. You will find this two letters occuring in automatically generated files, so that you can identify them.

For help you can call

``muonic --help``

.. program:: muonic

[OPTIONS]

.. option:: -s
   use the simulation mode of muonic. This should only used for testing and developing the software

.. option:: -d
   debug mode. Use it to generate more log messages on the console.

.. option:: -t sec
   change the timewindow for the calculation of the rates. If you expect very low rates, you might consider to change it to larger values.
   default is 5 seconds.

.. option:: -p
   automatically write a file with pulsetimes in a non hexadecimal representation

.. option:: -n
   supress any status messages in the output raw data file, might be useful if you want use muonic only for data taking and use another script afterwards for analysis.


Saving files with muonic
------------------------

All files which are saved by muonic are ASCII files. The filenames are as follows:

.. warning::
   currently all files are saved under $HOME/muonic_data. This directory must exist. If you use the provided setup script, it is created automatically

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

This is a python-tuple which contains the triggertime of the event and four lists with more tuples. The lists represent the channels (0-3 from left to right) and each tuple stands for a leading and a falling edge of a registered pulse. To get the exact time of the pulse start, one has to add the pulse LE and FE times to the triggertime

.. note::
   For calculation of the LE and FE pulse times a TMC is used. It seems that for some DAQs cards a TMC bin is 1.25 ns wide, allthough the documentation says something else.
   The triggertime is calculated using a CPLD which runs in some cards at 25MHz, which gives a binwidth of the CPLD time of 40 ns.
   Please keep this limited precision in mind when adding CPLD and TMC times.

Performing measurements with muonic
-----------------------------------

Setting up the DAQ
~~~~~~~~~~~~~~~~~~

For DAQ setup it is recommended to use the 'settings' menu, allthough everything can also be setup via the command line in the DAQ output window (see below.)
Muonic translates the chosen settings to the corresponding DAQ commands and sends them to the DAQ. So if you want to change things like the coincidence time window, you have to issue the corresponding DAQ command in the DAQ output window.

Two menu items are of interest here:
* Channel Configuration: Enable the channels here and set coincidence settings. A veto channel can also be specified.

.. note::
   You have to ensure that the checkboxes for the channels you want to use are checked before you leave this dialogue, otherwise the channel gets deactivated.

.. note::
   The concidence is realized by the DAQ in a way that no specific channels can be given. Instead this is meant as an 'any' condition.
   So 'twofold' means that 'any two of the enabled channels' must claim signal instead of two specific ones (like 1 and 2).

.. warning::
   Measurements ad DESY indicated that the veto feature of the DAq might not work properly in all cases.

* Thresholds: For each channel a threshold (in milliVolts) can be specified. Pulse which are below this threshold are rejected. Use this for electronic noise supression.

.. note::
   A proper calibration of the individual channels is the key to a succesfull measurement!
 

Looking at raw DAQ data
~~~~~~~~~~~~~~~~~~~~~~~

The first tab of muonic displays the raw ASCII DAQ data.
This can be saved to a file. If the DAQ status messages should be supressed in that file, the option `-n` should be given at the start of muonic.
The edit field can be used to send messages to the DAQ. For an overview over the messages, look here (link not available yet!).
To issue such an command periodically, you can use the button 'Periodic Call'

.. note::
   The two most importand DAQ commands are 'CD' ('counter disable') and 'CE' ('counter enable'). Pulse information is only given out by the DAQ if the counter is set to enabled. All pulse related features may not work properly if the counter is set to disabled.

Muon Rates
~~~~~~~~~~

In this tab a plot of the measured muonrates is displayed. A triggerrate is only shown if a coincidence condition is set.
In the block on the left side of the tab the average rates are displayed since the measurement start. Below you can find the number of counts for the individual channels. The measurement can be reset by clicking on 'Restart'. The 'Stop' button can be used to temporarily hold the plot to have a better look at it. 

.. note:: You can use the displayed 'max rate' at the left bottom to check if anything with the measurement went wrong.

.. note:: Currently the plot shows only the last 200 seconds. If you want to have a longer timerange, you can use the information which is automatically stored in the 'R' file.(see above)

Muon Lifetime
~~~~~~~~~~~~~

A lifetime measurement of muons can be performed here. A histogram of time differences between succeding pulses in the same channel is shown. It can be fit with an exponential by clicking on 'Fit!'. The fit lifetime is then shown in the above right of the plot, for an estimate on the errors you have to look at the console.

.. warning::
   This feature might not work properly, especially when used with the standard scintilators! Use it with extreme care.

Pulse Analyzer
~~~~~~~~~~~~~~

You can have a look at the pulsewidhts in this plot. The height of the pulses is lost during the digitization prozess, so all pulses have the same height here.



