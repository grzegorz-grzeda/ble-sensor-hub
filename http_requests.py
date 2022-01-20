import logging
from requests import get, post
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from decouple import config
from base64 import b64encode

module_logger = logging.getLogger('sensor-hub.http_requests')

def encode_password(password):
    return b64encode(password.encode()).decode('utf-8')


def authorization_header(user, password):
    return {'Authorization': f'{user}:{encode_password(password)}'}


def get_sensors_config():
    try:
        module_logger.info("Fetching sensors config")
        url = config("SMARTHOME_URL")
        user = config("SMARTHOME_USER")
        passw = config("SMARTHOME_PASS")
        r = get(url, auth=HTTPBasicAuth(user, passw))
        if r.status_code == 200:
            return r.json()
        else:
            module_logger.error("Couldn't fetch configuration!")
            raise Exception(f"Couldn't fetch sensor configuration: HTTP{r.status_code}")
    except RequestException as error:
        raise Exception(error)


def send_sensor_values(sensor):
    try:
        module_logger.info("Sending measurements")
        url = config("SMARTHOME_URL")
        user = config("SMARTHOME_USER")
        passw = config("SMARTHOME_PASS")
        r = post(url, auth=HTTPBasicAuth(user, passw), json=sensor)
        if r.status_code != 200:
            module_logger.error("Couldn't send measurements!")
            raise Exception(f"Couldn't send measurement data: HTTP{r.status_code}")
    except RequestException as error:
        raise Exception(error)
