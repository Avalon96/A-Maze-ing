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

## Reusable Code

The main reusable component of this project is the `MazeGenerator` class.

It provides a configurable interface for generating mazes with different:
- dimensions
- entry and exit points
- random seeds
- generation modes

Example:

```python
(Code snippet for how to use)
```
# Instructions


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

AI was used to help choose algorithms, keep docstrings consistent with NumPy conventions, and identify edge cases for more robust error handling.

## TBD
• What part of your code is reusable, and how.

    • Your team and project management with:

        ◦ The roles of each team member.

        ◦ Your anticipated planning and how it evolved until the end

        ◦ What worked well and what could be improved
