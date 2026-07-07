import random
from collections import deque
from enum import IntFlag

Coord = tuple[int, int]
Grid = list[list[int]]


class Direction(IntFlag):
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
    "#..#..####",
    "#..#....#.",
    "####..####",
    "...#..#...",
    "...#..####",
)


def _int_from_config(value: str | int | Coord | bool, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError(f"{name} must be a string or integer")
    return int(value)


def generate_maze(
        config: dict[str, str | int | Coord | bool]
        ) -> None:
    width: int = _int_from_config(config["WIDTH"], "WIDTH")
    height: int = _int_from_config(config["HEIGHT"], "HEIGHT")
    rng: int = random.randint(1, 1024)
    seed: int = _int_from_config(config.get("SEED", rng), "SEED")
    perfect: bool = bool(config["PERFECT"])
    entry: Coord = _normalize_coord(config["ENTRY"])
    exit_: Coord = _normalize_coord(config["EXIT"])
    output_file: str = str(config["OUTPUT_FILE"])

    _validate_dimensions(width, height)
    _validate_points(width, height, entry, exit_)

    blocked_cells: set[Coord] = _build_42_pattern(width, height)
    if entry in blocked_cells or exit_ in blocked_cells:
        raise ValueError("Entry and exit must not be inside the 42 pattern")

    grid: Grid = _generate_connected_maze(width, height, blocked_cells, seed)
    if not perfect:
        _add_extra_opening(grid, blocked_cells, seed)
    path: str = _shortest_path(grid, entry, exit_)

    with open(output_file, "w", newline="\n") as file:
        for row in grid:
            file.write("".join(f"{cell:X}" for cell in row) + "\n")
        file.write("\n")
        file.write(f"{entry[0]},{entry[1]}\n")
        file.write(f"{exit_[0]},{exit_[1]}\n")
        file.write(path + "\n")


def _normalize_coord(value: object) -> Coord:
    if not isinstance(value, tuple) or len(value) != 2:
        raise ValueError("Configuration coordinates must contain two values")
    x: int = value[0]
    y: int = value[1]
    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError("Configuration coordinates must be integers")
    return x, y


def _validate_dimensions(width: int, height: int) -> None:
    if width < 1 or height < 1:
        raise ValueError("Maze dimensions must be positive")


def _validate_points(
        width: int,
        height: int,
        entry: Coord,
        exit_: Coord,
        ) -> None:
    for name, point in (("ENTRY", entry), ("EXIT", exit_)):
        x: int = point[0]
        y: int = point[1]
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(f"{name} must be inside the maze bounds")
    if entry == exit_:
        raise ValueError("ENTRY and EXIT must be different")


def _build_42_pattern(width: int, height: int) -> set[Coord]:
    pattern_width: int = min(width, len(_BASE_42_PATTERN[0]))
    pattern_height: int = min(height, len(_BASE_42_PATTERN))
    offset_x: int = (width - pattern_width) // 2
    offset_y: int = (height - pattern_height) // 2

    blocked_cells: set[Coord] = set()
    for row_index in range(pattern_height):
        row: str = _BASE_42_PATTERN[row_index]
        for col_index in range(pattern_width):
            if row[col_index] == "#":
                blocked_cells.add((offset_x + col_index, offset_y + row_index))
    return blocked_cells


def _generate_connected_maze(
        width: int,
        height: int,
        blocked_cells: set[Coord],
        seed: int,
        ) -> Grid:
    grid: Grid = [[0xF for _ in range(width)] for _ in range(height)]
    allowed_cells: set[Coord] = {
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in blocked_cells
    }
    if not allowed_cells:
        raise ValueError("Maze cannot be entirely occupied by the 42 pattern")

    rng: random.Random = random.Random(seed)
    start: Coord = min(allowed_cells)
    stack: list[Coord] = [start]
    visited: set[Coord] = {start}

    while stack:
        x: int = stack[-1][0]
        y: int = stack[-1][1]
        neighbours: list[tuple[Coord, Direction, Direction]] = []
        for dx, dy, wall, opposite_wall, _ in _DIRECTIONS:
            neighbour: Coord = (x + dx, y + dy)
            if neighbour in allowed_cells and neighbour not in visited:
                neighbours.append((neighbour, wall, opposite_wall))

        if not neighbours:
            stack.pop()
            continue

        neighbour, wall, opposite_wall = rng.choice(neighbours)
        nx: int = neighbour[0]
        ny: int = neighbour[1]
        grid[y][x] &= ~wall
        grid[ny][nx] &= ~opposite_wall
        visited.add(neighbour)
        stack.append(neighbour)

    if visited != allowed_cells:
        raise ValueError("42 pattern disconnects the maze at the chosen size")

    for blocked_x, blocked_y in blocked_cells:
        grid[blocked_y][blocked_x] = 0xF

    return grid


def _add_extra_opening(
        grid: Grid,
        blocked_cells: set[Coord],
        seed: int,
        ) -> None:
    height: int = len(grid)
    width: int = len(grid[0])
    candidates: list[tuple[int, int, int, int, Direction, Direction]] = []

    for y in range(height):
        for x in range(width):
            if (x, y) in blocked_cells:
                continue
            for dx, dy, wall, opposite_wall, _ in _DIRECTIONS[1:3]:
                neighbour_x: int = x + dx
                neighbour_y: int = y + dy
                if not (
                        0 <= neighbour_x < width
                        and 0 <= neighbour_y < height
                        ):
                    continue
                if (neighbour_x, neighbour_y) in blocked_cells:
                    continue
                if (
                        grid[y][x] & wall
                        and grid[neighbour_y][neighbour_x] & opposite_wall
                        ):
                    candidates.append(
                        (x, y, neighbour_x, neighbour_y, wall, opposite_wall)
                    )

    if not candidates:
        return

    rng: random.Random = random.Random(seed ^ 0x9E3779B9)
    rng.shuffle(candidates)

    for x, y, neighbour_x, neighbour_y, wall, opposite_wall in candidates:
        grid[y][x] &= ~wall
        grid[neighbour_y][neighbour_x] &= ~opposite_wall
        if not _has_three_by_three_open_area(grid):
            return
        grid[y][x] |= wall
        grid[neighbour_y][neighbour_x] |= opposite_wall


def _has_three_by_three_open_area(grid: Grid) -> bool:
    height: int = len(grid)
    width: int = len(grid[0])

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
                    if cell & Direction.SOUTH or neighbour & Direction.NORTH:
                        fully_open = False
                        break
                if not fully_open:
                    break

            if fully_open:
                return True

    return False


def _shortest_path(grid: Grid, entry: Coord, exit_: Coord) -> str:
    height: int = len(grid)
    width: int = len(grid[0])
    queue: deque[Coord] = deque([entry])
    previous: dict[Coord, tuple[Coord, str]] = {}
    seen: set[Coord] = {entry}

    while queue:
        cell: Coord = queue.popleft()
        x: int = cell[0]
        y: int = cell[1]
        if (x, y) == exit_:
            break

        cell_walls: int = grid[y][x]
        for dx, dy, wall, opposite_wall, letter in _DIRECTIONS:
            if cell_walls & wall:
                continue
            neighbour_x: int = x + dx
            neighbour_y: int = y + dy
            if not (0 <= neighbour_x < width and 0 <= neighbour_y < height):
                continue
            if grid[neighbour_y][neighbour_x] & opposite_wall:
                continue
            neighbour: Coord = (neighbour_x, neighbour_y)
            if neighbour in seen:
                continue
            seen.add(neighbour)
            previous[neighbour] = ((x, y), letter)
            queue.append(neighbour)

    if exit_ not in previous and entry != exit_:
        raise ValueError("No valid path exists between ENTRY and EXIT")

    path_letters: list[str] = []
    current: Coord = exit_
    while current != entry:
        entry_data: tuple[Coord, str] = previous[current]
        current = entry_data[0]
        path_letter: str = entry_data[1]
        path_letters.append(path_letter)
    path_letters.reverse()
    return "".join(path_letters)
