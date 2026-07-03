import sys

from config import (
    read_config_file,
    validate_config,
    validate_parameters
)


def main() -> None:
    try:
        config_file_path: str = validate_parameters()
        config: dict[str, str | int | tuple[int, int] | bool] = \
            read_config_file(config_file_path)
        validate_config(config)
    except (ValueError, FileNotFoundError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # DEBUG
    from debug import PRINT_DEBUG
    if PRINT_DEBUG:
        for key, value in config.items():
            print(f"main: {key}: {value}")
    # DEBUG END


if __name__ == "__main__":
    main()
