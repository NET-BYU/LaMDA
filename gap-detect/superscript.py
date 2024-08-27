from gap_detect import detect_gap, detect_recency
import loguru
from time import sleep
from testing import detection, stop_traceroute


SENSOR_ID = 1
CONFIDENCE_THRESHOLD = 0.8
TIME_TRAVEL = -604800

def check_sensor(sensor_id, confidence):
    if confidence < CONFIDENCE_THRESHOLD:
        print("SUPERSCRIPT\t","{} has been flagged for re-registration".format(sensor_id))    


def main():
    try:
        while True:
            sensor_id = detect_recency(SENSOR_ID)
            if sensor_id != None:
                print("SUPERSCRIPT\t","{} has gone inactive".format(sensor_id))
                stop_traceroute(sensor_id)

            else:
                sensor_id, strt_tmstmp, end_tmstmp = detect_gap()
                print("SUPERSCRIPT\t","\n\tID:\t{}\n\tSTRT:\t{}\n\tEND:\t{}\n".format(sensor_id, strt_tmstmp, end_tmstmp))
                if sensor_id != None and strt_tmstmp != -1:
                    confidence = detection(SENSOR_ID, strt_tmstmp + TIME_TRAVEL, end_tmstmp + TIME_TRAVEL)
                    print("SUPERSCRIPT\t","Gap analyzed:\tConfidence:\t{} for Sensor#{}".format(confidence, sensor_id))
                    check_sensor(SENSOR_ID, confidence)
            sleep(30)


    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Exiting...")
        return


if __name__ == "__main__":
    main()
