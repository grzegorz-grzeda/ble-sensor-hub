# Simple BLE Sensor handler with MQTT
This is a simple project intending to capture functionality of the 
[ATC1441](https://github.com/atc1441/ATC_MiThermometer) sensors and push data through a computer (desktop, RPi, etc.) 
to the MQTT broker.

## Setup
After downloading the project, install the `python3`, `python3-pip` and `bluepy`. 
If you won't add needed capabilities, run the script `sudo ./sensor.py`. Otherwise run it normally `./sensor.py`.

For the first time, the program will create a `config.json` file. You need to fill it with proper entries.

You also need to run a simple web server, which will return the dynamic configuration for rest of operation.
The server should serve a simple GET request on the path defined in the `api_server` config entry in `config.json`.
The configuration is as follows (example):
```
{
    "whitelist":{
        "a4:c1:38:WW:YY:ZZ": "/room1",
        "a4:c1:38:JJ:KK:LL": "/room10"
    },
    "scan_interval": "10",
    "mqtt_broker_ip":"<MQTT_BROKER_IP_HERE>",
    "mqtt_broker_port": "<MQTT_BROKER_PORT_HERE>"
    "mqtt_trigger_topic": "/measure"
}
```

## Operation
When everything is set up:
- the program starts,
- fetches configuration from the defined server location,
- connects to the MQTT broker
- waits for a trigger message from the trigger topic and starts BLE scan
- if finds a device from the whitelist:
   - it presumes its a ATC1441, 
   - parses the service data,
   - packs it and sends to the defined MQTT topic

# Copyright
Under MIT license
&copy; 2021 G2Labs Grzegorz Grzęda