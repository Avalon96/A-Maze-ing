*This project has been created as part of the 42 curriculum by aunverdi, bepolat*

# Description
This project is a Python package for generating and solving mazes. Its goal is to generate valid maze layouts following specific constraints, including entry/exit points, optional perfect maze generation, and Pac-Man compatible map rules. The package can be imported into other Python projects.

The package generates mazes using a Depth-First Search (DFS) algorithm, validates connectivity, places the 42 pattern when possible, and computes the shortest solution path between the entry and exit.

Features:
- Generate mazes of configurable sizes
- Support deterministic generation using seeds
- Generate perfect and non-perfect mazes
- Validate entry and exit positions
- Export generated mazes to a file
- Calculate the shortest solution path
- Visually show the generated maze

## Maze Generation Algorithm
The project uses a randomized DFS backtracking algorithm to generate mazes.

The algorithm starts from an initial cell and explores neighboring unvisited cells. When moving to a new cell, the wall between the current cell and the neighbor is removed. If the algorithm reaches a cell where no unvisited neighbors remain, it backtracks until another possible path is found.

This produces a connected maze where every accessible cell can be reached. When the `PERFECT` option is enabled, the generated accessible cells form a perfect maze, meaning there is exactly one path between any two connected cells, so only a single path exists between entry and exit.


## Why This Algorithm
DFS was chosen because it is a simple and efficient algorithm for generating perfect mazes. It naturally creates a connected maze without requiring a separate graph representation.

Another advantage is that the algorithm is deterministic when combined with a seed, allowing generated mazes to be reproduced for testing and debugging.

The algorithm is also flexible enough to support additional constraints, such as blocked cells created by the 42 pattern.

# Instructions
→→→ *Write how to install the package and use it*

## Reusable Code

The main reusable component of this project is the `MazeGenerator` class.

It provides a configurable interface for generating mazes with different:
- dimensions
- entry and exit points
- random seeds
- generation modes

Example:

```python
config_file_path = validate_parameters()
config = read_config_file(config_file_path)
validate_config(config)

maze = build_generator(config)
maze.generate()
maze.save(config["OUTPUT_FILE"])
preference(maze)
```

## Config File Format

Available options:

| Key         | Type            | Required | Description                            |
|-------------|-----------------|----------|----------------------------------------|
| WIDTH       | integer         | Yes      | Width of the maze in cells             |
| HEIGHT      | integer         | Yes      | Height of the maze in cells            |
| ENTRY       | x,y coordinates | Yes      | Starting position of the maze          |
| EXIT        | x,y coordinates | Yes      | Ending position of the maze            |
| OUTPUT_FILE | string          | Yes      | File where the generated maze is saved |
| PERFECT     | boolean         | Yes      | Whether to generate a perfect maze     |
| SEED        | integer         | No       | Seed used for deterministic generation |

# Resources
* [geeksforgeeks - DFS](https://www.geeksforgeeks.org/dsa/depth-first-search-or-dfs-for-a-graph/)
* [geeksforgeeks - BFS](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/)
* [PEP 257 – Docstring Conventions NumPy](https://numpydoc.readthedocs.io/en/latest/format.html)
* [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

AI was used to help choose algorithms, keep docstrings consistent with NumPy conventions, and identify edge cases for more robust error handling.

# Team & Project Management

## Team Roles
We divided the project to ensure we could work efficiently in parallel:
* **aunverdi**: Core Logic & Algorithms. Responsible for implementing the maze generation algorithms, the shortest-path finding logic, and data parsing.
* **bepolat**: Quality Assurance, Visualization & Architecture. Responsible for rigorous code testing, the visual rendering of the mazes, and structuring the project into a distributable package.

## Planning & Evolution
**Initial Plan:**
Initially, our timeline was structured around a sequential hand-off: aunverdi would rapidly develop the maze generation, allowing bepolat to research and implement the shortest-path algorithms. We planned to divide the remaining tasks organically once these core components were functional.

**How it Evolved:**
As development progressed, we realized that the algorithms for maze generation and path resolution shared significant foundational logic. To capitalize on this and avoid redundant work, aunverdi took ownership of both algorithms, as well as the parsing logic required to test them. 

This pivot shifted bepolat's focus. He took charge of Quality Assurance—testing the core logic for edge cases and faults—before moving on to handle the remaining architectural requirements: building the visual representation and packaging the project for distribution.

## Retrospective
**What Worked Well:**
* **Clear Architecture:** The strict separation of algorithmic logic and visual rendering allowed us to develop and test our components independently without causing merge conflicts.
* **Continuous Integration:** We tested the code regularly to ensure new commits didn't break existing functionality, which kept the codebase stable.

**What Could Be Improved:**
* **Time Estimation:** We underestimated the overall scope and time required to finish the project. This led to a tighter schedule than anticipated and left us with less buffer time to comfortably finalize everything at the end.