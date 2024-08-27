from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from random import uniform
from time import sleep

# You can generate an API token from the "API Tokens Tab" in the UI
token = "<Put API key/URL here>"
org = "<Put org here>"
bucket = "<Put bucket here>"

client = InfluxDBClient(url="<Put URL here>", token=token, org=org)

write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    data = "mem,host=host1 used_percent=" + str(uniform(0.0, 100))
    write_api.write(bucket, org, data)
    sleep(30)
