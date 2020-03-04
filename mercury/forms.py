"""This module defines the ModelForms (or Forms) that are used by the rendering
engine to accept input for various features of the site"""
from django import forms
from mercury.models import (
    Event,
    TemperatureSensor,
    AccelerationSensor,
    WheelSpeedSensor,
    SuspensionSensor,
    FuelLevelSensor,
)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"id": "post-event-name", "required": True}),
            "location": forms.TextInput(
                attrs={"id": "post-event-location", "required": True}
            ),
            "date": forms.DateInput(
                attrs={"id": "post-event-date", "required": True, "type": "date"}
            ),
            "comments": forms.Textarea(
                attrs={"id": "post-event-comments", "required": False},
            ),
        }


class TemperatureForm(forms.ModelForm):
    class Meta:
        model = TemperatureSensor
        fields = "__all__"
        widgets = {
            "created_at": forms.DateTimeInput(
                attrs={"id": "post-created-at-temp", "required": True}
            ),
            "temperature": forms.NumberInput(
                attrs={"id": "post-temperature", "required": True}
            ),
        }


class AccelerationForm(forms.ModelForm):
    class Meta:
        model = AccelerationSensor
        fields = "__all__"
        widgets = {
            "created_at": forms.DateTimeInput(
                attrs={"id": "post-created-at_accel", "required": True}
            ),
            "acceleration_x": forms.NumberInput(
                attrs={"id": "post-acceleration-X", "required": True}
            ),
            "acceleration_y": forms.NumberInput(
                attrs={"id": "post-acceleration-Y", "required": True}
            ),
            "acceleration_z": forms.NumberInput(
                attrs={"id": "post-acceleration-Z", "required": True}
            ),
        }


class WheelSpeedForm(forms.ModelForm):
    class Meta:
        model = WheelSpeedSensor
        fields = "__all__"
        widgets = {
            "created_at": forms.DateTimeInput(
                attrs={"id": "post-created-at_ws", "required": True}
            ),
            "wheel_speed_fr": forms.NumberInput(
                attrs={"id": "post-wheel-speed-fr", "required": True}
            ),
            "wheel_speed_fl": forms.NumberInput(
                attrs={"id": "post-wheel-speed-fl", "required": True}
            ),
            "wheel_speed_br": forms.NumberInput(
                attrs={"id": "post-wheel-speed-br", "required": True}
            ),
            "wheel_speed_bl": forms.NumberInput(
                attrs={"id": "post-wheel-speed-bl", "required": True}
            ),
        }


class SuspensionForm(forms.ModelForm):
    class Meta:
        model = SuspensionSensor
        fields = "__all__"
        widgets = {
            "created_at": forms.DateTimeInput(
                attrs={"id": "post-created-at_ss", "required": True}
            ),
            "suspension_fr": forms.NumberInput(
                attrs={"id": "post-suspension-fr", "required": True}
            ),
            "suspension_fl": forms.NumberInput(
                attrs={"id": "post-suspension-fl", "required": True}
            ),
            "suspension_br": forms.NumberInput(
                attrs={"id": "post-suspension-br", "required": True}
            ),
            "suspension_bl": forms.NumberInput(
                attrs={"id": "post-suspension-bl", "required": True}
            ),
        }


class FuelLevelForm(forms.ModelForm):
    class Meta:
        model = FuelLevelSensor
        fields = "__all__"
        widgets = {
            "created_at": forms.DateTimeInput(
                attrs={"id": "post-created-at_fl", "required": True}
            ),
            "current_fuel_level": forms.NumberInput(
                attrs={"id": "post-current-fuel-level", "required": True}
            ),
        }


class CANForm(forms.Form):
    """This simple form is used just to accept a CAN message on the CAN UI."""

    can_msg = forms.CharField(label="CAN Message")
