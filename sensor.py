#!/usr/bin/python3
from bluepy.btle import Scanner as ble_scanner
import paho.mqtt.client as mqtt_client
from requests import get as get_request
from json import load as load_json_from_file, loads as load_json_from_string, dump as dump_json_to_file
from json import dumps as dump_json_to_string
from sys import exit
from logging import info as i, error as e, basicConfig as basic_logging_config, INFO
from time import sleep

CONFIG = "config.json"


def configure_logging():
    """
    Configure logging utility with proper formatting
    """
    basic_logging_config(format="%(asctime)s [%(levelname)s] %(message)s", level=INFO)


def create_system_configuration_template():
    """
    Creates a template for system configration
    """
    config = {
        "api_server": "http://<API_SERVER_URL_HERE>",
        "mqtt_id": "<MQTT_UNIQUE_ID_HERE>"
    }
    i("Creating template config file")
    with open(CONFIG, "w") as config_json:
        dump_json_to_file(config, config_json)


def get_system_configuration():
    """
    Get the basic configuration
    """
    i("Loading system configuration")
    with open(CONFIG) as config_json:
        return load_json_from_file(config_json)


def get_measurement_configuration(api_server_url):
    """
    Get rest of configuration from api server
    """
    i("Loading measurement configuration")
    r = get_request(api_server_url)
    if(r.status_code == 200):
        return load_json_from_string(r.text)
    else:
        raise Exception(f"Couldn't fetch configuration - HTTP status: {r.status_code}")


def connect_mqtt(broker, port, id):
    """
    Connect to MQTT broker
    """
    def on_connect(_client, _userdata, _flags, rc):
        if rc != 0:
            raise Exception(f"Counldn't connect to MQTT Broker {broker}:{port}")
    i("Connecting to MQTT broker")
    client = mqtt_client.Client(id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def signed_hex_string_to_int(value):
    """
    Convert signed hex string to int
    """
    bits = 16
    result = int(value, bits)
    if result & (1 << (bits-1)):
        result -= 1 << bits
    return result


def handle_single_device(dev, devices, mqtt):
    """
    Handle a single entry of BLE Scanning
    """
    address = dev.addr.lower()
    rssi = dev.rssi
    if address in devices:
        for (adtype, _, value) in dev.getScanData():
            if (adtype == 22):
                topic = devices[address]
                battery = int(value[22:24], 16)
                humidity = int(value[20:22], 16)
                temperature = signed_hex_string_to_int(value[16:20]) / 10
                data = {
                    "t": temperature,
                    "h": humidity,
                    "b": battery,
                    "r": rssi
                }
                i(f"{address} @ {rssi} dBm: {temperature} C, {humidity} % RH, battery {battery} %")
                mqtt.publish(topic, dump_json_to_string(data))


def on_mqtt_message_prototype(scanner, config):
    def on_mqtt_message(client, userdata, message):
        i("Received trigger, scanning BLE")
        discovered_devices = scanner.scan(float(config["scan_interval"]))
        for dev in discovered_devices:
            handle_single_device(dev, config["whitelist"], client)

    return on_mqtt_message


def main():
    """
    The main code
    """
    configure_logging()
    while(True):
        try:
            system_config = get_system_configuration()
            config = get_measurement_configuration(system_config["api_server"])
            mqtt = connect_mqtt(config["mqtt_broker_ip"], int(config["mqtt_broker_port"]), system_config["mqtt_id"])
            scanner = ble_scanner()
            mqtt.on_message = on_mqtt_message_prototype(scanner, config)
            mqtt.subscribe(config["mqtt_trigger_topic"])
            i("Waiting for MQTT trigger")
            mqtt.loop_forever()
        except FileNotFoundError as exp:
            e(f"Couldn't find configuration file '{exp.filename}'!")
            create_system_configuration_template()
            exit(-1)
        except KeyboardInterrupt:
            i("Program interrupted by user")
            exit(0)
        except Exception as exp:
            e(exp)
        finally:
            mqtt.disconnect()


if __name__ == "__main__":
    main()
