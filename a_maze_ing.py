import sys
from typing import cast

from visualizer import preference
from config import (
    read_config_file,
    validate_config,
    validate_parameters
)
from maze_generator import Coord, MazeGenerator, MazeGenerationError


def build_generator(
        config: dict[str, str | int | Coord | bool]
        ) -> MazeGenerator:
    """Build a MazeGenerator from the parsed configuration.

    Parameters
    ----------
    config : dict[str, str | int | Coord | bool]
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
        entry=cast(Coord, config["ENTRY"]),
        exit_=cast(Coord, config["EXIT"]),
        perfect=cast(bool, config["PERFECT"]),
        seed=seed
    )


def main() -> None:
    """Read the config, build the maze, save it and show the viewer."""
    try:
        path: str = validate_parameters()
        config: dict[str, str | int | Coord | bool] = read_config_file(path)
        validate_config(config)
        output_file: str = cast(str, config["OUTPUT_FILE"])

        maze: MazeGenerator = build_generator(config)
        maze.generate()
        maze.save(output_file)
        preference(maze, output_file)
    except (ValueError, FileNotFoundError, OSError, MazeGenerationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
