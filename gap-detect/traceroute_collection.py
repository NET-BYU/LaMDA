from traceroute_resources import parse_data
# import pandas as pd

IP_true_file = "<Put IP addr here>"
IP_false_file = "<Put IP addr here>"
path_to_data = "Outputs/"
length_of_true_data = (
    1008  # 7 days.     1 day = 1440 minutes      (1440 * 7) / 10 = 1008
)
number_of_test_IPs = 20


def gap_detected(id, timestamp1, timestamp2, testing_false_data):
    # getting the data from the text files and throwing them in some dataframes
    # TODO: Make sure that the timestamps are withing the time that we took data
    IP_true_df = parse_data(IP_true_file)
    IP_false_df = parse_data(IP_true_file)
    if testing_false_data:
        IP_untested_df = IP_false_df.copy()
    else:
        IP_untested_df = IP_true_df.copy()

    # here is where I convert the times with the timestamps to lines in the data
    # the true_* and untested_* variables are meant to be index numbers in either

    # this might not work, it really depends on which times we get
    for index, row in IP_true_df.iterrows():
        if row["Time"] > timestamp1:
            true_end = index - 1
            break
    true_start = true_end - length_of_true_data
    # If the time we get is to close to the begining of the file, then automatically just take the data from the beginning of the program
    if true_start < 0:
        # TODO: throw an error here to let us know that this triggered
        # TODO: make this smarter so that it can try to stay faithful to the actual times given by timestamp1
        true_start = 0
        true_end = length_of_true_data
    # true_end = length_of_true_data  # just for testing purposes, I would do more math if this was actually implemented

    differance = int(
        (timestamp2 - timestamp1) / (60 * 10)
    )  # 60 seconds / minute and 10 minutes / data sample
    # uses different methods for finding the begining of the testing data for different use cases
    if testing_false_data:
        for i in IP_untested_df.index:
            if IP_untested_df.at[i, "Time"] > timestamp2:
                untested_start = i
                break
    else:
        untested_start = true_end + differance
    untested_end = untested_start + number_of_test_IPs

    # This trims down IP_untested_df to just the data that we want
    start_to_drop = [i for i in range(0, untested_start)]
    end_to_drop = [i for i in range(untested_end, len(IP_untested_df))]
    data_to_drop = start_to_drop + end_to_drop
    IP_untested_df = IP_untested_df.drop(data_to_drop, axis=0)

    # this trims down IP_true_df to just the data that we want
    begining_to_drop = [i for i in range(0, true_start)]
    end_to_drop = [i for i in range(untested_end, len(IP_untested_df))]
    data_to_drop = begining_to_drop + end_to_drop
    IP_true_df = IP_true_df.drop(data_to_drop, axis=0)

    # removing the time collum from both because we don't want it in the output
    IP_true_df = IP_true_df.drop(["Time"], axis=1)
    IP_untested_df = IP_untested_df.drop(["Time"], axis=1)
    return IP_true_df, IP_untested_df
