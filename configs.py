import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from common.logger import Logger

LOGGER = Logger("configs.py").get()


@dataclass
class Config:
    width: int = field(default=1024)
    height: int = field(default=600)
    fullscreen: bool = field(default=False)
    playstation_ip: Optional[str] = field(default=None)
    recent_connected: list[str] = field(default_factory=list)

    @classmethod
    def parse_config(cls, path: Path) -> "Config":
        config = {}
        LOGGER.debug(
            f'Config path "{path}" exists: {path.exists()} is file: {path.is_file()}'
        )
        if path.exists() and path.is_file():
            with open(path, "r") as f:
                config = json.load(f)
        result = Config(**config)
        LOGGER.info(f"Config: {result}")

        if not path.exists():
            result.write_to_file(path)

        return result

    def write_to_file(self, path: Path) -> None:
        LOGGER.debug(f"Write config to {path}")
        config_dict = asdict(self)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config_dict, indent=4))


class ConfigManager:
    path = Path.home() / ".config" / "simdash" / "config.json"  # default path
    _config: Optional[Config] = None

    @classmethod
    def set_path(cls, path: Path) -> None:
        cls.path = path

    @classmethod
    def get_config(cls) -> Config:
        if cls._config is None:
            cls._config = Config.parse_config(cls.path)
        return cls._config

    @classmethod
    def last_connected(cls, ip_address: str) -> None:
        config = cls.get_config()
        if (
            len(config.recent_connected) > 0
            and config.recent_connected[0] == ip_address
        ):
            # already latest connected
            return
        if ip_address in config.recent_connected:
            config.recent_connected.remove(ip_address)
        config.recent_connected.insert(0, ip_address)
        config.write_to_file(cls.path)
