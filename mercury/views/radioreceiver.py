import datetime
import glob
import json
import os
import sys

import serial
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from subprocess import Popen

from ag_data.models import AGEvent


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    if "TRAVIS" in os.environ:
        result = ["dev/tty.USB"]
    return result


def call_script(uuid, port, fake):
    """
    Run a shell script to receive radio sensor data from the vehicle
    This script will call local server to store all data received
    Command Example:
    python3 ./scripts/radioport.py --uuid d81cac8d-26e1-4983-a942-1922e54a943d
        --port /dev/tty.SOC --fake
        --data '{"sensor_id": 1, "values": {"power": "2", "speed": 1},
            "date": "2020-02-02T20:21:22"}'
    """
    command = "python3 ./scripts/radioport.py --uuid {} --port {} ".format(
        str(uuid), str(port)
    )
    if fake:
        command = command + "--fake --data "
        data = {
            "sensor_id": 1,
            "values": {"power": "2", "speed": 1},
            "date": datetime.datetime(2020, 2, 2, 20, 21, 22),
        }
        data = json.dumps(data, cls=DjangoJSONEncoder)
        command = command + "'" + data + "'"
        print(command)
    Popen(command, shell=True)


def check_port(ser):
    """
        Package ser.is_open for test purpose
        TODO: Add other checks on Serial port
    """
    return ser.is_open


def build_error(str):
    return json.dumps({"error": str})


class RadioReceiverView(APIView):
    """
    This is a Django REST API supporting user to send GET request fetching the RADIO
    module configuration settings from backend and to send POST request sending
    JSON-formatted data.
    """

    def get(self, request, event_uuid=None):
        """
        The get request sent from web to determine the parameters of the serial port
            Url Sample:
            https://localhost:8000/radioreceiver/d81cac8d-26e1-4983-a942-1922e54a943d?
                &enable=1&baudrate=8000&bytesize=8&parity=N&stopbits=1&timeout=None&fake=1
            uuid: event_uuid
            enable: must define, set the port on if 1, off if 0
            baudrate: Optional, default 9600
            bytesize: Optional, default 8 bits
            parity: Optional, default no parity
            stop bits: Optional, default one stop bit
            timeout: Optional, default 1 second
            fake: Optional, send fake data for test only
            """
        # First check event_uuid exists
        try:
            event = AGEvent.objects.get(uuid=event_uuid)
        except AGEvent.DoesNotExist:
            event = False
        if event is False:
            return Response(
                build_error("Event uuid not found"), status=status.HTTP_404_NOT_FOUND
            )

        # Check Serial port parameters
        params = request.query_params
        enable = params.get("enable")
        if enable is None:
            return Response(
                build_error("Missing enable value in url"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        enable = int(enable)
        ser = serial.Serial()

        valid_ports = serial_ports()
        if len(valid_ports) > 0:
            ser.port = valid_ports[0]
        else:
            return Response(
                build_error("No valid ports on the backend"),
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        res = {"enable": enable}

        if params.get("baudrate"):
            ser.baudrate = params.get("baudrate")
        if params.get("bytesize"):
            bytesize = int(params.get("bytesize"))
            ser.bytesize = bytesize
        if params.get("parity"):
            ser.parity = params.get("parity")
        if params.get("stopbits"):
            ser.stopbits = int(params.get("stopbits"))
        if params.get("timeout"):
            timeout = int(params.get("timeout"))
            ser.timeout = timeout

        fake = params.get("fake")
        if fake:
            call_script(event_uuid, ser.port, fake)
        elif enable:
            try:
                ser.open()
                if check_port(ser):
                    # Call Script
                    call_script(event_uuid, ser.port, fake)
            except serial.serialutil.SerialException:
                pass
        else:
            if check_port(ser):
                ser.close()
            print("listening port closed")

        # Response data
        res["baudrate"] = ser.baudrate
        res["bytesize"] = ser.bytesize
        res["parity"] = ser.parity
        res["stopbits"] = ser.stopbits
        res["timeout"] = ser.timeout

        return Response(json.dumps(res), status=status.HTTP_200_OK)
