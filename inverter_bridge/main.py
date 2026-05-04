"""ESGSolax → Home Assistant MQTT bridge.

Polls the inverter via Solarman V5 (port 8899) or Solax local REST API,
then publishes data to MQTT with Home Assistant auto-discovery support.
"""
import asyncio
import logging
import os
import sys

import aiohttp
import yaml
from asyncio_mqtt import Client as MQTTClient, MqttError, Will

from ha_discovery import SENSORS, RUN_MODE_MAP, build_discovery_payloads

try:
    from pysolarmanv5 import PySolarmanV5Async, V5FrameError
except ImportError:
    PySolarmanV5Async = None
    V5FrameError = Exception

logger = logging.getLogger(__name__)

# Solax Gen4 registers (FC04 input registers)
_REG_BLOCK_0_START = 0
_REG_BLOCK_0_COUNT = 20   # covers PV, AC, Battery
_REG_BLOCK_40_START = 40
_REG_BLOCK_40_COUNT = 35  # covers load(47), inverter temp(54), grid(70)
_REG_SOC = 168


def _to_signed16(val: int) -> int:
    return val - 65536 if val > 32767 else val


def _parse_registers(r0: list[int], r40: list[int], soc: int) -> dict:
    """Extract inverter data from three register blocks."""
    pv1_power = r0[6]
    pv2_power = r0[7]

    battery_soc = soc
    # Gen3 fallback: if Gen4 SOC register returns nonsense, try index 103-0=63 in r40
    # (addressed separately if needed — Gen4 assumed by default)

    return {
        "pv1_voltage":          round(r0[0] * 0.1, 1),
        "pv1_power":            pv1_power,
        "pv_power":             pv1_power + pv2_power,
        "ac_voltage":           round(r0[10] * 0.1, 1),
        "ac_power":             _to_signed16(r0[11]),
        "ac_frequency":         round(r0[12] * 0.01, 2),
        "battery_voltage":      round(r0[13] * 0.1, 2),
        "battery_current":      round(_to_signed16(r0[14]) * 0.1, 2),
        "battery_power":        _to_signed16(r0[15]),
        "battery_temperature":  _to_signed16(r0[17]),
        "battery_soc":          battery_soc,
        "load_power":           r40[47 - _REG_BLOCK_40_START],
        "inverter_temperature": round(_to_signed16(r40[54 - _REG_BLOCK_40_START]) * 0.1, 1),
        "grid_power":           _to_signed16(r40[70 - _REG_BLOCK_40_START]),
        "run_mode":             RUN_MODE_MAP.get(r0[19], f"Unknown({r0[19]})"),
    }


class InverterBridge:
    def __init__(self, config: dict):
        self.config = config
        self.protocol: str | None = None
        self._solarman: "PySolarmanV5Async | None" = None

    async def detect_and_connect(self) -> bool:
        proto_setting = self.config["inverter"]["protocol"]
        timeout = self.config["inverter"]["timeout"]
        ip = self.config["inverter"]["ip"]
        serial = self.config["inverter"]["serial"]
        port = self.config["inverter"]["port"]

        if PySolarmanV5Async and proto_setting in ("auto", "solarman"):
            try:
                self._solarman = PySolarmanV5Async(
                    address=ip,
                    serial=int(serial),
                    port=port,
                    mb_slave_id=1,
                    verbose=False,
                    auto_reconnect=True,
                )
                await asyncio.wait_for(self._solarman.connect(), timeout=timeout)
                await asyncio.wait_for(
                    self._solarman.read_input_registers(_REG_BLOCK_0_START, 1),
                    timeout=timeout,
                )
                self.protocol = "solarman"
                logger.info("Connected via Solarman V5 protocol (port %d)", port)
                return True
            except Exception as exc:
                logger.warning("Solarman V5 failed: %s", exc)
                if self._solarman:
                    try:
                        await self._solarman.disconnect()
                    except Exception:
                        pass
                    self._solarman = None

        if proto_setting in ("auto", "solax_rest"):
            try:
                data = await self._solax_rest_read()
                if data and "Data" in data:
                    self.protocol = "solax_rest"
                    logger.info("Connected via Solax local REST API")
                    return True
            except Exception as exc:
                logger.error("Solax REST also failed: %s", exc)

        return False

    async def _solax_rest_read(self) -> dict | None:
        url = f"http://{self.config['inverter']['ip']}/"
        payload = {
            "optType": "ReadRealTimeData",
            "pwd": str(self.config["inverter"]["rest_password"]),
        }
        timeout = aiohttp.ClientTimeout(total=self.config["inverter"]["timeout"])
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, timeout=timeout) as resp:
                if resp.status != 200:
                    raise ConnectionError(f"REST API returned HTTP {resp.status}")
                return await resp.json(content_type=None)

    async def _read_solarman(self) -> dict:
        timeout = self.config["inverter"]["timeout"]
        r0 = await asyncio.wait_for(
            self._solarman.read_input_registers(_REG_BLOCK_0_START, _REG_BLOCK_0_COUNT),
            timeout=timeout,
        )
        r40 = await asyncio.wait_for(
            self._solarman.read_input_registers(_REG_BLOCK_40_START, _REG_BLOCK_40_COUNT),
            timeout=timeout,
        )
        soc_list = await asyncio.wait_for(
            self._solarman.read_input_registers(_REG_SOC, 1),
            timeout=timeout,
        )
        return _parse_registers(r0, r40, soc_list[0])

    async def _read_solax_rest(self) -> dict:
        raw = await self._solax_rest_read()
        data = raw.get("Data", [])
        if len(data) < 171:
            raise ValueError(f"REST response too short: {len(data)} registers")

        # Build same-shape lists as the Modbus blocks
        r0 = data[0:20]
        r40 = data[40:75]
        soc = data[168]
        return _parse_registers(r0, r40, soc)

    async def read_inverter_data(self) -> dict:
        if self.protocol == "solarman":
            return await self._read_solarman()
        if self.protocol == "solax_rest":
            return await self._read_solax_rest()
        raise RuntimeError("No protocol available — call detect_and_connect first")


def _topic_map(base: str) -> dict[str, str]:
    suffix_by_key = {s["key"]: s["topic_suffix"] for s in SENSORS}
    return {key: f"{base}/{suffix}" for key, suffix in suffix_by_key.items()}


async def _publish_data(mqtt_client: MQTTClient, data: dict, config: dict) -> None:
    base = config["mqtt"]["base_topic"]
    qos = config["mqtt"]["qos"]
    retain = config["mqtt"]["retain"]
    topics = _topic_map(base)

    for key, topic in topics.items():
        if key not in data:
            continue
        value = data[key]
        if isinstance(value, float):
            value = round(value, 2)
        await mqtt_client.publish(topic, str(value), qos=qos, retain=retain)


async def _send_discovery(mqtt_client: MQTTClient, config: dict) -> None:
    serial = str(config["inverter"]["serial"])
    for topic, payload in build_discovery_payloads(config, serial):
        await mqtt_client.publish(topic, payload, qos=1, retain=True)
    logger.info("Published HA discovery payloads for %d sensors", len(SENSORS))


def _setup_logging(config: dict) -> None:
    level = getattr(logging, config["logging"]["level"].upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    log_file = config["logging"].get("file", "")
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def _load_config() -> dict:
    config_path = os.environ.get("BRIDGE_CONFIG", "config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)


async def main() -> None:
    config = _load_config()
    _setup_logging(config)

    mqtt_cfg = config["mqtt"]
    status_topic = f"{mqtt_cfg['base_topic']}/status"
    bridge = InverterBridge(config)
    consecutive_failures = 0

    async with MQTTClient(
        mqtt_cfg["host"],
        port=mqtt_cfg["port"],
        username=mqtt_cfg["username"] or None,
        password=mqtt_cfg["password"] or None,
        client_id=mqtt_cfg["client_id"],
        will=Will(
            topic=status_topic,
            payload="offline",
            qos=1,
            retain=True,
        ),
    ) as mqtt_client:
        await mqtt_client.publish(status_topic, "online", qos=1, retain=True)
        logger.info("MQTT connected — sending discovery payloads")
        await _send_discovery(mqtt_client, config)

        while True:
            try:
                if bridge.protocol is None:
                    logger.info("Detecting inverter protocol...")
                    connected = await bridge.detect_and_connect()
                    if not connected:
                        logger.error("Cannot connect to inverter — retrying in 60s")
                        await asyncio.sleep(60)
                        continue

                data = await bridge.read_inverter_data()
                await _publish_data(mqtt_client, data, config)
                consecutive_failures = 0
                logger.debug("Published %d values — SOC=%s%%", len(data), data.get("battery_soc"))

            except (ConnectionError, asyncio.TimeoutError, OSError) as exc:
                consecutive_failures += 1
                logger.warning("Read failed (%d): %s", consecutive_failures, exc)
                bridge.protocol = None

            except Exception as exc:  # noqa: BLE001
                consecutive_failures += 1
                logger.warning("Unexpected error (%d): %s", consecutive_failures, exc)
                bridge.protocol = None

            if consecutive_failures >= 5:
                await mqtt_client.publish(status_topic, "offline", qos=1, retain=True)
                logger.warning("5 consecutive failures — marked offline in HA")
                consecutive_failures = 0

            await asyncio.sleep(config["inverter"]["poll_interval"])


if __name__ == "__main__":
    asyncio.run(main())
