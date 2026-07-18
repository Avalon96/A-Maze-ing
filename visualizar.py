from maze_generator import MazeGenerator

CLOSING = "\033[0m"
RED = "\033[31m"
BLUE = "\033[34m"
GREEN = "\033[32m"


def draw(maze: MazeGenerator, show_path: bool) -> None:
    grid = maze.grid
    entry = maze.entry
    cell_exit = maze.exit
    solution_path = maze.solution_coords()
    cell_blocked = maze.blocked_cells

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            cell = grid[y][x]
            print("+", end="")
            if cell & 1:
                print("--", end="")
            else:
                print("  ", end="")
        print("+")

        for x in range(len(grid[y])):
            cell = grid[y][x]
            if cell & 8:
                print("|", end="")
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
        print("|")

    for x in range(len(grid[0])):
        print("+--", end="")
    print("+")


def preference(maze: MazeGenerator) -> None:
    show_path = True

    while True:
        draw(maze, show_path)

        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show / Hide the shortest path")
        print("3. Rotate the wall colours")
        print("4. Quit")

        choice = input("Choice? (1-4): ")

        if choice == "1":
            maze = MazeGenerator(maze.width, maze.height,entry=maze.entry, exit=maze.exit,perfect=maze.perfect)
            maze.generate()
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            print()
        elif choice == "4":
            print("")
            break
        else:
            print("You entered incorrect information")


if __name__ == "__main__":
    m = MazeGenerator(20, 15, entry=(0, 0), exit=(19, 14), seed=42)
    m.generate()
    preference(m)