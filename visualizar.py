from maze_generator import MazeGenerator

def draw(maze: MazeGenerator) -> None:
    grid = maze.grid
    entry = maze.entry
    cell_exit = maze.exit
    solution_path = maze.solution_coords()
    cell_blocked = maze.blocked_cells
    closing = "\033[m"
    red = "\033[31m"
    blue = "\033[34m"
    green = "\033[32m"

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
                print(blue + "E " + closing, end="")
            elif (x, y) == cell_exit:
                print(blue + "X " + closing, end="")
            elif (x, y) in solution_path:
                print(red + "* " + closing,end="")
            elif (x, y) in cell_blocked:
                print(green + "# " + closing, end="")
            else:
                print("  ", end="")
        print("|")

    for x in range(len(grid[0])):
        print("+--", end="")    


if __name__ == "__main__":
    m = MazeGenerator(20, 15, entry=(0, 0), exit=(19, 14), seed=42)
    m.generate()
    draw(m)