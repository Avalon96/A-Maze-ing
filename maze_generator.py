from __future__ import annotations
import random
import sys
from collections import deque
from enum import IntFlag

Coord = tuple[int, int]
Grid = list[list[int]]


class MazeGenerationError(ValueError):
    """Raised when a maze cannot be generated with the given parameters."""


class Direction(IntFlag):
    """Bit flags representing a wall on each side of a maze cell."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8


# dx, dy, wall, opposite_wall, letter
_DIRECTIONS: tuple[tuple[int, int, Direction, Direction, str], ...] = (
    (0, -1, Direction.NORTH, Direction.SOUTH, "N"),
    (1, 0, Direction.EAST, Direction.WEST, "E"),
    (0, 1, Direction.SOUTH, Direction.NORTH, "S"),
    (-1, 0, Direction.WEST, Direction.EAST, "W"),
)

_BASE_42_PATTERN: tuple[str, ...] = (
    "#...###",
    "#.....#",
    "###.###",
    "..#.#..",
    "..#.###",
)


class MazeGenerator:
    """Generate rectangular mazes and query their structure and solution.

    Parameters
    ----------
    width, height:
        Size of the maze, in cells. Both must be positive integers.
    entry, exit:
        ``(x, y)`` coordinates (0-indexed, ``x`` is the column and ``y``
        is the row) of the maze entrance and exit. They must lie inside
        the maze bounds and be different from each other.
    seed:
        Optional integer used to seed the internal random number
        generator. Using the same seed (and the same other parameters)
        always produces the same maze. If omitted, a random seed is
        chosen automatically.
    perfect:
        If ``True`` (the default) the maze is "perfect": there is
        exactly one path between any two cells. If ``False``, one extra
        wall is knocked down (when possible) to create a loop, without
        creating any open 3x3 area.

    Raises
    ------
    ValueError
        If width, height, entry, exit, or seed cannot be converted to
        valid values.

    Notes
    -----
    Very small mazes may skip the ``42`` pattern entirely when the fixed
    pattern would not fit without breaking connectivity.

    The maze is not generated until `generate` is called.
    """

    def __init__(
        self,
        width: int,
        height: int,
        *,
        entry: Coord | None = None,
        exit: Coord | None = None,
        seed: int | None = None,
        perfect: bool = True
    ) -> None:
        self.width = self._as_int(width, "width")
        self.height = self._as_int(height, "height")
        self.entry = self._normalize_coord(
            entry if entry is not None else (0, 0), "entry")
        self.exit = self._normalize_coord(
            exit if exit is not None else (self.width - 1, self.height - 1),
            "exit",
        )
        self.seed = (
            self._as_int(seed, "seed")
            if seed is not None
            else random.randint(1, 2**31 - 1)
        )
        self.perfect = bool(perfect)

        self._grid: Grid | None = None
        self._path: str | None = None
        self._blocked_cells: set[Coord] = set()
        self.pattern_skipped: bool = False
        self.pattern_warning: str | None = None

    @staticmethod
    def _as_int(value: object, name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, (str, int)):
            raise ValueError(f"{name} must be a string or integer")
        return int(value)

    @staticmethod
    def _normalize_coord(value: object, name: str) -> Coord:
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError(f"{name} must be a 2-tuple of integers")
        x, y = value
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError(f"{name} coordinates must be integers")
        return x, y

    def _validate(self) -> None:
        if self.width < 1 or self.height < 1:
            raise MazeGenerationError("Maze dimensions must be positive")
        for name, point in (("entry", self.entry), ("exit", self.exit)):
            x, y = point
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise MazeGenerationError(
                    f"{name} must be inside the maze bounds"
                )
        if self.entry == self.exit:
            raise MazeGenerationError("entry and exit must be different")

    def generate(self) -> MazeGenerator:
        """Generate (or regenerate) the maze.

        Returns
        -------
        MazeGenerator
            The generator itself, to allow method chaining.

        Raises
        ------
        MazeGenerationError
            If the maze dimensions are invalid, the entry or exit is
            outside the maze, the entry and exit are identical, the
            42 pattern cannot fit, or no valid path exists between the
            entry and exit.
        """
        self._validate()

        self.pattern_skipped = False
        self.pattern_warning = None

        if (
            self.width <= len(_BASE_42_PATTERN[0])
            or self.height <= len(_BASE_42_PATTERN)
        ):
            blocked_cells: set[Coord] = set()
            self.pattern_skipped = True
            self.pattern_warning = (
                f"Maze is {self.width}x{self.height}, which is too small to "
                f"fit the {len(_BASE_42_PATTERN[0])}x{len(_BASE_42_PATTERN)} "
                "\"42\" pattern and create a connected maze; "
                "generating the maze without it."
            )
            print(self.pattern_warning, file=sys.stderr)
        else:
            blocked_cells = self._build_42_pattern(self.width, self.height)

        if self.entry in blocked_cells or self.exit in blocked_cells:
            raise MazeGenerationError(
                "entry and exit must not be inside the 42 pattern"
            )

        grid = self._generate_connected_maze(
            self.width, self.height, blocked_cells, self.seed
        )
        if not self.perfect:
            self._add_extra_opening(grid, blocked_cells, self.seed)

        self._blocked_cells = blocked_cells
        self._grid = grid
        self._path = self._shortest_path(grid, self.entry, self.exit)
        return self

    @property
    def grid(self) -> Grid:
        """The maze as a 2D list of ints (``grid[y][x]``).

        Returns
        -------
        list[list[int]]
            The generated maze grid, where each cell stores closed
            walls as a bitmask.

        Raises
        ------
        MazeGenerationError
            If the maze cannot be generated for the current settings.

        Each cell is a bitmask of :class:`Direction` flags indicating
        which walls are present (1=North, 2=East, 4=South, 8=West;
        e.g. ``0xF``/15 means all four walls are closed).
        Generates the maze automatically on first access.
        """
        if self._grid is None:
            self.generate()
        assert self._grid is not None
        return self._grid

    @property
    def blocked_cells(self) -> set[Coord]:
        """Coordinates reserved by the carved "42" pattern, if one was used.

        Returns
        -------
        set[tuple[int, int]]
            The coordinates kept fully closed by the pattern, or an
            empty set if the pattern was skipped.
        """
        if self._grid is None:
            self.generate()
        return self._blocked_cells

    def solution(self) -> str:
        """Return the shortest path from ``entry`` to ``exit``.

        Returns
        -------
        str
            A string of direction letters (``N``, ``E``, ``S``, ``W``)
            describing the shortest path.

        Raises
        ------
        MazeGenerationError
            If the maze cannot be generated or no path exists.

        The result is a string of direction letters (``N``, ``E``,
        ``S``, ``W``), e.g. ``"EESSW"``, describing the moves to take
        from ``entry`` to reach ``exit``. Generates the maze
        automatically on first access.
        """
        if self._path is None:
            self.generate()
        assert self._path is not None
        return self._path

    def solution_coords(self) -> list[Coord]:
        """Return the solution path as a list of ``(x, y)`` coordinates.

        Returns
        -------
        list[tuple[int, int]]
            The path coordinates, starting with ``entry`` and ending
            with ``exit``.

        The list starts at ``entry`` and ends at ``exit`` (inclusive),
        using the same coordinate order as the constructor and the
        in-memory maze representation.
        """
        deltas = {d[4]: (d[0], d[1]) for d in _DIRECTIONS}
        x, y = self.entry
        coords = [(x, y)]
        for letter in self.solution():
            dx, dy = deltas[letter]
            x, y = x + dx, y + dy
            coords.append((x, y))
        return coords

    def to_dict(self) -> dict:
        """Return the full maze structure as a plain ``dict``.

        Returns
        -------
        dict
            A dictionary containing the maze parameters, grid, blocked
            cells, solution, and pattern status flags.
        """
        return {
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "perfect": self.perfect,
            "entry": self.entry,
            "exit": self.exit,
            "grid": [row[:] for row in self.grid],
            "blocked_cells": sorted(self.blocked_cells),
            "solution": self.solution(),
            "pattern_skipped": self.pattern_skipped,
            "pattern_warning": self.pattern_warning,
        }

    def save(self, output_file: str) -> None:
        """Write the maze to ``output_file`` using the reference text
        format: one hex digit per cell (row by row), a blank line, the
        entry coordinates, the exit coordinates, and the solution path.

        Parameters
        ----------
        output_file:
            Path to the file that should receive the maze text format.

        Returns
        -------
        None
            This method writes the file as a side effect.

        Raises
        ------
        OSError
            If the file cannot be opened or written.

        Coordinates are written as ``x,y`` to match the generator's
        internal coordinate order.
        """
        grid = self.grid
        with open(output_file, "w", newline="\n") as file:
            for row in grid:
                file.write("".join(f"{cell:X}" for cell in row) + "\n")
            file.write("\n")
            file.write(f"{self.entry[0]},{self.entry[1]}\n")
            file.write(f"{self.exit[0]},{self.exit[1]}\n")
            file.write(self.solution() + "\n")

    @staticmethod
    def _build_42_pattern(width: int, height: int) -> set[Coord]:
        pattern_width = min(width, len(_BASE_42_PATTERN[0]))
        pattern_height = min(height, len(_BASE_42_PATTERN))
        offset_x = (width - pattern_width) // 2
        offset_y = (height - pattern_height) // 2

        blocked_cells: set[Coord] = set()
        for row_index in range(pattern_height):
            row = _BASE_42_PATTERN[row_index]
            for col_index in range(pattern_width):
                if row[col_index] == "#":
                    blocked_cells.add(
                        (offset_x + col_index, offset_y + row_index)
                    )
        return blocked_cells

    @staticmethod
    def _generate_connected_maze(
        width: int, height: int, blocked_cells: set[Coord], seed: int
    ) -> Grid:
        grid: Grid = [[0xF for _ in range(width)] for _ in range(height)]
        allowed_cells: set[Coord] = {
            (x, y)
            for y in range(height)
            for x in range(width)
            if (x, y) not in blocked_cells
        }
        if not allowed_cells:
            raise MazeGenerationError(
                "Maze cannot be entirely occupied by the 42 pattern"
            )

        rng = random.Random(seed)
        start = min(allowed_cells)
        stack: list[Coord] = [start]
        visited: set[Coord] = {start}

        while stack:
            x, y = stack[-1]
            neighbours: list[tuple[Coord, Direction, Direction]] = []
            for dx, dy, wall, opposite_wall, _ in _DIRECTIONS:
                neighbour = (x + dx, y + dy)
                if neighbour in allowed_cells and neighbour not in visited:
                    neighbours.append((neighbour, wall, opposite_wall))

            if not neighbours:
                stack.pop()
                continue

            neighbour, wall, opposite_wall = rng.choice(neighbours)
            nx, ny = neighbour
            grid[y][x] &= ~wall
            grid[ny][nx] &= ~opposite_wall
            visited.add(neighbour)
            stack.append(neighbour)

        if visited != allowed_cells:
            raise MazeGenerationError(
                "42 pattern disconnects the maze at the chosen size"
            )

        for blocked_x, blocked_y in blocked_cells:
            grid[blocked_y][blocked_x] = 0xF

        return grid

    @classmethod
    def _add_extra_opening(
        cls, grid: Grid, blocked_cells: set[Coord], seed: int
    ) -> None:
        height = len(grid)
        width = len(grid[0])
        candidates: list[tuple[int, int, int, int, Direction, Direction]] = []

        for y in range(height):
            for x in range(width):
                if (x, y) in blocked_cells:
                    continue
                for dx, dy, wall, opposite_wall, _ in _DIRECTIONS[1:3]:
                    neighbour_x = x + dx
                    neighbour_y = y + dy
                    if not (
                        0 <= neighbour_x < width and 0 <= neighbour_y < height
                    ):
                        continue
                    if (neighbour_x, neighbour_y) in blocked_cells:
                        continue
                    if (
                        grid[y][x] & wall
                        and grid[neighbour_y][neighbour_x] & opposite_wall
                    ):
                        candidates.append((
                            x, y, neighbour_x, neighbour_y, wall, opposite_wall
                        ))

        if not candidates:
            return

        rng = random.Random(seed ^ 0x9E3779B9)
        rng.shuffle(candidates)

        for x, y, neighbour_x, neighbour_y, wall, opposite_wall in candidates:
            grid[y][x] &= ~wall
            grid[neighbour_y][neighbour_x] &= ~opposite_wall
            if not cls._has_three_by_three_open_area(grid):
                return
            grid[y][x] |= wall
            grid[neighbour_y][neighbour_x] |= opposite_wall

    @staticmethod
    def _has_three_by_three_open_area(grid: Grid) -> bool:
        height = len(grid)
        width = len(grid[0])

        for top in range(height - 2):
            for left in range(width - 2):
                fully_open = True

                for row in range(3):
                    for col in range(2):
                        cell = grid[top + row][left + col]
                        neighbour = grid[top + row][left + col + 1]
                        if cell & Direction.EAST or neighbour & Direction.WEST:
                            fully_open = False
                            break
                    if not fully_open:
                        break

                if not fully_open:
                    continue

                for row in range(2):
                    for col in range(3):
                        cell = grid[top + row][left + col]
                        neighbour = grid[top + row + 1][left + col]
                        if (
                            cell & Direction.SOUTH or
                            neighbour & Direction.NORTH
                        ):
                            fully_open = False
                            break
                    if not fully_open:
                        break

                if fully_open:
                    return True

        return False

    @staticmethod
    def _shortest_path(grid: Grid, entry: Coord, exit_: Coord) -> str:
        height = len(grid)
        width = len(grid[0])
        queue: deque[Coord] = deque([entry])
        previous: dict[Coord, tuple[Coord, str]] = {}
        seen: set[Coord] = {entry}

        while queue:
            x, y = queue.popleft()
            if (x, y) == exit_:
                break

            cell_walls = grid[y][x]
            for dx, dy, wall, opposite_wall, letter in _DIRECTIONS:
                if cell_walls & wall:
                    continue
                neighbour_x = x + dx
                neighbour_y = y + dy
                if not (
                    0 <= neighbour_x < width and 0 <= neighbour_y < height
                ):
                    continue
                if grid[neighbour_y][neighbour_x] & opposite_wall:
                    continue
                neighbour = (neighbour_x, neighbour_y)
                if neighbour in seen:
                    continue
                seen.add(neighbour)
                previous[neighbour] = ((x, y), letter)
                queue.append(neighbour)

        if exit_ not in previous and entry != exit_:
            raise MazeGenerationError(
                "No valid path exists between entry and exit"
            )

        path_letters: list[str] = []
        current = exit_
        while current != entry:
            current, letter = previous[current]
            path_letters.append(letter)
        path_letters.reverse()
        return "".join(path_letters)
