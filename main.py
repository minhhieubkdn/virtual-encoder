# This Python file uses the following encoding: utf-8
from re import S
import sys
from pathlib import Path

import sys
import os
import time
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

from PySide2.QtCore import QObject, Slot, Signal, QTimer
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice

class MainWindow(QObject):
    def __init__(self):
        QObject.__init__(self)

        self.timer1 = QTimer()
        self.timer1.timeout.connect(lambda: self.check_connection())
        self.timer1.start(2000)

        self.timer2 = QTimer()
        self.timer2.timeout.connect(lambda: self.auto_send_position())

        self.start_time = time.time()

        self.serial_port = QSerialPort()
        self.serial_port.setBaudRate(115200, QSerialPort.Direction.AllDirections)
        self.serial_port.readyRead.connect(self.receive_serial_data)
        self.received_data = "None"
        self.is_connected = False
        self.opening_ports = None
        self.speed = 0.0
        self.current_position = 0.0
        self.is_auto_send_position = False
        self.current_time = self.start_time
        self.is_absolute_mode = True
        self.period = int(0)
        self.interval = int(0)

    receivedSerialDataSignal = Signal(str)
    getOpeningPorts = Signal(list)
    connectedPort = Signal(bool)
    setCurrentPosition = Signal(float)

    def get_current_pos(self, _speed):
        interval = time.time()
        interval -= self.start_time
        self.current_position = round(_speed * interval, 2)
        return self.current_position
    
    def auto_send_position(self):
        if self.is_connected:
            if self.is_auto_send_position:
                self.interval += self.period / 1000
                self.current_position = round(self.speed * self.interval, 2)
                self.send_serial_data('P' + str(self.current_position))
                self.setCurrentPosition.emit(self.current_position)
            

    @Slot(str)
    def connect_port(self, port_name):
        self.serial_port.setPortName(str(port_name))
        self.serial_port.open(QIODevice.ReadWrite)
        if self.serial_port.isOpen():
            print(self.serial_port.portName() + ' Connected!')

            self.is_connected = True
            self.connectedPort.emit(True)
            self.serial_port.errorOccurred.connect(self.handle_serial_error)
            self.receivedSerialDataSignal.emit("Connected")

    @Slot(str)
    def receive_serial_data(self):
        while self.serial_port.canReadLine():
            self.received_data = self.serial_port.readLine().data().decode()
            self.received_data = self.received_data.rstrip("\r\n")
            print("R:" + self.received_data)

            if self.received_data[:4] == 'M311':
                _speed = float(self.received_data[5:])
                self.set_speed(_speed)

            elif self.received_data == 'M317':
                self.get_current_pos(self.speed)
                self.send_serial_data("P" + str(self.current_position))
                self.is_auto_send_position = False
                self.timer2.stop()
                self.send_serial_data('Ok')
                self.setCurrentPosition.emit(self.current_position)

            elif self.received_data[:6] == "M317 T":
                self.period = int(self.received_data[6:])
                self.is_auto_send_position = True
                self.timer2.stop()
                self.timer2.start(self.period)
                self.interval = time.time() - self.start_time

            elif self.received_data[:4] == 'M316':
                if int(self.received_data[5:]) == 0:
                    self.is_absolute_mode = True
                    self.send_serial_data('Ok')
                elif int(self.received_data[5:]) == 1:
                    self.is_absolute_mode = False
                    self.send_serial_data('Ok')
            break

    @Slot(float)
    def set_speed(self, _speed):
        self.speed = _speed
        self.start_time = time.time()
        print(_speed)

    @Slot(str)
    def handle_serial_error(self):
        self.close_serial()

    @Slot(str)
    def send_serial_data(self, data):
        if self.serial_port.isOpen():
            self.sending_data = data + '\n'

            print('S:' + data)
            self.serial_port.write(self.sending_data.encode())
            self.receivedSerialDataSignal.emit(data)

    def check_connection(self):
        if self.is_connected:
            return
        else:
            self.opening_ports = QSerialPortInfo.availablePorts()
            port_name_array = [port.portName() for port in self.opening_ports]
            print(port_name_array)
            self.getOpeningPorts.emit(port_name_array)

    @Slot(bool)
    def close_serial(self, is_disconnecting):
        self.is_connected = False
        self.connectedPort.emit(False)
        self.receivedSerialDataSignal.emit("Disconnected")
        self.serial_port.errorOccurred.disconnect(self.handle_serial_error)
        self.serial_port.close()
        print("Serial Closed")

        self.is_auto_send_position = False
        self.timer2.stop()

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    main = MainWindow()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", main)
    engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))

    main.is_pending_connection = True

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
