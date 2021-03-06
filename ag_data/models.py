from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
import uuid


class AGVenue(models.Model):
    """Store the venue where events happens, including name, description, latitude and
    longtitude.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=100, null=False, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    def __str__(self):
        return self.name


class AGEvent(models.Model):
    """Stores the information about events including name, date and description.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=40, blank=True)
    date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=100, null=False, blank=True)
    venue_uuid = models.ForeignKey(AGVenue, null=True, on_delete=models.SET_NULL)


class AGSensorType(models.Model):
    """Stores the information about sensor types which is used to provide a sensor template
    and related formula for different types of sensors.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1024, blank=True)
    processing_formula = models.IntegerField(default=0, null=False)
    format = JSONField()

    # Graph type for visualization in Grafana
    GRAPH = "graph"
    MAP = "map"
    GAUGE = "gauge"
    GRAPH_CHOICES = (
        (GRAPH, "Graph"),
        (MAP, "Map"),
        (GAUGE, "Gauge"),
    )
    graph_type = models.CharField(max_length=20, choices=GRAPH_CHOICES, default=GRAPH,)


class AGSensor(models.Model):
    """Stores the information about sensors including name and type id.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial = models.IntegerField(unique=True, default=1)
    name = models.CharField(max_length=1024, blank=True)
    type_id = models.ForeignKey(AGSensorType, null=False, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if self._state.adding:
            last_serial = AGSensor.objects.all().aggregate(models.Max("serial"))[
                "serial__max"
            ]

            if last_serial is not None:
                self.serial = last_serial + 1

        super(AGSensor, self).save(*args, **kwargs)


class AGMeasurement(models.Model):
    """Stores the information about sensor measurements, including timestamp, event, sensor
    id and measurement values.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, blank=False)
    event_uuid = models.ForeignKey(
        AGEvent, on_delete=models.CASCADE, blank=False, null=False
    )
    sensor_id = models.ForeignKey(
        AGSensor, on_delete=models.CASCADE, blank=False, null=False
    )
    value = JSONField()


class AGActiveEvent(models.Model):
    """Stores the currently Active event which must refer to one of the instance in AGEvent table
    """

    agevent = models.ForeignKey(AGEvent, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        # check if the inserted event is valid
        if not AGEvent.objects.filter(pk=self.pk).exists():
            pass

        # Make sure there's at most one record in table.
        objs = AGActiveEvent.objects.all()
        if len(objs) == 1:
            obj = objs[0]
            if obj.pk == self.pk:
                pass
            else:
                AGActiveEvent.objects.all().delete()
                super(AGActiveEvent, self).save(*args, **kwargs)
        elif len(objs) == 0:
            super(AGActiveEvent, self).save(*args, **kwargs)
        else:
            pass


class ErrorLog(models.Model):
    """Stores information about error log data,including error timestamp, error code,
    error description and error raw data
    """

    # error declaration
    UNKNOWN_FMT = "UNKNOWN_FORMAT"
    MISSING_COL = "MISSING_COLUMN"
    MISSING_FIELD_IN_RAW = "MISSING_FIELD_IN_RAW_READING"
    INVALID_COL_NM = "INVALID_COLUMN_NAME"
    INVALID_COL_VL = "INVALID_COLUMN_VALUE"
    INVALID_FIELD_IN_RAW = "INVALID_FIELD_IN_RAW_READING"
    ERROR_F_PROC_MMT = "FORMULA_PROCESS_MEASUREMENT_ERROR"
    EXTRA_KEYVAL_IN_MMT = "EXTRANEOUS_KEY_VALUE_PAIR_IN_MEASUREMENT"
    NO_ACT_EVENT = "NO_ACTIVE_EVENT"
    OTHER = "OTHER_ERROR"

    ERROR_CODE_CHOICES = [
        (UNKNOWN_FMT, "Unknown Format"),
        (MISSING_COL, "Missing Column"),
        (MISSING_FIELD_IN_RAW, "Missing Field In Raw Reading"),
        (INVALID_COL_NM, "Invalid Column Name"),
        (INVALID_COL_VL, "Invalid Column Value"),
        (INVALID_FIELD_IN_RAW, "Invalid Field In Raw Reading"),
        (ERROR_F_PROC_MMT, "Error When Formula Processing Measurement"),
        (EXTRA_KEYVAL_IN_MMT, "Extraneous Key-Value Pair In Measurement"),
        (NO_ACT_EVENT, "No active event"),
        (OTHER, "Other Error"),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now)
    error_code = models.CharField(
        max_length=100, choices=ERROR_CODE_CHOICES, default=OTHER
    )
    description = models.CharField(max_length=100, null=False, blank=False)
    raw_data = models.TextField(null=False)
