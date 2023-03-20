import data_manipulation
from loguru import logger


# Parses all of the data and puts it in a variable called data
def traceroute_analysis(good_data, unverified_data):
    # Get list of unique routes
    good_unique_routes = good_data["Traceroute"].unique()

    # Filter out empty sets
    good_unique_routes = [routes for routes in good_unique_routes if len(routes) > 0]

    # Transform routes
    # Instead of [[hop a1, hop a2, ...], [hop b1, hop b2, ...]] --> [[hop a1, hop b1, ...], [hop a2, hop b2, ...]]
    good_grouped_unique_routes = [set(hop) for hop in zip(*good_unique_routes)]

    total_score = [
        verify(row[0], good_grouped_unique_routes)
        for i, row in unverified_data.iterrows()
    ]

    # TODO: Is this the right length to be dividing by?
    return (sum(total_score) / len(total_score)) * 100


def verify(data, verify_check):
    score = [1 if hop in good_hop else 0 for hop, good_hop in zip(data, verify_check)]
    return sum(score) / len(score)
