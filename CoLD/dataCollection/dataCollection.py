# Pings then traceroutes to each IP address in Input.json everyt 10 minutes
# Saves the traceroute data, the delay of each trace in that route, the TTL of the ping, and the delay of the ping
# Stores the saved data in a .txt file named after the IP address

import time
import os
from trace import getData
import sentry_sdk
import json

# Sentry will email me if the code stopps unexpectedly
sentry_sdk.init(
    "<Put API key/URL here>",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
)

# This is where we get the IP addresses we will be tracerouteing too
with open("Input.json", "r") as input_file:
    IPADR = json.load(input_file)

# Just making sure that the folder we want to put these files into exists
if not os.path.exists("./Outputs"):
    os.makedirs("./Outputs")

# Here is where I run the code that actualy runs the traceroute, ping, and
while True:
    for target in IPADR:
        with open("./Outputs/" + target + ".txt", "a") as this:
            this.write(getData(target) + "\n")
    time.sleep(60 * 10)
