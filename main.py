import sys

from config import (
    read_config_file,
    validate_config,
    validate_parameters
)
from maze_generator import MazeGenerator, MazeGenerationError


def build_generator(
        config: dict[str, str | int | tuple[int, int] | bool]
        ) -> MazeGenerator:
    return MazeGenerator(
        width=int(config["WIDTH"]),
        height=int(config["HEIGHT"]),
        entry=config["ENTRY"],
        exit=config["EXIT"],
        seed=int(config["SEED"]) if "SEED" in config else None,
        perfect=bool(config["PERFECT"]),
    )


def main() -> None:
    try:
        config_file_path: str = validate_parameters()
        config: dict[str, str | int | tuple[int, int] | bool] = \
            read_config_file(config_file_path)
        validate_config(config)

        maze: MazeGenerator = build_generator(config)
        maze.generate()
        maze.save(config["OUTPUT_FILE"])
    except (ValueError, FileNotFoundError, OSError, MazeGenerationError) as e:
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
