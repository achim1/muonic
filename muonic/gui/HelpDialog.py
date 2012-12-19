#! /usr/bin/env python


from PyQt4 import QtGui, QtCore

class HelpDialog(QtGui.QDialog): 

    def __init__(self, *args):
        _NAME = 'Help'
        QtGui.QDialog.__init__(self,*args)
        self.resize(600, 480)
        self.setModal(True)
        self.setWindowTitle("DAQ Commands")
        self.v_box = QtGui.QVBoxLayout()
        self.textbox = QtGui.QPlainTextEdit(self.helptext())
        self.textbox.setReadOnly(True)
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.v_box.addWidget(self.textbox)
        self.v_box.addWidget(self.button_box)
        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )

        self.show()

    def helptext(self):
        """
        Show this text in the help window
        """
    
        return """QNET2_Vx Help Page
    ------------------------------------------------------------
    Quarknet Scintillator Card 'QNET2_V2' HE=HELP CL=Clear Screen
    Command List Firmware Date 06/23/03 CPU_TempC=31.1 CPU_Volts=3.3
    ------------------------------------------------------------
    Quick Guide,
    see http://neutrino.phys.washington.edu/~walta/qnet_daq/
    for more information
    ------------------------------------------------------------
    General
    HE - Help
    HE1 - Help page 1
    HEx - Help page x
    ------------------------------------------------------------
    Start & Stop Counter
    CE=Enable
    CD=Disable
    ------------------------------------------------------------
    GPS & Weather
    BA - Barometer Current Reading, Raw BCD counts and kPa.
    TH - Display Digital Thermometer, -40 to 99 degrees C.
    DG - Display GPS Date, Time, Position and Status.
    ------------------------------------------------------------
    Scalars
    DF - Display Scalar Fifo Data, First 12 Bytes.
    DS - Display Scalar Fifo, Counters 0-3, Triggers, and 1PPS Time.
    ------------------------------------------------------------
    Acces internal control registers 
    -(needed to set coincidence and veto criteria as well as gate width)-
    WC MM DD - Write Counter Control Registers CPLD, address MM with DD.
    WT MM DD - Write Time Control Registers TMC address MM with data DD.
    check control registers with
    DC - Display Counters, Control Registers CPLD, address 0-4.
    DT - Display Time Control Registers TMC , address 0-3.
    ---------------------------adresses---------------------------------
    MM - 00 -> 8bits for channel enable/disable, coincidence and veto
    |7   |6   |5          |4          |3       |2       |1       |0       |
    |veto|veto|coincidence|coincidence|channel3|channel2|channel1|channel0|
    ---------------------------bits-------------------------------------
    Set bits for veto:
    ........................
    00 - ch0 is veto
    01 - ch1 is veto
    10 - ch2 is veto
    11 - ch3 is veto
    ........................
    Set bits for coincidence
    ........................ 
    00 - singles
    01 - twofold
    10 - threefold
    11 - fourfold
    --------------------------examples-----------------------------------
    threefold coincidence with veto ch3, all channels enabled
    11101111 -> 1110 1111 two binary numbers -> e f two corresponding hex numbers
    => WC 00 EF should do the job
    ..................................
    no veto, coincidence level twofold, all channels enabled
    00011111 -> 0001 1111 two binary numbers -> 1 f two corresponding hex numbers
    => WC 00 1F should do the job
    .................................
    no veto, single mode, all channels enabled
    00001111 -> 0000 1111 two binary numbers -. 0 f two corresponding hex numbers
    => WC 00 0F should do the job
    
    ...for more descriptions see 
    http://neutrino.phys.washington.edu/~berns/WALTA/Qnet2/FNAL_files/QnetCpldII.doc
    ===================================ADVANCED=======================================
    BC BB.B GG.G - Barometer Calibrate, Store Baseline and Gain, HELP 'HB'.
    NM N - NMEA GPS Data Echo (N==1 On),(N!=1 Off), (GPS_Baud=9600).
    NA N - NMEA GPS Data Append (N==1 On),(N!=1 Off), add GPS to output.
    ST N - Send Status Data (N==1 On),(N!=1 Off), HELP 'HF'.
    GP - Send GPS NMEA Rate GGA=1Sec, RMC=1Sec, others=disable.
    COUNTER - CE=Enable, CD=Disable, Controls TMC Running bit CPLD CCR1.
    3
    FLASH - FL=Load Binary File, FR=Read SumCheck, FC=Copy_2_CPLD.
    RESET - RB=TMC and Counter CPLD, RE=MSP430+TMC+CPLD.
    HELP - HF=Trigger format, HS=Status format, HB=Barometer format
    'HF' Help command on trigger data format
     Timer Counter Bits 31..0 ( 8 bytes ascii)
     RE0 TAG RE0 DATA ( 2 bytes ascii) -- '0x80=Trig_Tag'
     FE0 TAG FE0 DATA ( 2 bytes ascii) -- '0x20=Edge_Tag'
     RE1 TAG RE1 DATA ( 2 bytes ascii) -- '0x1F=Data,(5 bits)'
     FE1 TAG FE1 DATA ( 2 bytes ascii) --
     RE2 TAG RE2 DATA ( 2 bytes ascii) --
     FE2 TAG FE2 DATA ( 2 bytes ascii) --
     RE3 TAG RE3 DATA ( 2 bytes ascii) --
     FE3 TAG FE3 DATA ( 2 bytes ascii) --
     1PPS TIME Bits 31..0 ( 8 bytes ascii)
     GPS RMC UTC hhmmss.sss (10 bytes ascii)
     GPS RMC DATE ddmmyy ( 6 bytes ascii)
     GPS RMC STATUS A=valid ( 1 byte ascii)
     GPS GGA SATELLITES USED ( 2 bytes ascii)
     TRIG IRQ STATUS FLAGS ( 1 byte ascii)
     GPS DATA TO 1PPS DELAY ms ( 5 bytes ascii)
    Status Line Format (* BCD1 BCD2 BCD3 BCD4), 5 minute update synced to triggers
     BAR_kPa -> BCD1 / 10
     GPS_DegC -> BCD2 / 10
     CPU_DegC -> BCD3
     CPU_Vcc -> BCD4 * 0.00122 (3.3 Volt Supply)
     (Pending BCD5-BCD8 CPLD register 0-3 setup data)
     (Pending BCD9 for Board Serial Number)
    'HS' Help command on Status data format
     TRIGGER IRQ STATUS BYTE, BIT ASSIGNMENTS (see 'HF' for location on data line)
     0x1 = 1PPS interrupt pending
     0x2 = Trigger interrupt pending
     0x4 = GPS data could be corrupted (write in progress while readout)
     0x8 = Current or last 1PPS tick not within 41666666 +/-50 clock ticks
    'HB' Help command on Barometer data format
     kPa=Baseline+(BAR_ADC/Gain), If Data= 0xFFFF (not calibrated)
     Flash memory display, (Memory Display of Baseline*10) = 0xFFFF
     Flash memory display, (Memory Display of Gain*10) = 0xFFFF"""



if __name__ == "__main__":

    import sys
    app = QtGui.QApplication(sys.argv)
    hwindow = HelpWindow()
    sys.exit(app.exec_())

