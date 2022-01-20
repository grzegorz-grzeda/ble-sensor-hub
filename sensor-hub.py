import logging
from http_requests import get_sensors_config, send_sensor_values
from ble_scan import scan_for_devices
from time import sleep
from decouple import config

DEFAULT_SLEEP_TIME = int(config('DEFAULT_SEEP_TIME'))
DEFAULT_SCAN_TIME = int(config('DEFAULT_SCAN_TIME'))

def get_scan_interval(scan_interval_from_config):
    return DEFAULT_SCAN_TIME if scan_interval_from_config < 1 else scan_interval_from_config

def get_sleep_interval(sleep_interval_from_config):
    return DEFAULT_SLEEP_TIME if sleep_interval_from_config < 1 else sleep_interval_from_config

def main():
    sh = logging.StreamHandler()
    sh.format('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('sensor-hub')
    logger.setLevel(logging.INFO)
    logger.addHandler(sh)
    while True:
        try:
            logger.info("Getting sensors configuration")
            config = get_sensors_config()
            scan_interval = get_scan_interval(config['scan_interval_seconds'])
            sleep_interval = get_sleep_interval(config['sleep_interval_seconds'])
            logger.info("Scanning for devices")
            measurements = scan_for_devices(config['sensors'], scan_interval)
            logger.info("Sending measurements")
            for measurement in measurements:
                send_sensor_values(measurement)
        except Exception as error:
            print(error)
        finally: 
            sleep(sleep_interval)


if __name__ == "__main__":
    main()
