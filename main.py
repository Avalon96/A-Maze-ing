from config import (
    read_config_file,
    validate_config,
    validate_parameters
)


def main() -> None:
    config_file_path: str = validate_parameters()
    config: dict[str, str | int] = read_config_file(config_file_path)
    validate_config(config)
    # for key, value in config.items():
    #     print(f"{key}: {value}")


if __name__ == "__main__":
    main()
