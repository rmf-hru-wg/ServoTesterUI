from enum import Enum, auto
from dataclasses import dataclass

from gs2d import SerialInterface, Futaba, KondoICS
from typing import Type, Optional
from time import sleep

import threading

class ServoProtocol(Enum):
    KONDO_ICS_20 = auto()
    KONDO_ICS_30 = auto()
    KONDO_ICS_35 = auto()
    KONDO_ICS_36 = auto()

    FUTABA_ROBOT = auto()
    FUTABA_SBUS_1 = auto()
    FUTABA_SBUS_2 = auto()

    DYNAMIXEL_PROTO_1 = auto()
    DYNAMIXEL_PROTO_2 = auto()

    FEETECH_SCS = auto()

@dataclass
class ServoData:
    id: str
    target_angle: float = 0.0
    current_angle: float = 0.0
    is_power_on: bool = False

def open_servo_if_by_proto(serial_if:SerialInterface, proto:ServoProtocol):
    if proto == ServoProtocol.FUTABA_ROBOT:
        class FutabaServoDriver(Futaba.Futaba):
            def __init__(self, serial_interface):
                super().__init__(serial_interface)
                if self.command_handler:
                    self.add_command = self.command_handler.add_command
            def close(self, force=False):
                if self.command_handler:
                    self.command_handler.close()
        return FutabaServoDriver(serial_if)
    elif proto == ServoProtocol.KONDO_ICS_36:
        return KondoICS(serial_if, loopback=False)
    elif proto == ServoProtocol.KONDO_ICS_20 | ServoProtocol.KONDO_ICS_30 | ServoProtocol.KONDO_ICS_35:
        # return KondoICS(serial_if, version versionloopback=False)
        pass

class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
            raise NotImplementedError("ServoCommunication is a singletone class. Use get_instance()")

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls.__init__(cls._instance)
        return cls._instance


class ServoCommunication(Singleton):
    def __init__(self) -> None:
        self._serial_if: SerialInterface = None
        self._servo_if = None
        self.serial_path:str = None
        self.servo_proto:ServoProtocol = None
        self.servo_list:list[ServoData] = []

    def send_servo_async(self):
        pass

    def send_servo_sync(self):
        for d in self.servo_list:
            if not d.is_power_on:
                self._servo_if.set_torque_enable(True, sid=d.id)
                d.is_power_on = True

        for d in self.servo_list:
            self._servo_if.set_target_position(d.target_angle, sid=d.id)

    @property
    def servo_proto(self):
        return self._servo_proto

    @servo_proto.setter
    def servo_proto(self, servo_proto:ServoProtocol):
        if servo_proto != None:
            self._servo_if = open_servo_if_by_proto(self._serial_if, servo_proto)
        self._servo_proto = servo_proto

    @property
    def serial_path(self):
        return self._serial_path

    @serial_path.setter
    def serial_path(self, serial_path:str):
        if serial_path != None:
            if self._servo_if != None:
                self._servo_if.close()
            if self._serial_if != None:
                self._serial_if.close()
            sleep(0.2)

            self._serial_if = SerialInterface(serial_path)
            print("Open serial:", self._serial_if)
            if self.servo_proto != None:
                self._servo_if = open_servo_if_by_proto(self._serial_if, self.servo_proto)
        self._serial_path = serial_path




