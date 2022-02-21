from datetime import datetime, timedelta
from medops.models import device_models

def test_device_datum_to_dict():
    """Test the base datum class"""
    now = datetime.now()
    collected = now - timedelta(hours=1)
    datum = device_models.DeviceDatum(
        device_id=1,
        assigned_user=1,
        received_time=now,
        collection_time=collected
    )

    as_dict = datum.to_dict()
    assert as_dict['device_id'] == datum.device_id
    assert as_dict['assigned_user'] == datum.assigned_user
    assert as_dict['received_time'] == datum.received_time
    assert as_dict['collection_time'] == datum.collection_time

def test_device_datum_to_json():
    now = datetime.now()
    collected = now - timedelta(hours=1)
    datum = device_models.DeviceDatum(
        device_id=1,
        assigned_user=1,
        received_time=now,
        collection_time=collected
    )

    as_json = datum.to_json()
    assert as_json['device_id'] == datum.device_id
    assert as_json['assigned_user'] == datum.assigned_user
    assert as_json['received_time'] == now.isoformat()
    assert as_json['collection_time'] == collected.isoformat()

def test_device_datum_from_json():
    now = datetime.now()
    collected = now - timedelta(hours=1)
    datum = device_models.DeviceDatum(
        device_id=1,
        assigned_user=1,
        received_time=now,
        collection_time=collected
    )

    as_json = datum.to_json()
    reinflated = device_models.DeviceDatum.from_json(as_json)
    assert reinflated == datum

def test_temperature_datum():
    now = datetime.now()
    collected = now - timedelta(hours=1)
    datum = device_models.TemperatureDatum(
        device_id=1,
        assigned_user=1,
        received_time=now,
        collection_time=collected,
        deg_c=37.3
    )

    as_json = datum.to_json()
    assert as_json['device_id'] == datum.device_id
    assert as_json['assigned_user'] == datum.assigned_user
    assert as_json['received_time'] == now.isoformat()
    assert as_json['collection_time'] == collected.isoformat()
    assert as_json['deg_c'] == datum.deg_c

    reinflated = device_models.TemperatureDatum.from_json(as_json)
    assert reinflated == datum


def test_bloodpressure_datum():
    now = datetime.now()
    collected = now - timedelta(hours=1)
    datum = device_models.BloodPressureDatum(
        device_id=1,
        assigned_user=1,
        received_time=now,
        collection_time=collected,
        systolic=120,
        diastolic=80
    )

    as_json = datum.to_json()
    assert as_json['device_id'] == datum.device_id
    assert as_json['assigned_user'] == datum.assigned_user
    assert as_json['received_time'] == now.isoformat()
    assert as_json['collection_time'] == collected.isoformat()
    assert as_json['systolic'] == datum.systolic
    assert as_json['diastolic'] == datum.diastolic

    reinflated = device_models.BloodPressureDatum.from_json(as_json)
    assert reinflated == datum


def test_glucometer_datum():
    now = datetime.now()
    collected = now - timedelta(hours=1)
    datum = device_models.GlucometerDatum(
        device_id=1,
        assigned_user=1,
        received_time=now,
        collection_time=collected,
        mg_dl=80
    )

    as_json = datum.to_json()
    assert as_json['device_id'] == datum.device_id
    assert as_json['assigned_user'] == datum.assigned_user
    assert as_json['received_time'] == now.isoformat()
    assert as_json['collection_time'] == collected.isoformat()
    assert as_json['mg_dl'] == datum.mg_dl

    reinflated = device_models.GlucometerDatum.from_json(as_json)
    assert reinflated == datum


def test_pulse_datum():
    now = datetime.now()
    collected = now - timedelta(hours=1)
    datum = device_models.PulseDatum(
        device_id=1,
        assigned_user=1,
        received_time=now,
        collection_time=collected,
        bpm=80
    )

    as_json = datum.to_json()
    assert as_json['device_id'] == datum.device_id
    assert as_json['assigned_user'] == datum.assigned_user
    assert as_json['received_time'] == now.isoformat()
    assert as_json['collection_time'] == collected.isoformat()
    assert as_json['bpm'] == datum.bpm

    reinflated = device_models.PulseDatum.from_json(as_json)
    assert reinflated == datum


def test_weight_datum():
    now = datetime.now()
    collected = now - timedelta(hours=1)
    datum = device_models.WeightDatum(
        device_id=1,
        assigned_user=1,
        received_time=now,
        collection_time=collected,
        grams=57380
    )

    as_json = datum.to_json()
    assert as_json['device_id'] == datum.device_id
    assert as_json['assigned_user'] == datum.assigned_user
    assert as_json['received_time'] == now.isoformat()
    assert as_json['collection_time'] == collected.isoformat()
    assert as_json['grams'] == datum.grams

    reinflated = device_models.WeightDatum.from_json(as_json)
    assert reinflated == datum


def test_bloodsaturation_datum():
    now = datetime.now()
    collected = now - timedelta(hours=1)
    datum = device_models.BloodSaturationDatum(
        device_id=1,
        assigned_user=1,
        received_time=now,
        collection_time=collected,
        percentage=98
    )

    as_json = datum.to_json()
    assert as_json['device_id'] == datum.device_id
    assert as_json['assigned_user'] == datum.assigned_user
    assert as_json['received_time'] == now.isoformat()
    assert as_json['collection_time'] == collected.isoformat()
    assert as_json['percentage'] == datum.percentage

    reinflated = device_models.BloodSaturationDatum.from_json(as_json)
    assert reinflated == datum
