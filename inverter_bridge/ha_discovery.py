"""HA MQTT Discovery payload generator."""
import json

SENSORS = [
    {
        "key": "battery_soc",
        "name": "Battery SOC",
        "topic_suffix": "battery/soc",
        "unit": "%",
        "device_class": "battery",
        "state_class": "measurement",
        "icon": "mdi:battery",
    },
    {
        "key": "battery_voltage",
        "name": "Battery Voltage",
        "topic_suffix": "battery/voltage",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "icon": "mdi:lightning-bolt",
    },
    {
        "key": "battery_current",
        "name": "Battery Current",
        "topic_suffix": "battery/current",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
        "icon": "mdi:current-dc",
    },
    {
        "key": "battery_power",
        "name": "Battery Power",
        "topic_suffix": "battery/power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:battery-charging",
    },
    {
        "key": "battery_temperature",
        "name": "Battery Temperature",
        "topic_suffix": "battery/temperature",
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "icon": "mdi:thermometer",
    },
    {
        "key": "ac_voltage",
        "name": "AC Voltage",
        "topic_suffix": "ac/voltage",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "icon": "mdi:sine-wave",
    },
    {
        "key": "ac_power",
        "name": "AC Output Power",
        "topic_suffix": "ac/power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:power-plug",
    },
    {
        "key": "ac_frequency",
        "name": "AC Frequency",
        "topic_suffix": "ac/frequency",
        "unit": "Hz",
        "device_class": "frequency",
        "state_class": "measurement",
        "icon": "mdi:sine-wave",
    },
    {
        "key": "pv_power",
        "name": "PV Total Power",
        "topic_suffix": "pv/power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:solar-power",
    },
    {
        "key": "pv1_power",
        "name": "PV1 Power",
        "topic_suffix": "pv/pv1_power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:solar-power-variant",
    },
    {
        "key": "pv1_voltage",
        "name": "PV1 Voltage",
        "topic_suffix": "pv/pv1_voltage",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "icon": "mdi:solar-panel",
    },
    {
        "key": "grid_power",
        "name": "Grid Power",
        "topic_suffix": "grid/power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:transmission-tower",
    },
    {
        "key": "load_power",
        "name": "Load Power",
        "topic_suffix": "load/power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:home-lightning-bolt",
    },
    {
        "key": "inverter_temperature",
        "name": "Inverter Temperature",
        "topic_suffix": "inverter/temperature",
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "icon": "mdi:thermometer",
    },
    {
        "key": "run_mode",
        "name": "Run Mode",
        "topic_suffix": "inverter/run_mode",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:information",
    },
]

RUN_MODE_MAP = {
    0: "Waiting",
    1: "Checking",
    2: "Normal",
    3: "Off",
    4: "Permanent Fault",
    5: "Update Mode",
    6: "EPS Check",
    7: "EPS Mode",
    8: "Self-Test",
    9: "Idle",
    10: "Standby",
}


def build_discovery_payloads(config: dict, serial: str) -> list[tuple[str, str]]:
    """Return list of (topic, json_payload) tuples for all sensors."""
    base_topic = config["mqtt"]["base_topic"]
    ha_prefix = config["mqtt"]["ha_discovery_prefix"]
    node_id = f"solax_{serial}"
    results = []

    for sensor in SENSORS:
        discovery_topic = f"{ha_prefix}/sensor/{node_id}/{sensor['key']}/config"

        payload: dict = {
            "name": sensor["name"],
            "unique_id": f"{node_id}_{sensor['key']}",
            "state_topic": f"{base_topic}/{sensor['topic_suffix']}",
            "availability_topic": f"{base_topic}/status",
            "payload_available": "online",
            "payload_not_available": "offline",
            "value_template": "{{ value }}",
            "icon": sensor["icon"],
            "device": {
                "identifiers": [node_id],
                "name": "Solax Inverter",
                "model": "ESGSolax 5kW 24V Hybrid",
                "manufacturer": "Solax Power",
            },
        }

        if sensor["unit"]:
            payload["unit_of_measurement"] = sensor["unit"]
        if sensor["device_class"]:
            payload["device_class"] = sensor["device_class"]
        if sensor["state_class"]:
            payload["state_class"] = sensor["state_class"]

        results.append((discovery_topic, json.dumps(payload)))

    return results
