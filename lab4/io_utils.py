from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .flow import FlowEdge, WeightedEdge
from .matching import Edge
from .pathfinding import Grid, PathFindingResult


class InputFormatError(Exception):
    pass


def parse_adj_weighted(path: Path) -> tuple[int, int, int, List[WeightedEdge]]:
    """Парсит взвешенный граф в формате списков смежности.

    Формат:
    1) n
    2) s t
    3) n строк списков смежности для вершин 0..n-1: пары "v capacity" через пробел.
       Пустая строка означает отсутствие исходящих рёбер.
    """
    raw_lines = [ln.rstrip() for ln in path.read_text(encoding="utf-8").splitlines()]
    if len(raw_lines) < 2:
        raise InputFormatError("Нужно минимум две строки: n и s t")

    try:
        n = int(raw_lines[0].strip())
    except Exception as exc:
        raise InputFormatError("Первая строка: одно число n") from exc

    try:
        s, t = map(int, raw_lines[1].split())
    except Exception as exc:
        raise InputFormatError("Вторая строка: два числа s t") from exc

    edges: List[WeightedEdge] = []

    adj_lines = raw_lines[2:]
    if len(adj_lines) < n:
        # недостающие строки считаем пустыми списками смежности
        adj_lines.extend([""] * (n - len(adj_lines)))

    for u in range(n):
        line = adj_lines[u] if u < len(adj_lines) else ""
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) % 2 != 0:
            raise InputFormatError(
                f"Строка смежности для вершины {u}: ожидаются пары 'v capacity' через пробел"
            )
        for i in range(0, len(parts), 2):
            try:
                v = int(parts[i])
                cap = float(parts[i + 1])
            except Exception as exc:
                raise InputFormatError(
                    f"Строка вершины {u}: пара '{parts[i]} {parts[i+1]}' не число"
                ) from exc
            edges.append((u, v, cap))

    return n, s, t, edges


def parse_grid(path: Path) -> Grid:
    """Парсит двумерную матрицу.

    Формат:
    1) m строк по n столбцов
    Пустые строки игнорируются.
    """
    rows: List[List[int]] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = [int(x) for x in line.split()]
        except Exception as exc:
            raise InputFormatError(f"Строка {idx}: должны быть целые числа") from exc
        rows.append(row)

    if not rows:
        raise InputFormatError("Файл карты пуст")

    width = len(rows[0])
    if any(len(r) != width for r in rows):
        raise InputFormatError("Строки карты должны иметь одинаковую длину")

    return rows


def parse_edge_list_graph(path: Path) -> tuple[int, int, list[Edge]]:
    """Парсит неориентированный граф в формате списка рёбер.

    Формат:
    1) n
    2) m строк: u v (0-based), неориентированные рёбра
    Пустые строки игнорируются.
    """
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        raise InputFormatError("Файл пуст")

    try:
        n = int(lines[0].strip())
    except Exception as exc:
        raise InputFormatError("Первая строка: одно число n") from exc

    edges: list[Edge] = []
    for idx, line in enumerate(lines[1:], start=2):
        try:
            u, v = map(int, line.split())
        except Exception as exc:
            raise InputFormatError(f"Строка {idx}: ожидается 'u v'") from exc
        edges.append((u, v))

    return n, len(edges), edges


def format_flow_output(source: int, sink: int, max_flow: float, edges: List[FlowEdge]) -> str:
    lines = [
        f"Источник: {source}",
        f"Сток: {sink}",
        f"Максимальный поток: {max_flow:.2f}",
        "Рёбра (поток/пропускная способность):",
    ]

    for e in edges:
        lines.append(f"  {e.to} -> {e.rev_i}: {e.flow:.2f} / {e.capacity:.2f}")

    return "\n".join(lines)


def _format_path(path: List[Tuple[int, int]]) -> str:
    return " -> ".join(f"({r},{c})" for r, c in path)


def format_path_outputs(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    results: dict[str, PathFindingResult],
) -> str:
    lines = [f"Старт: {start}", f"Финиш: {goal}"]

    for name, res in results.items():
        lines.append("")
        lines.append(f"Алгоритм A* ({name}):")
        if res.length == float("inf") or not res.path:
            lines.append("  Путь не найден")
            lines.append(f"  Просмотрено: {res.visited_percent:.2f}% ({res.visited_count} вершин)")
            lines.append(f"  Время: {res.runtime_sec:.6f} c")
            continue

        lines.append(f"  Длина пути: {res.length:.2f}")
        lines.append(f"  Путь: {_format_path(res.path)}")
        lines.append(f"  Просмотрено: {res.visited_percent:.2f}% ({res.visited_count} вершин)")
        lines.append(f"  Время: {res.runtime_sec:.6f} c")

    return "\n".join(lines)


def format_matching_output(
    is_bipartite: bool,
    n: int,
    m: int,
    matching: list[Edge] | None,
) -> str:
    if not is_bipartite:
        return "\n".join(["Граф двудольный: Нет"])

    lines = [
        "Граф двудольный: Да",
        f"Вершин: {n}",
        f"Рёбер: {m}",
        f"Размер максимального паросочетания: {len(matching or [])}",
        "Рёбра паросочетания:",
    ]

    for u, v in matching or []:
        lines.append(f"  {u} - {v}")

    return "\n".join(lines)
