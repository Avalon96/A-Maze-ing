import sys
from typing import cast
from visualizar import preference

from config import (
    read_config_file,
    validate_config,
    validate_parameters
)
from maze_generator import MazeGenerator, MazeGenerationError


def build_generator(
        config: dict[str, str | int | tuple[int, int] | bool]
        ) -> MazeGenerator:
    """Build a MazeGenerator from the parsed configuration.

    Parameters
    ----------
    config : dict[str, str | int | tuple[int, int] | bool]
        Configuration values already validated by `validate_config`.

    Returns
    -------
    MazeGenerator
        A generator configured with the given values.
    """
    seed = cast(int, config["SEED"]) if "SEED" in config else None
    return MazeGenerator(
        width=cast(int, config["WIDTH"]),
        height=cast(int, config["HEIGHT"]),
        entry=cast(tuple[int, int], config["ENTRY"]),
        exit=cast(tuple[int, int], config["EXIT"]),
        seed=seed,
        perfect=cast(bool, config["PERFECT"]),
    )


def main() -> None:
    """Read the config, build the maze, save it and show the viewer."""
    try:
        config_file_path: str = validate_parameters()
        config: dict[str, str | int | tuple[int, int] | bool] = \
            read_config_file(config_file_path)
        validate_config(config)

        maze: MazeGenerator = build_generator(config)
        maze.generate()
        maze.save(cast(str, config["OUTPUT_FILE"]))
        preference(maze)
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
