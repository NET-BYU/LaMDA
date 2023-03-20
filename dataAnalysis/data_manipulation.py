import pandas as pd
import numpy as np
from loguru import logger

length_of_true_data = (
    1008  # 7 days.     1 day = 1440 minutes      (1440 * 7) / 10 = 1008
)
seconds_per_week = 604800


def convert_traceroute(route, total_hops=3):
    route = route.split(" ")

    # Filter out empty hops and stars
    # route = [hop for hop in route if hop not in ("", "*")]
    route = [hop for hop in route if hop not in ("")]

    # TODO: Only remove stars at the end of the route

    # Remove last byte of IP address
    # route = [hop.rsplit(".", 1)[0] for hop in route]

    # Limit number of hops
    route = route[-total_hops:]

    # Convert to tuples so the route is hashable
    route = tuple(route)

    # Remove empty routes
    if len(route) == 0:
        return np.NaN

    return route


def dataframe(target, server, start):
    # Takes the data from a txt file and parses it into a pandas dataframe in a way that will be recognizable by the machine learning algorithm
    data = pd.read_csv(
        f"Outputs/{server}/{target}.txt",
        sep="\t",
        index_col=0,
        names=["Time", "TTL", "Traceroute", "Delay", "Latency"],
        converters={"Traceroute": convert_traceroute},
    )

    # Drop some data we don't need
    data = data.drop(["TTL", "Latency", "Delay"], axis=1)

    # Remove any NaNs. These mean that there was no routes listed in the CSV file
    data = data.dropna()

    # Convert index into date time
    data.index = pd.to_datetime(data.index, unit="s", utc=True).tz_convert(
        tz="US/Mountain"
    )

    # Filter data by specific start time
    data = data[start:]

    # Group by 7 day chunks
    groups = data.groupby([pd.Grouper(freq="7D")])

    return groups


def process_dataframe(data, len_of_IP):
    random_list = ["a", "b"]
    row_to_drop = []
    for index in data.index:
        if type(data.loc[index, "Traceroute"]) == type(random_list):
            # I decided that we don't want to include any instances of * into the data. This is in an effort to provide more specificity to the data
            while True:
                try:
                    data.loc[index, "Traceroute"].remove("*")
                except:
                    break
            while True:
                try:
                    data.loc[index, "Traceroute"].remove("")
                except:
                    break
            # We need a consistant sized array to pass into sklearn, so i decided that the last 5 nodes in the traceroute's path. I belived this would be sort enough almost any route would have then but long enough to get accurate results
            if len(data.loc[index, "Traceroute"]) > len_of_IP:
                reduced_traceroute = data.loc[index, "Traceroute"][-len_of_IP:]
            else:
                while len(data.loc[index, "Traceroute"]) < len_of_IP:
                    data.loc[index, "Traceroute"].append("0.0.0.0")
                reduced_traceroute = data.loc[index, "Traceroute"][0:]
            del data.loc[index, "Traceroute"][0:]
            # This takes the IP addresses from the ["x.x.x.x", "x.x.x.x"] format and replaces it with ["x.x.x",  "x.x.x"]
            for ip in range(len(reduced_traceroute)):
                broken_ip = reduced_traceroute[ip].split(".")
                while True:
                    try:
                        broken_ip.remove("")
                    except:
                        break
                try:
                    data.loc[index, "Traceroute"].append(
                        broken_ip[0] + "." + broken_ip[1] + "." + broken_ip[2]
                    )
                except:
                    logger.debug("Can't append:", broken_ip)
            if len(reduced_traceroute) == 0:
                row_to_drop.append(index)
                # This takes the last 5 delay values and converts them to floats
            while True:
                try:
                    data.loc[index, "Delay"].remove("*")
                except:
                    break
            while True:
                try:
                    data.loc[index, "Delay"].remove("")
                except:
                    break
            if len(data.loc[index, "Delay"]) > len_of_IP:
                reduced_delay = data.loc[index, "Delay"][-len_of_IP:]
            # This ensures that even if something wonkey happens with the traceroute and we don't get the amount of data that we expect, there is still 5 numbers in the array
            else:
                while len(data.loc[index, "Delay"]) < len_of_IP:
                    data.loc[index, "Delay"].append("0.0")
                reduced_delay = data.loc[index, "Delay"][
                    0:
                ]  # This Takes in all of the strings that make up the delay array and converts them into floats.
            if len(reduced_delay) == 0:
                logger.debug("reduced_delay:")
            del data.loc[index, "Delay"][0:]
            for delay in reduced_delay:
                data.loc[index, "Delay"].append(float(delay))
        else:
            logger.debug(f"Error in data_manipulation.trim_dataframe")
            row_to_drop.append(index)
    data = data.drop(row_to_drop, axis=0)
    data = data.reset_index(drop=True)
    return data


def trim_dataframe(df, timestamp1, timestamp2):
    # here is where I convert the times with the timestamps to lines in the data
    if timestamp1 > timestamp2:
        logger.debug(
            f"WARNING - data_manipulation.py\n\t Timestamp1 is after Timestamp2. Switching the two."
        )
        return trim_dataframe(df, timestamp2, timestamp1)
    if timestamp1 == timestamp2:
        logger.debug(
            f"WARNING - data_manipulation.py\n\t Timestamp1 = Timestamp2. Adding a week to Timestamp2."
        )
        return trim_dataframe(df, timestamp1, timestamp2 + seconds_per_week / 7)

    # the start and end variables are meant to be index numbers in df
    start = 0
    end = 0
    for index, row in df.iterrows():
        if row["Time"] > timestamp1:
            start = index - 1
            break
    for index, row in df.iterrows():
        if row["Time"] > timestamp2:
            end = index
            break

        # If the time we get is to close to the begining of the file, then automatically just take the data from the beginning of the program
    # Lets us know about and fixes any out of bounds errors that are likley to happen
    if end <= 0:
        logger.debug(
            f"WARNING - data_manipulation.py\n\t Timestamp1 and Timestamp2 pre-date the creation of the file."
        )
        end = 0
    elif start < 0:
        logger.debug(
            f"WARNING - data_manipulation.py:\n\t Timestamp1 pre-dates the creaton of the file."
        )
        start = 0

    # trims down IP_untested_df to just the data that we want
    start_to_drop = [i for i in range(0, start)]
    end_to_drop = [i for i in range(end, len(df))]
    data_to_drop = start_to_drop + end_to_drop
    df = df.drop(data_to_drop, axis=0)

    # Trims off the time collumn
    df = df.drop(["Time"], axis=1)
    return df


# When there has been a gap from time timestamp1 to timestamp2 this takes the last weeks's worth of data from id_T and the next week's worth of data from id_Q. Puts them into dataframes, trims, and processes them
def gap_detected(IP_true_df, IP_untested_df, timestamp1, timestamp2):
    # Fromating and getting rid of un nessisary data
    IP_true_df = process_dataframe(IP_true_df, 5)
    IP_untested_df = process_dataframe(IP_untested_df, 5)
    return IP_true_df, IP_untested_df
