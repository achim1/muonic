muonic package software reference
====================================

.. default-domain:: py

main package: muonic
----------------------
.. automodule:: muonic
   :members:
   :undoc-members:
   :private-members:

   :mod:`muonic.daq`
   :mod:`muonic.gui`
   :mod:`muonic.analysis`

daq i/o with muonic.daq
-----------------------

.. automodule:: muonic.daq
   :members:
   :undoc-members:
   :private-members:

.. currentmodule:: muonic.daq
   .. automethod:: __Init__ 

`muonic.daq.DAQProvider`
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Control the two I/O threads which communicate with the DAQ. If the simulated DAQ is used, there is only one thread.

.. automodule:: muonic.daq.DAQProvider
   :members:
   :undoc-members:
   :private-members:

   .. automethod:: __init__

`muonic.daq.DAQConnection`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module provides a class which uses python-serial to open a connection over the usb ports to the daq card. Since on LINUX systems the used usb device ( which is usually /dev/tty0 ) might change during runtime, this is catched automatically by DaqConnection. Therefore a shell script is invoked.

.. automodule:: muonic.daq.DaqConnection
   :members:
   :undoc-members:
   :private-members:


`muonic.daq.SimDaqConnection`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module provides a dummy class which simulates DAQ I/O which is read from the file "simdaq.txt".
The simulation is only useful if the software-gui should be tested, but no DAQ card is available

.. automodule:: muonic.daq.SimDaqConnection
   :members:
   :undoc-members:
   :private-members:

pyqt4 gui with muonic.gui
-------------------------

This package contains all gui relevant classes like dialogboxes and tabwidgets. Every item in the global menu is utilizes a "Dialog" class. The "Canvas" classes contain plot routines for displaying measurements in the TabWidget.


.. automodule:: muonic.gui
   :members:

`muonic.gui.MainWindow`
~~~~~~~~~~~~~~~~~~~~~~~~

Contains the  "main" gui application. It Provides the MainWindow, which initializes the different tabs and draws a menu. 


.. automodule:: muonic.gui.MainWindow
   :members:
   :undoc-members:
   :private-members:

`muonic.gui.TabWidget`
~~~~~~~~~~~~~~~~~~~~~~~~~

This provides the interface to the different "physics" features of muonic, like a rate plot or a pulse display.

.. automodule:: muonic.gui.TabWidget
   :members:
   :undoc-members:
   :private-members:


`muonic.gui.MuonicDialogs`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: muonic.gui.MuonicDialogs
   :members:
   :undoc-members:
   :private-members:

`muonic.gui.MuonicPlotCanvases`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: muonic.gui.MuonicPlotCanvases
   :members:
   :undoc-members:
   :private-members:




analyis package muonic.analysis
-------------------------------

.. automodule:: muonic.analysis
   :members:


`muonic.analysis.PulseAnalyzer`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transformation of ASCII DAQ data. Combination of Pulses to events, and looking for decaying muons with different trigger condi

.. automodule:: muonic.analysis.PulseAnalyzer
   :members:
   :undoc-members:
   :private-members:

`muonic.analysis.fit`
~~~~~~~~~~~~~~~~~~~~~~~~~

Provide a fitting routine

.. automodule:: muonic.analysis.fit
   :members:
   :undoc-members:
   :private-members:


