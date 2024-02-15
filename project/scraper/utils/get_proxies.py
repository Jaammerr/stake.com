import os
import sys
from pathlib import Path

from loguru import logger


def get_proxies() -> list[dict]:
    path = Path(__file__).parent.parent / "proxy.txt"
    if not os.path.exists(path):
        logger.error("proxy.txt not found")
        sys.exit(1)

    with open(path, "r") as f:
        proxies = [proxy.strip() for proxy in f.readlines()]

    valid_proxies = []
    for proxy in proxies:
        try:
            ip, port, username, password = proxy.split(":")
            valid_proxies.append(
                {
                    "http": f"http://{username}:{password}@{ip}:{port}",
                    "https": f"http://{username}:{password}@{ip}:{port}",
                }
            )
        except ValueError:
            logger.warning(f"Invalid proxy format: {proxy} | Skipped")

    if not valid_proxies:
        logger.error("No valid proxies found")
        sys.exit(1)

    logger.success(f"Loaded {len(valid_proxies)} proxies")
    return valid_proxies
