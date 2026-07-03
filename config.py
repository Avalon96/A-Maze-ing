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


def read_config_file(file_path: str) -> dict[str, str | int | tuple[int, int]]:
    config: dict[str, str | int | tuple[int, int]] = {}
    try:
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, start=1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    raise ValueError(
                        f"Malformed line {line_num} in {file_path}: {line}"
                    )
                key, _, raw_value = line.partition('=')
                key = key.strip()
                value = raw_value.strip()
                try:
                    if key in CONFIG_KEYS_INT:
                        config[key] = int(value)
                    elif key in CONFIG_KEYS_COORD:
                        x: str = value.split(',')[0].strip()
                        y: str = value.split(',')[1].strip()
                        config[key] = (int(x), int(y))
                    elif key in CONFIG_KEYS_BOOL:
                        config[key] = value.lower() == 'true'
                    else:
                        config[key] = value
                except ValueError as e:
                    raise ValueError(
                        f"Invalid value for {key} on line {line_num}: {value}"
                    ) from e
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found:{file_path}") from None
    except OSError as e:
        raise OSError(f"Could not read config file {file_path}: {e}") from e
    return config


def validate_config(config: dict[str, str | int | tuple[int, int]]) -> None:
    for key_group, expected_type in MANDATORY_CONFIG_KEYS.items():
        for key in key_group:

            # DEBUG
            from debug import PRINT_DEBUG
            if PRINT_DEBUG:
                print(f"validate_config: {key} = {config.get(key)}")
            # DEBUG END

            if key not in config:
                raise ValueError(f"Missing mandatory configuration key: {key}")
            if not isinstance(config[key], expected_type):
                raise ValueError(
                    f"Invalid type for configuration key: {key}. "
                    f"Expected {expected_type.__name__}, "
                    f"got {type(config[key]).__name__}"
                )


def validate_parameters() -> str:

    # DEBUG
    from debug import PRINT_DEBUG
    l: int = 2 + PRINT_DEBUG
    # DEBUG END

    if len(sys.argv) != l:
        raise ValueError("Usage: python main.py <config_file_path>")
    return sys.argv[1]
