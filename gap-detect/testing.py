from traceroute_analysis import traceroute_analysis
from traceroute_collection import gap_detected


def detection(id, t1, t2):
    print("TESTING:\t","Re started traceroute data colleciton to id:", id)
    # when doing in real time pause while traceroute collects data
    testing1, testing2 = gap_detected(id, t1, t2, True)
    output = traceroute_analysis(testing1, testing2)
    return output


def stop_traceroute(id):
    print("TESTING:\t","Stoped tracerouting to id:", id)


# Example function call
# detection("24.49.90.3.txt", 1662680942.4790363, 1662806033.300248)
