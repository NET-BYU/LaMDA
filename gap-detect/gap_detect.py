from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

UPLOAD_THRESHOLD = 60 * 1
RECENCY_WINDOW = "1m"
GAP_WINDOW = "24h"

# You can generate an API token from the "API Tokens Tab" in the UI
token = "<Put API key/URL here>"
org = "<Put org here>"
bucket = "<Put bucket here>"

client =  InfluxDBClient(url="<Put URL here>", token=token, org=org)

# Check to see the recency of the last data point
def detect_recency(id_num):
    query = 'from(bucket: "<Put bucket here>") |> range(start: -{}) |> filter(fn: (r) => r["_measurement"] == "mem") |> filter(fn: (r) => r["_field"] == "used_percent") |> filter(fn: (r) => r["host"] == "host1") |> sort(columns: ["_time"], desc: true) |> last() '.format(RECENCY_WINDOW)
    # print(query)
    tables = client.query_api().query(query, org=org)

    # for table in tables:
    #     for record in table.records:
    #         print(datetime.timestamp(record.get_time()))

    # if (tables != []):
    #     return None
    # else:
    #     return 1
    print(tables)
    return None if (tables != []) else 1

# Check most recent two points and see if they are within the gap threshold
def detect_gap():
    penultimate_pt = -1
    last_pt = -1

    # Debug vars
    penultimate_val = -1
    last_val = -1

    query = 'from(bucket: "<Put bucket here>") |> range(start: -{}) |> filter(fn: (r) => r["_measurement"] == "mem") |> filter(fn: (r) => r["_field"] == "used_percent") |> filter(fn: (r) => r["host"] == "host1") |> sort(columns: ["_time"], desc: true) |> limit(n:2, offset: 0) '.format(GAP_WINDOW)
    tables = client.query_api().query(query, org=org)

    for table in tables:
        for record in table.records:
            # print(datetime.timestamp(record.get_time()))
            if last_pt == -1:
                last_pt = datetime.timestamp(record.get_time())
                last_val = record.get_value()
            else:
                penultimate_pt = datetime.timestamp(record.get_time())
                penultimate_val = record.get_value()

    # Make sure data is within the threshold
    # print("Diff:\t\t", last_pt - penultimate_pt)
    print("last_pt:\t", last_pt, "\tval:\t", last_val)
    print("penultimate_pt:\t", penultimate_pt, "\tval:\t", penultimate_val)
    if (last_pt - penultimate_pt) > UPLOAD_THRESHOLD:
        print("GAP_DETECT:\t", "No data within the last five minutes <possible flag raised here>")
        return 1, penultimate_pt, last_pt # Change the 1 to the IP address
    elif (last_pt - penultimate_pt) < UPLOAD_THRESHOLD:
        print("GAP_DETECT:\t", "Good data")
        return None, None, None


# def main():

#     if detect_recency():

#         try:
#             while True:
#                 detect_gap()
#         except KeyboardInterrupt:
#             print("\nCtrl-C pressed. Exiting...")
#     else:
#         print("No recent data found. Check your sensor <possible flag raised here>")

# if __name__ == "__main__":
#     main()
