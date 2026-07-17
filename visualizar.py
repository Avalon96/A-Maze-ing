from maze_generator import MazeGenerator


def draw(maze: MazeGenerator) -> None:
    grid = maze.grid
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            cell = grid[y][x]
            if cell & 2:
                print("|", end="")
            else:
                print(" ", end ="")
            
        print()
        


if __name__ == "__main__":
    m = MazeGenerator(20, 15, entry=(0, 0), exit=(19, 14), seed=42)
    m.generate()
    draw(m)