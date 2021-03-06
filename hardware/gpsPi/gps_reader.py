import os
import serial
from hardware.Utils.utils import get_logger, date_str_with_current_timezone

GPS_ID = 1


class GPSReader:
    def __init__(self, log_file_name=None):
        self.gps = serial.Serial(os.environ["GPS_PORT"], os.environ["GPS_BAUDRATE"])

        if log_file_name is None:
            self.logging = get_logger("GPS_LOG_FILE")
        else:
            self.logging = get_logger(log_file_name, log_file_name)

    def get_geolocation(self):
        while self.gps.inWaiting() == 0:
            pass
        nmeaSentence = str(self.gps.readline()).split(",")
        # print(nmeaSentence)
        nmeaType = nmeaSentence[0]

        # verify nmeaSentence type and verify if gps has valid data
        if nmeaType == "b'$GPRMC" and nmeaSentence[2] == "A":
            latitude_hours = float(nmeaSentence[3][0:2])
            latitude_minutes = float(nmeaSentence[3][2:])
            longitude_hours = float(nmeaSentence[5][0:3])
            longitude_minutes = float(nmeaSentence[5][3:])

            latitude_decimal = latitude_hours + latitude_minutes / 60
            longitude_decimal = longitude_hours + longitude_minutes / 60

            latitude_dir = nmeaSentence[4]
            longitude_dir = nmeaSentence[6]

            if latitude_dir == "S":
                latitude_decimal = latitude_decimal * -1
            if longitude_dir == "W":
                longitude_decimal = longitude_decimal * -1

            self.logging.info("latitude_decimal: " + str(latitude_decimal))
            self.logging.info("longitude_decimal: " + str(longitude_decimal))

            data = {}
            data["sensor_id"] = GPS_ID
            data["values"] = {
                "latitude": latitude_decimal,
                "longitude": longitude_decimal,
            }
            data["date"] = date_str_with_current_timezone()
            return data
        else:
            return None

    def get_speed_mph(self):
        while self.gps.inWaiting() == 0:
            pass

        nmeaSentence = str(self.gps.readline()).split(",")
        nmeaType = nmeaSentence[0]

        # verify nmeaSentence type and verify if gps has valid data
        if nmeaType == "b'$GPRMC" and nmeaSentence[2] == "A":

            speed_in_knots = nmeaSentence[7]
            speed_in_mph = float(speed_in_knots) * 1.151

            self.logging.info("speed: " + str(speed_in_mph))

            data = {}
            data["sensor_id"] = GPS_ID
            data["values"] = {
                "speed": speed_in_mph,
            }
            data["date"] = date_str_with_current_timezone()
            return data
        else:
            return None
