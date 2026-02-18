from __future__ import annotations

import heapq
import math
import time
from dataclasses import dataclass
from typing import Callable, Iterable

Coord = tuple[int, int]
Grid = list[list[int]]
HeuristicFunc = Callable[[Coord, Coord], float]


@dataclass
class PathFindingResult:
    length: float
    path: list[Coord]
    visited_count: int
    visited_percent: float
    runtime_sec: float


def manhattan(a: Coord, b: Coord) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a: Coord, b: Coord) -> float:
    dr = a[0] - b[0]
    dc = a[1] - b[1]
    return math.hypot(dr, dc)


def a_star(grid: Grid, start: Coord, goal: Coord, heuristic: HeuristicFunc) -> PathFindingResult:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    def in_bounds(r: int, c: int) -> bool:
        return 0 <= r < rows and 0 <= c < cols

    def is_walkable(r: int, c: int) -> bool:
        return grid[r][c] > 0

    if not (in_bounds(*start) and in_bounds(*goal)):
        return PathFindingResult(math.inf, [], 0, 0.0, 0.0)
    if not (is_walkable(*start) and is_walkable(*goal)):
        return PathFindingResult(math.inf, [], 0, 0.0, 0.0)

    # все возможные для посещения клетки, включая старт и финиш
    # нужно для оценки процента посещённых клеток от общего количества проходимых
    total_walkable = sum(1 for r in range(rows) for c in range(cols) if is_walkable(r, c))
    visited_count = 0

    start_time = time.perf_counter()

    dist: dict[Coord, float] = {start: 0.0}
    prev: dict[Coord, Coord] = {}
    # куча (f_score, dist, coord)
    # f_score = dist + эвристика
    queue: list[tuple[float, float, Coord]] = [(0 + heuristic(start, goal), 0.0, start)]

    moves: Iterable[Coord] = ((1, 0), (-1, 0), (0, 1), (0, -1))

    while queue:
        _, current_dist, current = heapq.heappop(queue)

        # уже найден более короткий путь
        if current_dist > dist.get(current, math.inf):
            continue

        visited_count += 1

        if current == goal:
            break

        r, c = current
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if not (in_bounds(nr, nc) and is_walkable(nr, nc)):
                continue

            # step_cost = abs(grid[nr][nc] - grid[r][c])  # вариант с разницей высот
            step_cost = grid[nr][nc]  # вариант с самим значением высоты
            new_dist = current_dist + step_cost

            if new_dist < dist.get((nr, nc), math.inf):
                dist[(nr, nc)] = new_dist
                prev[(nr, nc)] = current
                f_score = new_dist + heuristic((nr, nc), goal)
                heapq.heappush(queue, (f_score, new_dist, (nr, nc)))

    # статистика
    runtime_sec = time.perf_counter() - start_time
    visited_percent = (visited_count / total_walkable) * 100 if total_walkable else 0.0

    if goal not in dist:
        return PathFindingResult(math.inf, [], visited_count, visited_percent, runtime_sec)

    # найденный путь в обратном порядке
    path: list[Coord] = []
    cur = goal
    while cur:
        path.append(cur)
        cur = prev[cur]

    path.reverse()  # в нормальном порядке

    return PathFindingResult(dist[goal], path, visited_count, visited_percent, runtime_sec)


def solve_grid(grid: Grid, start: Coord, goal: Coord) -> dict[str, PathFindingResult]:
    """Запускает оба варианта A* и возвращает результаты по именам эвристик."""
    return {
        "manhattan": a_star(grid, start, goal, manhattan),
        "euclidean": a_star(grid, start, goal, euclidean),
    }
