import logging
import logging.config
import os
import time

import requests
import schedule
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

logging.config.fileConfig("logging.ini")
log = logging.getLogger("json")


# GLOBALS
API_CLIENT = os.environ.get("API_CLIENT", "")
API_SECRET = os.environ.get("API_SECRET", "")
INFLUX_HOST = os.environ.get("INFLUX_HOST", "")
INFLUX_HOST_PORT = int(os.environ.get("INFLUX_HOST_PORT", 8086))
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN", "")
INFLUX_ORG = os.environ.get("INFLUX_ORG", "")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "")
LATITUDE = os.environ.get("LATITUDE", "")
LONGITUDE = os.environ.get("LONGITUDE", "")
RUNMINS = int(os.environ.get("RUNMINS", 0))

log.info(
    {
        "message": "starting",
        "env": {"RUNMINS": RUNMINS, "LATITUDE": LATITUDE, "LONGITUDE": LONGITUDE},
    }
)

INFLUX_CLIENT = InfluxDBClient(
    url=f"{INFLUX_HOST}:{INFLUX_HOST_PORT}", org=INFLUX_ORG, token=INFLUX_TOKEN
)
INFLUX_WRITE_API = INFLUX_CLIENT.write_api(write_options=SYNCHRONOUS)


def metoffice_request():
    url = f"https://api-metoffice.apiconnect.ibmcloud.com/v0/forecasts/point/hourly?excludeParameterMetadata=false&includeLocationName=true&latitude={LATITUDE}&longitude={LONGITUDE}"
    headers = {
        "X-IBM-Client-Id": API_CLIENT,
        "X-IBM-Client-Secret": API_SECRET,
        "accept": "application/json",
    }
    resp = requests.get(url, headers=headers)
    payload_data = resp.json()["features"][0]["properties"]["timeSeries"]
    log.info({"message": f"retrieved {len(payload_data)} records from metoffice"})
    return payload_data


def write_to_influx(data_payload):
    data_payload = list(data_payload)
    INFLUX_WRITE_API.write(INFLUX_BUCKET, INFLUX_ORG, data_payload)
    log.info({"message": f"updated {len(data_payload)} records in InfluxDB"})


def apply_format(data_point):
    base_dict = {"measurement": "met_weather", "tags": {"name": "met_weather"}}
    time_stamp = data_point["time"]
    base_dict.update({"time": time_stamp})
    del data_point["time"]

    for k, v in data_point.items():
        if type(v) == int:
            data_point.update({k: float(v)})

    base_dict.update({"fields": data_point})
    return base_dict


def metoffice_to_influxdb():
    raw_data = metoffice_request()
    formatted_data = map(apply_format, raw_data)
    write_to_influx(formatted_data)


if __name__ == "__main__":
    metoffice_to_influxdb()
    if RUNMINS:
        schedule.every(RUNMINS).minutes.do(metoffice_to_influxdb)
        while True:
            schedule.run_pending()
            time.sleep(60 * RUNMINS)
