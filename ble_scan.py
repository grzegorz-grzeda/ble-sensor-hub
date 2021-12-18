from bluepy.btle import Scanner as ble_scanner


def signed_hex_string_to_int(value):
    """
    Convert signed hex string to int
    """
    bits = 16
    result = int(value, bits)
    if result & (1 << (bits-1)):
        result -= 1 << bits
    return result


def handle_single_device(device, device_whitelist):
    address = device.addr.lower()
    if address in device_whitelist:
        
        for (adtype, _, value) in device.getScanData():
            if (adtype == 22):
                sensor = device_whitelist[address]
                battery = int(value[22:24], 16)
                humidity = int(value[20:22], 16)
                temperature = signed_hex_string_to_int(value[16:20]) / 10
                return {
                    "sensor": sensor,
                    "t": temperature,
                    "h": humidity,
                    "b": battery,
                }


def scan_for_devices(device_whitelist, scan_interval):
    result = []
    scanner = ble_scanner()
    discovered_devices = scanner.scan(scan_interval)
    for dev in discovered_devices:
        measurement = handle_single_device(dev, device_whitelist)
        if measurement is not None:
            result.append(measurement)

    return result
