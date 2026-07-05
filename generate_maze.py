import random
from collections import deque


Coord = tuple[int, int]
Grid = list[list[int]]

# y, x, wall, opposite_wall, letter
_DIRECTIONS: tuple[tuple[int, int, int, int, str], ...] = (
    (-1, 0, 1, 4, "N"),
    (0, 1, 2, 8, "E"),
    (1, 0, 4, 1, "S"),
    (0, -1, 8, 2, "W"),
)

_BASE_42_PATTERN: tuple[str, ...] = (
    "#..#..####",
    "#..#....#.",
    "####..####",
    "...#..#...",
    "...#..####",
)


def generate_maze(
        config: dict[str, str | int | tuple[int, int] | bool]
        ) -> None:
    width: int = int(config["WIDTH"])
    height: int = int(config["HEIGHT"])
    rng: int = random.randint(1, 1024)
    seed: int = int(config.get("SEED", rng))
    perfect: bool = bool(config["PERFECT"])
    entry: Coord = _normalize_coord(config["ENTRY"])
    exit_: Coord = _normalize_coord(config["EXIT"])
    output_file: str = str(config["OUTPUT_FILE"])

    _validate_dimensions(width, height)
    _validate_points(width, height, entry, exit_)

    blocked_cells = _build_42_pattern(width, height)
    if entry in blocked_cells or exit_ in blocked_cells:
        raise ValueError("Entry and exit must not be inside the 42 pattern")

    grid = _generate_connected_maze(width, height, blocked_cells, seed)
    if not perfect:
        _add_extra_opening(grid, blocked_cells, seed)
    path = _shortest_path(grid, entry, exit_)

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
    x, y = value
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
        x, y = point
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(f"{name} must be inside the maze bounds")
    if entry == exit_:
        raise ValueError("ENTRY and EXIT must be different")


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
                blocked_cells.add((offset_x + col_index, offset_y + row_index))
    return blocked_cells


def _generate_connected_maze(
        width: int,
        height: int,
        blocked_cells: set[Coord],
        seed: int,
        ) -> Grid:
    grid: Grid = [[0xF for _ in range(width)] for _ in range(height)]
    allowed_cells = {
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in blocked_cells
    }
    if not allowed_cells:
        raise ValueError("Maze cannot be entirely occupied by the 42 pattern")

    rng = random.Random(seed)
    start = min(allowed_cells)
    stack: list[Coord] = [start]
    visited: set[Coord] = {start}

    while stack:
        x, y = stack[-1]
        neighbours: list[tuple[Coord, int, int]] = []
        for dy, dx, wall, opposite_wall, _ in _DIRECTIONS:
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
        raise ValueError("42 pattern disconnects the maze at the chosen size")

    for blocked_x, blocked_y in blocked_cells:
        grid[blocked_y][blocked_x] = 0xF

    return grid


def _add_extra_opening(
        grid: Grid,
        blocked_cells: set[Coord],
        seed: int,
        ) -> None:
    height = len(grid)
    width = len(grid[0])
    candidates: list[tuple[int, int, int, int, int, int]] = []

    for y in range(height):
        for x in range(width):
            if (x, y) in blocked_cells:
                continue
            for dy, dx, wall, opposite_wall, _ in _DIRECTIONS[1:3]:
                neighbour_x = x + dx
                neighbour_y = y + dy
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

    rng = random.Random(seed ^ 0x9E3779B9)
    rng.shuffle(candidates)

    for x, y, neighbour_x, neighbour_y, wall, opposite_wall in candidates:
        grid[y][x] &= ~wall
        grid[neighbour_y][neighbour_x] &= ~opposite_wall
        if not _has_three_by_three_open_area(grid):
            return
        grid[y][x] |= wall
        grid[neighbour_y][neighbour_x] |= opposite_wall


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
                    if cell & 2 or neighbour & 8:
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
                    if cell & 4 or neighbour & 1:
                        fully_open = False
                        break
                if not fully_open:
                    break

            if fully_open:
                return True

    return False


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

        cell = grid[y][x]
        for dy, dx, wall, opposite_wall, letter in _DIRECTIONS:
            if cell & wall:
                continue
            neighbour_x = x + dx
            neighbour_y = y + dy
            if not (0 <= neighbour_x < width and 0 <= neighbour_y < height):
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
        raise ValueError("No valid path exists between ENTRY and EXIT")

    path_letters: list[str] = []
    current = exit_
    while current != entry:
        current, letter = previous[current]
        path_letters.append(letter)
    path_letters.reverse()
    return "".join(path_letters)
