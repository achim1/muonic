Fermilab DAQ - hardware documentation
======================================

ASCII DAQ output format
--------------------------

sample line of DAQ output - example for the daq data format

========== ==== ==== ==== ==== ==== ==== ==== ==== ========== ============ ======== ============== =============== ===== =============
triggers   r0   f0   r1   f1   r2   f2   r3   f3    onepps      gpstime    gpsdte   gps-valid      gps-satelites   xx     correction
========== ==== ==== ==== ==== ==== ==== ==== ==== ========== ============ ======== ============== =============== ===== =============
92328FE2   00   3D   00   3E   00   00   00   00   915E10CF   034016.021   060180   V              00                0      +0055
========== ==== ==== ==== ==== ==== ==== ==== ==== ========== ============ ======== ============== =============== ===== =============

DAQ onboard documentation
-----------------------------

Online help on the DAQ cards is available by sending the following commands to the DAQ

* V1, V2, V3
* H1,H2



V1
~~~

+-----------------+-----------------+---------------------------------------------------+
| Setting         |  example value  |  description                                      |
+=================+=================+===================================================+
| Run Mode        |    Off          |  CE (cnt enable), CD (cnt disable )               |
+-----------------+-----------------+---------------------------------------------------+
| Ch(s) Enabled   |    3,2,1,0      |  Cmd DC  Reg C0 using (bits 3-0)                  |
+-----------------+-----------------+---------------------------------------------------+
| Veto Enable     |    Off          |  VE 0 (Off),  VE 1 (On)                           |
+-----------------+-----------------+---------------------------------------------------+
| Veto Select     |    Ch0          |  Cmd DC  Reg C0 using (bits 7,6)                  |
+-----------------+-----------------+---------------------------------------------------+
| Coincidence 1-4 |    1-Fold       |  Cmd DC  Reg C0 using (bits 5,4)                  |
+-----------------+-----------------+---------------------------------------------------+
| Pipe Line Delay |       40 nS     |  Cmd DT  Reg T1=rDelay  Reg T2=wDelay  10nS/cnt   |
+-----------------+-----------------+---------------------------------------------------+
| Gate Width      |      100 nS     |  Cmd DC  Reg C2=LowByte Reg C3=HighByte 10nS/cnt  |
+-----------------+-----------------+---------------------------------------------------+
| Veto Width      |        0 nS     |  Cmd VG  (10nS/cnt)                               |
+-----------------+-----------------+---------------------------------------------------+
| Ch0 Threshold   |    0.200 vlts   |                                                   |
| Ch1 Threshold   |    0.200 vlts   |                                                   |
| Ch2 Threshold   |    0.200 vlts   |                                                   |
| Ch3 Threshold   |    0.200 vlts   |                                                   |
+-----------------+-----------------+---------------------------------------------------+
| Test Pulser Vlt |    3.000 vlts   |                                                   |
| Test Pulse Ena  |    Off          |                                                   |
+-----------------+-----------------+---------------------------------------------------+


Example line for 1 of 4 channels. (Line Drawing, Not to Scale)
Input Pulse edges (begin/end) set rising/falling tags bits.
____~~~~~~_________________________________ Input Pulse, Gate cycle begins
__________________~________________________ Delayed Rise Edge 'RE' Tag Bit
________________________~__________________ Delayed Fall Edge 'FE' Tag Bit
_____________                           Tag Bits delayed by PipeLnDly
___|        |_________________________ PipeLineDelay :   40nS
_____________________
_________________|                     |___ Capture Window:   60nS
___________________________________
___|                                   |___ Gate Width    :  100nS

If 'RE','FE' are outside Capture Window, data tag bit(s) will be missing.
CaptureWindow = GateWidth - PipeLineDelay
The default Pipe Line Delay is 40nS, default Gate Width is 100nS.
Setup CMD sequence for Pipeline Delay.  CD,  WT 1 0, WT 2 nn (10nS/cnt)
Setup CMD sequence for Gate Width.  CD, WC 2 nn(10nS/cnt), WC 3 nn (2.56uS/cnt)


H2

Barometer      Qnet Help Page 2
BA      - Display Barometer trim setting in mVolts and pressure as mBar.
BA d    - Calibrate Barometer by adj. trim DAC ch in mVlts (0-4095mV).
Flash
FL p    - Load Flash with Altera binary file(*.rbf), p=password.
FR      - Read FPGA setup flash, display sumcheck.
FMR p   - Read page 0-3FF(h), (264 bytes/page)
Page 100h= start fpga *.rbf file, page 0=saved setup.
GPS
NA 0    - Append NMEA GPS data Off,(include 1pps data).
NA 1    - Append NMEA GPS data On, (Adds GPS to output).
NA 2    - Append NMEA GPS data Off,(no 1pps data).
NM 0    - NMEA GPS display, Off, (default), GPS port speed 38400, locked.
NM 1    - NMEA GPS display (RMC + GGA + GSV) data.
NM 2    - NMEA GPS display (ALL) data, use with GPS display applications.
Test Pulser
TE m    - Enable run mode,  0=Off, 1=One cycle, 2=Continuous.
TD m    - Load sample trigger data list, 0=Reset, 1=Singles, 2=Majority.
TV m    - Voltage level at pulse DAC, 0-4095mV, TV=read.
Serial #
SN p n  - Store serial # to flash, p=password, n=(0-65535 BCD).
SN      - Display serial number (BCD).
Status
ST      - Send status line now.  This resets the minute timer.
ST 0    - Status line, disabled.
ST 1 m  - Send status line every (m) minutes.(m=1-30, def=5).
ST 2 m  - Include scalar data line, chs S0-S4 after each status line.
ST 3 m  - Include scalar data line, plus reset counters on each timeout.
TI n     - Timer (day hr:min:sec.msec), TI=display time, (TI n=0 clear).
U1 n     - Display Uart error counter, (U1 n=0 to zero counters).
VM 1     - View mode, 0x80=Event_Demarcation_Bit outputs a blank line.
- View mode returns to normal after 'CD','CE','ST' or 'RE'.


H1
Quarknet Scintillator Card,  Qnet2.5  Vers 1.11  Compiled Jul 15 2009  HE=Help
Serial#=6531     uC_Volts=3.33      GPS_TempC=0.0     mBar=1023.8

CE     - TMC Counter Enable.
CD     - TMC Counter Disable.
DC     - Display Control Registers, (C0-C3).
WC a d - Write   Control Registers, addr(0-6) data byte(H).
DT     - Display TMC Reg, 0-3, (1=PipeLineDelayRd, 2=PipeLineDelayWr).
WT a d - Write   TMC Reg, addr(1,2) data byte(H), if a=4 write delay word.
DG     - Display GPS Info, Date, Time, Position and Status.
DS     - Display Scalar, channel(S0-S3), trigger(S4), time(S5).
RE     - Reset complete board to power up defaults.
RB     - Reset only the TMC and Counters.
SB p d - Set Baud,password, 1=19K, 2=38K, 3=57K ,4=115K, 5=230K, 6=460K, 7=920K
SA n   - Save setup, 0=(TMC disable), 1=(TMC enable), 2=(Restore Defaults).
TH     - Thermometer data display (@ GPS), -40 to 99 degrees C.
TL c d - Threshold Level, signal ch(0-3)(4=setAll), data(0-4095mV), TL=read.
Veto   - Veto select, Off='VE 0', On='VE 1', Gate='VG c', 0-255(D) 10ns/cnt.
View   - View setup registers. Setup=V1, Voltages(V2), GPS LOCK(V3).
HELP   - HE,H1=Page1, H2=Page2, HB=Barometer, HS=Status, HT=Trigger.


VE2
V2
Barometer Pressure Sensor
Calibration Voltage  = 1495 mVolts   Use Cmd 'BA' to calibrate.
Sensor Output Voltage= 1655 mVolts   (2.93mV *  565 Cnts)
Pressure mBar        = 1023.6        (1655.5 - 1500)/15 + 1013.25
Pressure inch        = 30.63         (mBar / 33.42)

Timer Capture/Compare Channel
TempC  = 0.0     Error?  Check sensor cable connection at GPS unit.
TempF  = 32.0    (TempC * 1.8) + 32

Analog to Digital Converter Channels(ADC)
Vcc 1.80V = 1.82 vlts     (2.93mV *  621 Cnts)
Vcc 1.20V = 1.19 vlts     (2.93mV *  407 Cnts)
Pos 2.50V = 2.45 vlts     (2.93mV *  837 Cnts)
Neg 5.00V = 5.03 vlts     (7.38mV *  682 Cnts)
Vcc 3.30V = 3.33 vlts     (4.84mV *  689 Cnts)
Pos 5.00V = 4.84 vlts     (7.38mV *  656 Cnts)
5V Test    Max=4.86v    Min=4.84v    Noise=0.015v


V3
10 Second Accumulation of 1PPS Latched 25MHz Counter. (20 line buffer)
Buffer     Now (hex)     Prev-Now (dec) (25e6*10)
1              0               0
2              0               0
3              0               0
4              0               0
5              0               0
6              0               0
7              0               0
8              0               0
9              0               0
10              0               0
11              0               0
12              0               0
13              0               0
14              0               0
15              0               0
16              0               0
17              0               0
18              0               0
19              0               0
20              0               0




