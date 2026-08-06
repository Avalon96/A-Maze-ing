from maze_generator import MazeGenerator

CLOSING = "\033[0m"
RED = "\033[31m"
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

WALL_COLOURS = [WHITE, BLUE, YELLOW, MAGENTA, CYAN]


def draw(maze: MazeGenerator, show_path: bool, wall_colour: str) -> None:
    """Draw the maze on the terminal.

    Every maze row takes two lines on screen: the first one draws the
    north walls, the second one draws the west walls together with what
    is inside each cell. The bottom border is added at the end. Entry,
    exit, the path and the "42" pattern each get their own colour.

    Parameters
    ----------
    maze : MazeGenerator
        The maze we are drawing.
    show_path : bool
        True if the solution path should be visible.
    wall_colour : str
        The colour used for the walls.
    """
    grid: list[list[int]] = maze.grid
    entry: tuple[int, int] = maze.entry
    cell_exit: tuple[int, int] = maze.exit_
    solution_path: list[tuple[int, int]] = maze.solution_coords()
    cell_blocked: set[tuple[int, int]] = maze.blocked_cells

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            cell: int = grid[y][x]
            print(wall_colour + "+" + CLOSING, end="")
            if cell & 1:
                print(wall_colour + "--" + CLOSING, end="")
            else:
                print("  ", end="")
        print(wall_colour + "+" + CLOSING)

        for x in range(len(grid[y])):
            cell = grid[y][x]
            if cell & 8:
                print(wall_colour + "|" + CLOSING, end="")
            else:
                print(" ", end="")

            if (x, y) == entry:
                print(BLUE + "E " + CLOSING, end="")
            elif (x, y) == cell_exit:
                print(BLUE + "X " + CLOSING, end="")
            elif show_path and (x, y) in solution_path:
                print(RED + "* " + CLOSING, end="")
            elif (x, y) in cell_blocked:
                print(GREEN + "# " + CLOSING, end="")
            else:
                print("  ", end="")
        print(wall_colour + "|" + CLOSING)

    for x in range(len(grid[0])):
        print(wall_colour + "+--" + CLOSING, end="")
    print(wall_colour + "+" + CLOSING)


def preference(maze: MazeGenerator, output_file: str) -> None:
    """Show the menu and keep asking the user what to do.

    The maze is drawn first, then the menu appears. The user can ask
    for a new maze, hide or show the path, change the wall colour, or
    quit. Anything else just prints a warning and the menu comes back.

    Parameters
    ----------
    maze : MazeGenerator
        The maze we start with. If the user picks "1", a new one takes
        its place with the same size and the same entry and exit.
    output_file : str
        The file where the maze is saved after every change.
    """
    show_path: bool = True
    colour_index: int = 0
    needs_redraw: bool = True

    while True:
        if needs_redraw:
            draw(maze, show_path, WALL_COLOURS[colour_index])
            maze.save(output_file)

            print("=== A-Maze-ing ===")
            print(f"Seed: {maze.seed}\n")

            print("1. Generate a random new maze")
            print("2. Generate a maze with given seed")
            print("3. Generate a maze with given dimensions")
            print("4. Show / Hide the shortest path")
            print("5. Rotate the wall colours")
            print("6. Quit")

        choice = input("Choice? (1-6): ")

        match choice:
            case "1":
                maze = MazeGenerator(
                    width=maze.width, height=maze.height,
                    entry=maze.entry, exit_=maze.exit_,
                    perfect=maze.perfect
                )
                maze.generate()
                needs_redraw = True
            case "2":
                while True:
                    try:
                        seed = int(input("Enter the seed for the new maze: "))
                        break
                    except ValueError:
                        print("Invalid seed. Please enter a valid integer.")
                maze = MazeGenerator(
                    width=maze.width, height=maze.height,
                    entry=maze.entry, exit_=maze.exit_,
                    perfect=maze.perfect, seed=seed
                )
                maze.generate()
                needs_redraw = True
            case "3":
                while True:
                    try:
                        width, height = map(int, input(
                            "Enter the width and height (W, H): ").split(",")
                        )
                        entry = (0, 0)
                        exit_ = (width - 1, height - 1)
                        break
                    except ValueError:
                        print("Invalid dimensions.")
                maze = MazeGenerator(
                    width=width, height=height,
                    entry=entry, exit_=exit_,
                    perfect=maze.perfect
                )
                maze.generate()
                needs_redraw = True
            case "4":
                show_path = not show_path
                needs_redraw = True
            case "5":
                colour_index = (colour_index + 1) % len(WALL_COLOURS)
                needs_redraw = True
            case "6":
                print("Bye!")
                needs_redraw = False
                break
            case _:
                print("Invalid choice.")
                needs_redraw = False
                continue
