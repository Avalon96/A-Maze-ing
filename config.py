import sys

CONFIG_KEYS_INT: tuple[str, str, str] = ("WIDTH", "HEIGHT", "SEED")
CONFIG_KEYS_COORD: tuple[str, str] = ("ENTRY", "EXIT")
CONFIG_KEYS_STR: tuple[str] = ("OUTPUT_FILE",)
CONFIG_KEYS_BOOL: tuple[str] = ("PERFECT",)
MANDATORY_CONFIG_KEYS: dict[tuple[str, ...], type] = {
    ("WIDTH", "HEIGHT"): int,
    CONFIG_KEYS_COORD: tuple,
    CONFIG_KEYS_STR: str,
    CONFIG_KEYS_BOOL: bool
}


def read_config_file(
        file_path: str
        ) -> dict[str, str | int | tuple[int, int] | bool]:
    """Read a config file and return parsed configuration parameters.

    The file is expected to contain lines in the format "KEY=VALUE".
    Blank lines and comments (lines starting with "#") are ignored.
    Values are parsed based on the key group:

    * Integers for `CONFIG_KEYS_INT`
    * Tuples of two integers `(x, y)` for `CONFIG_KEYS_COORD`
    * Booleans for `CONFIG_KEYS_BOOL`
    * Strings for all other keys

    Parameters
    ----------
    file_path : str
        Path to the configuration file.

    Returns
    -------
    dict[str, str | int | tuple[int, int] | bool]
        Mapping of configuration keys to their parsed values.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    PermissionError
        If the config file cannot be read due to insufficient permissions.
    OSError
        If the config file cannot be opened or read for any other
        I/O-related reason.
    ValueError
        If a line is malformed (missing "=") or a value cannot be
        converted to its expected type.
    """
    config: dict[str, str | int | tuple[int, int] | bool] = {}
    try:
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, start=1):

                # DEBUG
                from debug import PRINT_DEBUG
                if PRINT_DEBUG:
                    print(f"read_config_file: line {line_num}: {line.strip()}")
                # DEBUG END

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


def validate_config(
        config: dict[str, str | int | tuple[int, int] | bool]
        ) -> None:
    """Validate that all mandatory configuration keys are present
    and typed correctly.

    Checks every key listed in `MANDATORY_CONFIG_KEYS` against the parsed
    config dictionary, confirming both presence and expected type.

    Parameters
    ----------
    config : dict[str, str | int | tuple[int, int] | bool]
        The parsed configuration dictionary, as returned by
        `read_config_file`.

    Raises
    ------
    ValueError
        If a mandatory key is missing, or if its value does not match
        the expected type for that key.
    """
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
    """Validate and extract the config file path from command-line arguments.

    Returns
    -------
    str
        The path to the configuration file, taken from `sys.argv[1]`.

    Raises
    ------
    ValueError
        If the script was not invoked with exactly one command-line
        argument.
    """
    # DEBUG
    from debug import PRINT_DEBUG
    argc: int = 2 + PRINT_DEBUG
    # DEBUG END

    if len(sys.argv) != argc:
        raise ValueError("Usage: python main.py <config_file_path>")
    return sys.argv[1]
