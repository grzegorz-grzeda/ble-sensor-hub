#!/usr/bin/python3
from bluepy.btle import Scanner as ble_scanner
import paho.mqtt.client as mqtt_client
import requests
import json
import sys
from logging import info, error, basicConfig, INFO
from time import sleep

CONFIG = "config.json"


def configure_logging():
    basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=INFO)


def get_system_configuration():
    with open(CONFIG) as config_json:
        return json.load(config_json)


def get_measurement_configuration(api_server_url):
    r = requests.get(api_server_url)
    if(r.status_code == 200):
        return json.loads(r.text)
    else:
        raise Exception(f"Couldn't fetch configuration - HTTP status: {r.status_code}")


def connect_mqtt(broker, port, id):
    def on_connect(_client, _userdata, _flags, rc):
        if rc == 0:
            info("Connected to MQTT Broker!")
        else:
            raise Exception(f"Counldn't connect to MQTT Broker {broker}:{port}")
    client = mqtt_client.Client(id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def handle_single_device(dev, devices, mqtt):
    address = dev.addr.lower()
    rssi = dev.rssi
    if address in devices:
        for (adtype, _, value) in dev.getScanData():
            if (adtype == 22):
                topic = devices[address]
                humidity = int(value[20:22], 16)
                temperature = int(value[16:20], 16) / 10
                info(f"=> {address} @ {rssi} dBm, MQTT: {topic}")
                data_to_send = f"{temperature};{humidity}"
                mqtt.publish(f"{topic}", data_to_send)


def main():
    configure_logging()
    while(True):
        try:
            system_config = get_system_configuration()
            config = get_measurement_configuration(system_config["api_server"])
            mqtt = connect_mqtt(config["mqtt_broker_ip"], int(config["mqtt_broker_port"]), system_config["mqtt_id"])
            mqtt.loop_start()
            scanner = ble_scanner()
            while(True):
                discovered_devices = scanner.scan(float(config["scan_interval"]))
                for dev in discovered_devices:
                    handle_single_device(dev, config["whitelist"], mqtt)
                sleep(float(config["sleep_interval"]))
        except FileNotFoundError as exp:
            error(f"Couldn't find configuration file '{exp.filename}'!")
            sys.exit(-1)
        except Exception as exp:
            error(exp)


if __name__ == "__main__":
    main()
