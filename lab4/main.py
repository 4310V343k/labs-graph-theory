#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

import click

from .flow import edmonds_karp
from .io_utils import (
    InputFormatError,
    format_flow_output,
    format_matching_output,
    format_path_outputs,
    parse_edge_list_graph,
    parse_adj_weighted,
    parse_grid,
)
from .matching import solve_matching
from .pathfinding import solve_grid


@click.group(subcommand_metavar="COMMAND INPUT_FILE")
def cli() -> None:
    """Набор утилит для лабораторной на 4."""


@cli.command("max_flow")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("ans.txt"),
    show_default=True,
    help="Файл для вывода результатов",
)
def cmd_max_flow(input_file: Path, output: Path) -> None:
    """Алгоритм Форда–Фалкерсона (Эдмондс–Карп)."""
    try:
        n, source, sink, edges = parse_adj_weighted(input_file)
    except InputFormatError as exc:
        click.echo(f"Ошибка формата входного файла: {exc}", err=True)
        raise SystemExit(1) from exc

    if any(not (0 <= e[0] < n) or not (0 <= e[1] < n) for e in edges):
        click.echo("Ошибка: вершины рёбер должны быть в диапазоне [0, n)", err=True)
        raise SystemExit(1)

    max_flow, result_edges = edmonds_karp(n, edges, source, sink)

    report = format_flow_output(source, sink, max_flow, result_edges)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report + "\n", encoding="utf-8")
    click.echo(report)
    click.echo(f"Результат сохранён в {output}")


@cli.command("shortest_path")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("ans.txt"),
    show_default=True,
    help="Файл для вывода результатов",
)
@click.option(
    "--start",
    "-a",
    nargs=2,
    type=int,
    required=True,
    help="Координаты старта (row col)",
)
@click.option(
    "--goal",
    "-b",
    nargs=2,
    type=int,
    required=True,
    help="Координаты финиша (row col)",
)
def cmd_shortest_path(
    input_file: Path, output: Path, start: tuple[int, int], goal: tuple[int, int]
) -> None:
    """A* с манхэттенской и евклидовой эвристиками."""
    try:
        grid = parse_grid(input_file)
    except InputFormatError as exc:
        click.echo(f"Ошибка формата входного файла: {exc}", err=True)
        raise SystemExit(1) from exc

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    def in_bounds(coord: tuple[int, int]) -> bool:
        r, c = coord
        return 0 <= r < rows and 0 <= c < cols

    if not (in_bounds(start) and in_bounds(goal)):
        click.echo("Ошибка: координаты старта/финиша вне карты", err=True)
        raise SystemExit(1)

    if grid[start[0]][start[1]] == 0 or grid[goal[0]][goal[1]] == 0:
        click.echo("Ошибка: старт или финиш попадает на стену (0)", err=True)
        raise SystemExit(1)

    results = solve_grid(grid, start, goal)

    report = format_path_outputs(start, goal, results)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report + "\n", encoding="utf-8")
    click.echo(report)
    click.echo(f"Результат сохранён в {output}")


@cli.command("matching")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("ans.txt"),
    show_default=True,
    help="Файл для вывода результатов",
)
def cmd_matching(input_file: Path, output: Path) -> None:
    """Проверка двудольности и максимальное паросочетание."""
    try:
        n, m, edges = parse_edge_list_graph(input_file)
    except InputFormatError as exc:
        click.echo(f"Ошибка формата входного файла: {exc}", err=True)
        raise SystemExit(1) from exc

    if any(not (0 <= u < n and 0 <= v < n) for u, v in edges):
        click.echo("Ошибка: вершины рёбер должны быть в диапазоне [0, n)", err=True)
        raise SystemExit(1)

    is_bipartite, matching = solve_matching(n, edges)

    report = format_matching_output(is_bipartite, n, m, matching if is_bipartite else None)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report + "\n", encoding="utf-8")
    click.echo(report)
    click.echo(f"Результат сохранён в {output}")


if __name__ == "__main__":
    cli()
