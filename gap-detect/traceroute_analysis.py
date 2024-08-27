from traceroute_resources import (
    verify,
)
from resources import (
    parse_data,
    create_check,
)
# import pandas as pd

start = 0
end = 1008  # 7 days.     1 days = 10080 minutes      (1440 * 7) / 10 = 1008
len_identified_data = 25
data = []
# Parses all of the data and puts it in a variable called data


def traceroute_analysis(good_data, unverified_data):
    # print("\nCalculating:\nGood data:")
    # print(good_data)
    # print("unverified_data:")
    # print(unverified_data)
    # parses the data we recieved from up above
    good_data = parse_data(good_data, 5, False)
    unverified_data = parse_data(unverified_data, 5, False)
    # print("parsed data:")
    # print(good_data)
    # print(unverified_data)
    verify_check = create_check(good_data)
    # print("Verified check:", verify_check)
    verified_data = []
    total_true = 0
    for i in unverified_data.index:
        verified_data.append(verify(unverified_data.take([i], axis=0), verify_check))
        if verified_data[i]:
            total_true += 1
    # print(f"Output = {total_true} / {len(verified_data)}")
    reliability_percent = total_true / len(verified_data)
    return reliability_percent
