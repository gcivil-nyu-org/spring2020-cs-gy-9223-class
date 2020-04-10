#
# Formulas for Mercury's built-in and natively supported sensor types
# Sample processing formulas with primary sensors and fictional Mercury-branded sensors
#

from ag_data import models


def fPass(timestamp, sensor, measurement_payload):
    print("passing")

    return None


def fMercurySimpleTemperatureSensor(timestamp, sensor, measurement_payload):
    print("fMercurySimpleTemperatureSensor")

    return None


def fMercuryDualTemperatureSensor(timestamp, sensor, measurement_payload):
    print("fMercuryDualTemperatureSensor")

    mean = measurement_payload["internal"] / 2 + measurement_payload["external"] / 2
    diff = measurement_payload["internal"] - measurement_payload["external"]

    result = {"mean": mean, "diff": diff}

    return result


def fMercuryFlowSensor(timestamp, sensor, measurement_payload):

    latest = models.AGMeasurement.objects.filter(sensor_id=sensor.id)

    result = None

    if latest.count() == 0:
        result = {"gasLevel": 100}
    else:
        latest = latest.latest("timestamp")
        timeElapsed = timestamp - latest.timestamp

        lastResult = latest.value["result"]["gasLevel"]

        if lastResult is None:
            result = None
        else:
            result = {
                "gasLevel": lastResult
                - measurement_payload["volumetricFlow"]
                * (timeElapsed.microseconds / 1000000)
            }

    return result