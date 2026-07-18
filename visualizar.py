from maze_generator import MazeGenerator

def draw(maze: MazeGenerator) -> None:
    grid = maze.grid
    entry = maze.entry
    cell_exit = maze.exit
    solution_path = maze.solution_coords()

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
                print("E ", end="")
            elif (x, y) == cell_exit:
                print("X ", end="")
            elif (x, y) in solution_path:
                print("* ",end="")
            else:
                print("  ", end="")
        print("|")

    for x in range(len(grid[0])):
        print("+--", end="")    


if __name__ == "__main__":
    m = MazeGenerator(20, 15, entry=(0, 0), exit=(19, 14), seed=42)
    m.generate()
    draw(m)