import re
import socket

from common.logger import Logger

LOGGER = Logger("ipv4").get()

# Regex pattern for matching IPv4 addresses
IPV4_PATTERN = r"([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})"


def get_host_ip_address(suffix: str = "") -> str:
    return socket.gethostbyname(socket.gethostname() + suffix)


def filter_ip_prefill(host_ip: str) -> str:
    """Returns the standard group of the given IP_v4-address, if it not localhost
    Example:
    get_ip_prefill("192.168.1.4") == "192.168.1."
    get_ip_prefill("127.0.0.1") == ""
    """
    if host_ip.startswith("127"):
        return ""
    matches = re.findall(IPV4_PATTERN, host_ip)
    if len(matches) == 0:
        return ""
    first = int(matches[0][0])
    if first <= 127:
        return matches[0][0] + "."
    if first <= 191:
        return matches[0][0] + "." + matches[0][1] + "."
    return matches[0][0] + "." + matches[0][1] + "." + matches[0][2] + "."


def get_ip_prefill() -> str:
    try:
        ip = get_host_ip_address()
        result = filter_ip_prefill(ip)
        if result:
            LOGGER.info(f"current ipv4 address: {ip}, prefill: {result}")
            return result
        ip = get_host_ip_address(".local")
        result = filter_ip_prefill(ip)
        LOGGER.info(f"current ipv4 address: {ip}, prefill: {result}")
        return result
    except socket.gaierror:
        LOGGER.info("An error occured fetching the ip address. No prefill available.")
        return ""
