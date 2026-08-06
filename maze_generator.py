from __future__ import annotations
import random
import sys
from collections import deque
from enum import IntFlag


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

Coord = tuple[int, int]
Grid = list[list[int]]
DeadEnd = tuple[int, int, list[tuple[int, int, Direction, Direction]]]
OpenableWalls = list[tuple[int, int, Direction, Direction]]
Candidate = list[tuple[int, int, int, int, Direction, Direction]]


class MazeGenerator:
    """Generate rectangular mazes and query their structure and solution.

    Parameters
    ----------
    width, height:
        Size of the maze, in cells. Both must be positive integers.
    entry, exit:
        `(x, y)` coordinates (0-indexed, `x` is the column and `y`
        is the row) of the maze entry and exit. They must lie inside
        the maze bounds and be different from each other.
    seed:
        Optional integer used to seed the internal random number
        generator. Using the same seed (and the same other parameters)
        always produces the same maze. If omitted, a random seed is
        chosen automatically.
    perfect:
        If `True` (the default) the maze is "perfect": there is
        exactly one path between any two cells. If `False`, all
        dead-ends are removed and at least two loops are added.

    Raises
    ------
    ValueError
        If width, height, entry, exit, or seed cannot be converted to
        valid values.

    Notes
    -----
    Very small mazes may skip the `_BASE_42_PATTERN` entirely when the fixed
    pattern would not fit without breaking connectivity.

    The maze is not generated until `generate` is called.
    """

    def __init__(
        self,
        width: int,
        height: int,
        *,
        entry: Coord,
        exit_: Coord,
        seed: int | None = None,
        perfect: bool = True
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.seed = (
            seed if seed is not None
            else random.randint(1, 2**31 - 1)
        )
        self.perfect = perfect

        self._grid: Grid | None = None
        self._path: str | None = None
        self._blocked_cells: set[Coord] = set()
        self.pattern_skipped: bool = False
        self.pattern_warning: str | None = None

    def _validate(self) -> None:
        if self.width < 1 or self.height < 1:
            raise MazeGenerationError("Maze dimensions must be positive")
        for name, point in (("entry", self.entry), ("exit", self.exit_)):
            x: int = point[0]
            y: int = point[1]
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise MazeGenerationError(
                    f"{name} must be inside the maze bounds"
                )
        if self.entry == self.exit_:
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
            `_BASE_42_PATTERN` cannot be placed, or no valid path exists
            between the entry and exit.
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
            try:
                blocked_cells = self._build_42_pattern(
                    self.width, self.height, self.entry, self.exit_
                )
            except MazeGenerationError as e:
                blocked_cells = set()
                self.pattern_skipped = True
                self.pattern_warning = f"{e}; generating the maze without it."
                print(self.pattern_warning, file=sys.stderr)

        if self.entry in blocked_cells or self.exit_ in blocked_cells:
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
        self._path = self._shortest_path(grid, self.entry, self.exit_)
        return self

    @property
    def grid(self) -> Grid:
        """The maze as a 2D list of ints (`grid[y][x]`).

        Each cell is a bitmask of :class:`Direction` flags indicating
        which walls are present (1=North, 2=East, 4=South, 8=West;
        e.g. `0xF`/15 means all four walls are closed).
        Generates the maze automatically on first access.

        Returns
        -------
        list[list[int]]
            The generated maze grid, where each cell stores closed
            walls as a bitmask.

        Raises
        ------
        MazeGenerationError
            If the maze cannot be generated for the current settings.

        """
        if self._grid is None:
            self.generate()
        assert self._grid is not None
        return self._grid

    @property
    def blocked_cells(self) -> set[Coord]:
        """Coordinates reserved by the carved `_BASE_42_PATTERN`,
        if one was used.

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
        """Return the shortest path from `entry` to `exit_`.

        The result is a string of direction letters (`N`, `E`, `S`, `W`),
        e.g. `"EESSW"`, describing the moves to take from `entry` to `exit_`.
        Generates the maze automatically on first access.

        Returns
        -------
        str
            A string of direction letters (`N`, `E`, `S`, `W`)
            describing the shortest path.

        Raises
        ------
        MazeGenerationError
            If the maze cannot be generated or no path exists.

        """
        if self._path is None:
            self.generate()
        assert self._path is not None
        return self._path

    def solution_coords(self) -> list[Coord]:
        """Return the solution path as a list of `(x, y)` coordinates.

        Returns
        -------
        list[tuple[int, int]]
            The path coordinates, starting with `entry` and ending
            with `exit_`.

        The list starts at `entry` and ends at `exit_` (inclusive),
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

    def save(self, output_file: str) -> None:
        """Write the maze to `output_file` using the reference text
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

        Coordinates are written as `x,y` to match the generator's
        internal coordinate order.
        """
        grid = self.grid
        with open(output_file, "w", newline="\n") as file:
            for row in grid:
                file.write("".join(f"{cell:X}" for cell in row) + "\n")
            file.write("\n")
            file.write(f"{self.entry[0]},{self.entry[1]}\n")
            file.write(f"{self.exit_[0]},{self.exit_[1]}\n")
            file.write(self.solution() + "\n")

    @staticmethod
    def _build_42_pattern(
        width: int, height: int, entry: Coord, exit_: Coord
    ) -> set[Coord]:
        """Finds a valid placement for the `_BASE_42_PATTERN` in the maze
        and returns the coordinates of the cells that are blocked by it.

        Parameters
        ----------
        width, height:
            The dimensions of the maze.
        entry, exit_:
            The coordinates of the maze entry and exit.

        Returns
        -------
        set[tuple[int, int]]
            The coordinates of the cells that are blocked
            by the `_BASE_42_PATTERN`

        Raises
        ------
        MazeGenerationError
            If the `_BASE_42_PATTERN` cannot be placed without
            blocking the entry, exit, or center.
        """
        pattern_width: int = min(width, len(_BASE_42_PATTERN[0]))
        pattern_height: int = min(height, len(_BASE_42_PATTERN))

        key_cells: set[Coord] = {
            (0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1),
            (width // 2, height // 2), entry, exit_
        }

        offsets: list[tuple[int, int, int]] = []
        for y in range(height - pattern_height + 1):
            for x in range(width - pattern_width + 1):
                center_x: int = x + pattern_width // 2
                center_y: int = y + pattern_height // 2

                dist: int = \
                    abs(center_x - width // 2) + abs(center_y - height // 2)
                offsets.append((dist, x, y))

        offsets.sort(key=lambda item: item[0])

        for _, x, y in offsets:
            blocked_cells: set[Coord] = set()
            for row_index in range(pattern_height):
                row: str = _BASE_42_PATTERN[row_index]
                for col_index in range(pattern_width):
                    if row[col_index] == "#":
                        blocked_cells.add((x + col_index, y + row_index))
            if not (blocked_cells & key_cells):
                return blocked_cells

        raise MazeGenerationError(
            "42 pattern cannot be placed without blocking entry/exit/center"
        )

    @staticmethod
    def _generate_connected_maze(
        width: int, height: int, blocked_cells: set[Coord], seed: int
    ) -> Grid:
        """Generate a perfect maze using a DFS algorithm.

        Parameters
        ----------
        width, height:
            The dimensions of the maze.
        blocked_cells:
            The coordinates of the cells that are blocked by the
            `_BASE_42_PATTERN`.
        seed:
            The random seed for reproducible maze generation.

        Returns
        -------
        Grid
            The generated maze grid, where each cell stores
            closed walls as a bitmask.

        Raises
        ------
        MazeGenerationError
            If the maze cannot be generated due to the blocked cells
        """
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

        rng: random.Random = random.Random(seed)
        start: Coord = min(allowed_cells)
        stack: list[Coord] = [start]
        visited: set[Coord] = {start}

        while stack:
            x: int
            y: int
            x, y = stack[-1]
            neighbours: list[tuple[Coord, Direction, Direction]] = []
            for dx, dy, wall, opposite_wall, _ in _DIRECTIONS:
                neighbour: Coord = (x + dx, y + dy)
                if neighbour in allowed_cells and neighbour not in visited:
                    neighbours.append((neighbour, wall, opposite_wall))

            if not neighbours:
                stack.pop()
                continue

            neighbour, wall, opposite_wall = rng.choice(neighbours)
            nx: int
            ny: int
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
        """Remove some extra walls to reduce dead ends in the maze.

        Repeatedly scans the grid for "dead end" cells (cells with exactly
        three closed walls) and, where possible, knocks down one of their
        walls into an unblocked neighbour. A candidate wall is only removed
        if doing so does not create a fully open 3x3 area in the grid.
        If fewer than two walls could be removed via dead ends,
        falls back to trying random east/west openings between arbitrary
        adjacent cells until at least two walls have been removed
        (or no valid candidates remain). The grid is mutated in place.

        Parameters
        ----------
        grid:
            The maze grid to modify in place.
        blocked_cells:
            The coordinates of cells blocked by the `_BASE_42_PATTERN`;
            these are never modified or used as neighbours.
        seed:
            The random seed (XORed with a fixed constant) used to make the
            extra-opening process reproducible and independent from the
            seed used for the initial maze generation.
        """
        height: int = len(grid)
        width: int = len(grid[0])
        rng: random.Random = random.Random(seed ^ 0x9E3779B9)

        def get_real_dead_ends() -> list[DeadEnd]:
            """Find all dead ends that can potentially be connected
            to a valid neighbour.
            """
            dead_ends: list[DeadEnd] = []
            for y in range(height):
                for x in range(width):
                    if (x, y) in blocked_cells:
                        continue

                    if bin(grid[y][x] & 0xF).count("1") == 3:
                        openable: OpenableWalls = []
                        for dx, dy, wall, opposite_wall, _ in _DIRECTIONS:
                            if grid[y][x] & wall:
                                nx: int = x + dx
                                ny: int = y + dy
                                if 0 <= nx < width and 0 <= ny < height:
                                    if (nx, ny) not in blocked_cells:
                                        openable.append(
                                            (nx, ny, wall, opposite_wall)
                                        )
                        if openable:
                            dead_ends.append((x, y, openable))
            return dead_ends

        walls_removed: int = 0

        while True:
            dead_ends = get_real_dead_ends()
            if not dead_ends:
                break

            rng.shuffle(dead_ends)
            changed: bool = False

            for x, y, openable in dead_ends:
                if bin(grid[y][x] & 0xF).count("1") != 3:
                    continue

                rng.shuffle(openable)
                for nx, ny, wall, opposite_wall in openable:
                    grid[y][x] &= ~wall
                    grid[ny][nx] &= ~opposite_wall

                    if cls._has_three_by_three_open_area(grid):
                        grid[y][x] |= wall
                        grid[ny][nx] |= opposite_wall
                    else:
                        changed = True
                        walls_removed += 1
                        break

            if not changed:
                break

        if walls_removed < 2:
            candidates: Candidate = []
            for y in range(height):
                for x in range(width):
                    if (x, y) in blocked_cells:
                        continue
                    for dx, dy, wall, opposite_wall, _ in _DIRECTIONS[1:3]:
                        if grid[y][x] & wall:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                if (nx, ny) not in blocked_cells:
                                    candidates.append(
                                        (x, y, nx, ny, wall, opposite_wall)
                                    )

            rng.shuffle(candidates)
            for x, y, nx, ny, wall, opposite_wall in candidates:
                if walls_removed >= 2:
                    break

                grid[y][x] &= ~wall
                grid[ny][nx] &= ~opposite_wall

                if cls._has_three_by_three_open_area(grid):
                    grid[y][x] |= wall
                    grid[ny][nx] |= opposite_wall
                else:
                    walls_removed += 1

    @staticmethod
    def _has_three_by_three_open_area(grid: Grid) -> bool:
        """Check whether the grid contains a fully open 3x3 block of cells.

        A 3x3 area is considered "fully open" when every internal wall
        between its cells (both horizontal, i.e. east/west, and vertical,
        i.e. north/south) has been removed, meaning a player could move
        freely within that 3x3 block in any direction.

        Parameters
        ----------
        grid:
            The maze grid to inspect.

        Returns
        -------
        bool
            True if any 3x3 fully open area exists in the grid,
            False otherwise.
        """
        height: int = len(grid)
        width: int = len(grid[0])

        for top in range(height - 2):
            for left in range(width - 2):
                fully_open: bool = True

                for row in range(3):
                    for col in range(2):
                        cell: int = grid[top + row][left + col]
                        neighbour: int = grid[top + row][left + col + 1]
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
        """Find the shortest path between two cells using a BFS algorithm.

        Parameters
        ----------
        grid:
            The maze grid to search, where each cell stores closed walls
            as a bitmask.
        entry:
            The coordinate of the starting cell.
        exit_:
            The coordinate of the destination cell.

        Returns
        -------
        str
            The sequence of direction letters (as defined by `_DIRECTIONS`)
            describing the shortest path from `entry` to `exit_`. Returns
            an empty string if `entry` equals `exit_`.

        Raises
        ------
        MazeGenerationError
            If no path exists between `entry` and `exit_`.
        """
        height: int = len(grid)
        width: int = len(grid[0])
        queue: deque[Coord] = deque([entry])
        previous: dict[Coord, tuple[Coord, str]] = {}
        seen: set[Coord] = {entry}

        while queue:
            x: int
            y: int
            x, y = queue.popleft()
            if (x, y) == exit_:
                break

            cell_walls: int = grid[y][x]
            for dx, dy, wall, opposite_wall, letter in _DIRECTIONS:
                if cell_walls & wall:
                    continue
                nx: int = x + dx
                ny: int = y + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                if grid[ny][nx] & opposite_wall:
                    continue
                neighbour: Coord = (nx, ny)
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
        current: Coord = exit_
        while current != entry:
            current, letter = previous[current]
            path_letters.append(letter)
        path_letters.reverse()
        return "".join(path_letters)
