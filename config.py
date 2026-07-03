import sys

CONFIG_KEYS_INT: tuple[str, str] = ("WIDTH", "HEIGHT")
CONFIG_KEYS_COORD: tuple[str, str] = ("ENTRY", "EXIT")
CONFIG_KEYS_STR: tuple[str] = ("OUTPUT_FILE",)
CONFIG_KEYS_BOOL: tuple[str] = ("PERFECT",)
MANDATORY_CONFIG_KEYS: dict[tuple[str, ...], type] = {
    CONFIG_KEYS_INT: int,
    CONFIG_KEYS_COORD: tuple,
    CONFIG_KEYS_STR: str,
    CONFIG_KEYS_BOOL: bool
}


def read_config_file(file_path: str) -> dict[str, str | int]:
    with open(file_path, 'r') as file:
        config: dict[str, str | int] = {}
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key: str = line.split('=')[0].strip()
            value: str | int | tuple = line.split('=')[1].strip()
            if key in CONFIG_KEYS_INT:
                config[key] = int(value)
            elif key in CONFIG_KEYS_COORD:
                config[key] = tuple(map(int, value.split(',')))
            elif key in CONFIG_KEYS_BOOL:
                config[key] = value.lower() == 'true'
            else:
                config[key] = value
    return config


def validate_config(config: dict[str, str | int]):
    for key_group, expected_type in MANDATORY_CONFIG_KEYS.items():
        for key in key_group:
            # print(f"{key} = {config.get(key)}")
            if key not in config:
                raise ValueError(f"Missing mandatory configuration key: {key}")
            if not isinstance(config[key], expected_type):
                raise ValueError(
                    f"Invalid type for configuration key: {key}. "
                    f"Expected {expected_type.__name__}, "
                    f"got {type(config[key]).__name__}"
                )


def validate_parameters() -> str:
    if len(sys.argv) != 2:
        raise ValueError("Usage: python main.py <config_file_path>")
    return sys.argv[1]
