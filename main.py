import sys

CONFIG_KEYS_INT = (
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
)
CONFIG_KEYS_STR = ("OUTPUT_FILE")
CONFIG_KEYS_BOOL = ("PERFECT")
MANDATORY_CONFIG_KEYS = {
    CONFIG_KEYS_INT: int,
    CONFIG_KEYS_STR: str,
    CONFIG_KEYS_BOOL: bool
}


def read_config_file(file_path: str) -> dict[str, str | int]:
    with open(file_path, 'r') as file:
        config: dict[str, str | int] = {}
        for line in file:
            line: str = line.strip()
            if line and not line.startswith('#'):
                key: str = line.split('=', 1)[0]
                value: str | int = line.split('=', 1)[1]
                try:
                    value = int(value)
                except ValueError:
                    pass
                config[key] = value
    return config


def validate_config(config: dict[str, str | int]):
    for key_group, expected_type in MANDATORY_CONFIG_KEYS.items():
        for key in key_group:
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
    # Avalon
    config_file_path = sys.argv[1]
    return config_file_path


def main() -> None:
    config_file_path = validate_parameters()
    config = read_config_file(config_file_path)
    validate_config(config)
    print(config)


if __name__ == "__main__":
    main()
