#!/usr/bin/env python3

from pathlib import Path
from typing import Optional, TypeGuard

import prompt_toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from rich import box, print
from rich.panel import Panel
from rich.table import Table

from .graph import Graph, GraphOrientationType, dijkstra, dijkstra_all, prim
from .gui_helpers import FileNameValidator, FloatValidator, FuzzyFileCompletion, IntValidator


def check_graph_exists(graph: Graph | None) -> TypeGuard[Graph]:
    """Проверяет, что граф создан"""
    if graph is None:
        print("[bold red]❌ Граф ещё не создан! Используйте команду 'create' или 'load'[/bold red]")
        return False
    return True


class CLI:
    def __init__(self):
        self.graph: Optional[Graph] = None

        self.commands = {
            "create": "Создать пустой граф",
            "load": "Загрузить граф из файла",
            "add_vertex": "Добавить вершину",
            "add_edge": "Добавить ребро",
            "remove_vertex": "Удалить вершину",
            "remove_edge": "Удалить ребро",
            "list_vertices": "Вывести список всех вершин",
            "list_edges": "Вывести список всех рёбер",
            "connected": "Проверить связность графа",
            "components": "Вывести компоненты связности",
            "shortest_path": "Найти кратчайший путь между двумя вершинами",
            "distances": "Найти расстояния от вершины до всех остальных",
            "mst": "Найти минимальное остовное дерево",
            "info": "Информация о графе",
            "help": "Показать справку",
            "exit": "Выйти из программы",
        }

        self.int_validator = IntValidator()
        self.float_validator = FloatValidator()
        self.file_validator = FileNameValidator()
        self.file_completer = FuzzyFileCompletion()

        self.command_completer = WordCompleter(
            list(self.commands.keys()), ignore_case=True, sentence=True
        )

        self.command_prompt_session = PromptSession(
            completer=self.command_completer,
            style=Style.from_dict(
                {
                    "prompt": "#00aa00 bold",
                }
            ),
        )

        self.active_command: str = ""

    def print_welcome(self):
        welcome_text = """
[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]  [bold white]Главный по графам[/bold white]                    [bold cyan]║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]

Введите [bold green]help[/bold green] для списка команд
        """  # noqa: E501
        print(welcome_text)

    def print_help(self):
        """Печатает справку по командам"""
        table = Table(title="Доступные команды", box=box.ROUNDED)
        table.add_column("Команда", style="cyan", no_wrap=True)
        table.add_column("Описание", style="white")

        for cmd, desc in self.commands.items():
            table.add_row(cmd, desc)

        print(table)

    def cmd_create(self):
        """Создать пустой граф"""
        size = int(
            self.prompt(
                "Количество вершин (0 для пустого графа): ",
                validator=self.int_validator,
            )
        )
        graph_type = self.choice(
            "Тип графа:",
            options=[
                (GraphOrientationType.UNDIRECTED, GraphOrientationType.UNDIRECTED.value),
                (GraphOrientationType.DIRECTED, GraphOrientationType.DIRECTED.value),
            ],
        )

        self.graph = Graph(size=size, graph_type=graph_type)
        print(f"[bold green]✓[/bold green] Создан {graph_type.value} граф с {size} вершинами")

    def cmd_load(self):
        """Загрузить граф из файла"""
        filepath = self.prompt(
            "Путь к файлу: ", validator=self.file_validator, completer=self.file_completer
        )
        graph_type = self.choice(
            "Тип графа:",
            options=[
                (GraphOrientationType.UNDIRECTED, GraphOrientationType.UNDIRECTED.value),
                (GraphOrientationType.DIRECTED, GraphOrientationType.DIRECTED.value),
            ],
        )

        self.graph = Graph(Path(filepath), graph_type)
        print(
            f"[bold green]✓[/bold green] {graph_type.value.capitalize()} "
            f"граф загружен из файла {filepath}"
        )
        self.execute("info")

    def cmd_add_vertex(self):
        """Добавить вершину"""
        if not check_graph_exists(self.graph):
            return

        vertex = int(self.prompt("Номер вершины: ", validator=self.int_validator))
        self.graph.add_vertex(vertex)
        print(f"[bold green]✓[/bold green] Вершина {vertex} добавлена")

    def cmd_add_edge(self):
        """Добавить ребро"""
        if not check_graph_exists(self.graph):
            return

        v1 = int(self.prompt("Первая вершина: ", validator=self.int_validator))
        v2 = int(self.prompt("Вторая вершина: ", validator=self.int_validator))
        weight = float(self.prompt("Вес ребра [1.0]: ", validator=self.float_validator) or "1.0")

        self.graph.add_edge(v1, v2, weight)
        print(f"[bold green]✓[/bold green] Ребро {v1} -> {v2} (вес: {weight}) добавлено")

    def cmd_remove_vertex(self):
        """Удалить вершину"""
        if not check_graph_exists(self.graph):
            return

        vertex = int(self.prompt("Номер вершины: ", validator=self.int_validator))
        self.graph.remove_vertex(vertex)
        print(f"[bold green]✓[/bold green] Вершина {vertex} удалена, сместив все последующие на -1")

    def cmd_remove_edge(self):
        """Удалить ребро"""
        if not check_graph_exists(self.graph):
            return

        v = int(self.prompt("Первая вершина: ", validator=self.int_validator))
        u = int(self.prompt("Вторая вершина: ", validator=self.int_validator))

        self.graph.remove_edge(v, u)
        print(f"[bold green]✓[/bold green] Ребро {v} -> {u} удалено")

    def cmd_list_vertices(self):
        """Вывести список всех вершин"""
        # да, список от 1 до n :)
        if not check_graph_exists(self.graph):
            return

        vertices = self.graph.list_of_vertices()
        print(f"[bold]Вершины графа:[/bold] {', '.join(map(str, vertices))}")
        print(f"[dim]Всего вершин: {len(vertices)}[/dim]")

    def cmd_list_edges(self):
        """Вывести список всех рёбер"""
        if not check_graph_exists(self.graph):
            return

        edges = self.graph.list_of_edges()

        if not edges:
            print("[yellow]Граф не содержит рёбер[/yellow]")
            return

        table = Table(title="Рёбра графа", box=box.ROUNDED)
        table.add_column("№", style="cyan", justify="right")
        table.add_column("От", style="green", justify="center")
        table.add_column("До", style="green", justify="center")
        table.add_column("Вес", style="yellow", justify="right")

        for i, (v, u, w) in enumerate(edges, 1):
            table.add_row(str(i), str(v), str(u), f"{w:.2f}")

        print()
        print(table)
        print(f"[dim]Всего рёбер: {len(edges)}[/dim]")

    def cmd_connected(self):
        """Проверить связность графа"""
        if not check_graph_exists(self.graph):
            return

        is_connected = self.graph.is_connected()

        if is_connected:
            print("[bold green]✓ Граф является связным[/bold green]")
        else:
            print("[bold yellow]⚠ Граф не является связным[/bold yellow]")

    def cmd_components(self):
        """Вывести компоненты связности"""
        if not check_graph_exists(self.graph):
            return

        components = self.graph.connected_components()

        graph_type_str = (
            "слабой связности орграфа"
            if self.graph.graph_type == GraphOrientationType.DIRECTED
            else "связности графа"
        )

        table = Table(title=f"Компоненты {graph_type_str}", box=box.ROUNDED)
        table.add_column("№", style="cyan", justify="right")
        table.add_column("Вершины", style="white")
        table.add_column("Размер", style="yellow", justify="right")

        for i, component in enumerate(components, 1):
            table.add_row(str(i), ", ".join(map(str, sorted(component))), str(len(component)))

        print(table)
        print(f"[dim]Всего компонент: {len(components)}[/dim]")

    def cmd_shortest_path(self):
        """Найти кратчайший путь между двумя вершинами"""
        if not check_graph_exists(self.graph):
            return

        start = int(self.prompt("Начальная вершина: ", validator=self.int_validator))
        end = int(self.prompt("Конечная вершина: ", validator=self.int_validator))

        distance, path = dijkstra(self.graph, start, end)

        if not distance:
            print("[yellow]Невозможно найти расстояние с заданными параметрами[/yellow]")
            return

        if distance == float("inf"):
            print(f"[bold red]❌ Пути от {start} до {end} не существует[/bold red]")
            return

        print(
            Panel(
                f"[bold]Путь:[/bold] {' → '.join(map(str, path))}\n"
                f"[bold]Расстояние:[/bold] {distance:.2f}",
                title=f"Кратчайший путь от {start} до {end}",
                border_style="green",
                expand=False,
            )
        )

    def cmd_distances(self):
        """Найти расстояния от вершины до всех остальных"""
        if not check_graph_exists(self.graph):
            return

        start = int(self.prompt("Начальная вершина: ", validator=self.int_validator))

        results = dijkstra_all(self.graph, start)

        if not results:
            print("[yellow]Невозможно найти все расстояния с заданными параметрами[/yellow]")
            return

        table = Table(title=f"Расстояния от вершины {start}", box=box.ROUNDED)
        table.add_column("Вершина", style="cyan", justify="right")
        table.add_column("Расстояние", style="yellow", justify="right")
        table.add_column("Путь", style="white")

        for i, (distance, path) in enumerate(results):
            path_str = " → ".join(map(str, path))
            table.add_row(str(i), f"{distance:.2f}", path_str)

        print(table)

    def cmd_mst(self):
        """Найти минимальное остовное дерево"""
        if not check_graph_exists(self.graph):
            return

        start = int(self.prompt("Начальная вершина: ", validator=self.int_validator))

        mst_edges = prim(self.graph, start)

        if not mst_edges:
            print("[yellow]Невозможно построить остовное дерево с заданными параметрами[/yellow]")
            return

        table = Table(title="Минимальное остовное дерево (алгоритм Прима)", box=box.ROUNDED)
        table.add_column("№", style="cyan", justify="right")
        table.add_column("От", style="green", justify="center")
        table.add_column("До", style="green", justify="center")
        table.add_column("Вес", style="yellow", justify="right")

        total_weight = 0
        for i, (v, u, weight) in enumerate(mst_edges, 1):
            table.add_row(str(i), str(v), str(u), f"{weight:.2f}")
            total_weight += weight

        print(table)
        print(f"[bold]Общий вес МОД:[/bold] {total_weight:.2f}")

    def cmd_info(self):
        """Информация о графе"""
        if not check_graph_exists(self.graph):
            return

        size = self.graph.size()
        edges = self.graph.list_of_edges()
        is_connected = self.graph.is_connected()
        components = self.graph.connected_components()

        components_type_str = (
            "слабой связности орграфа"
            if self.graph.graph_type == GraphOrientationType.DIRECTED
            else "связности графа"
        )

        info_text = f"""
[bold]Тип:[/bold] {self.graph.graph_type.value}
[bold]Вершин:[/bold] {size}
[bold]Рёбер:[/bold] {len(edges)}
[bold]Связность:[/bold] {"Да" if is_connected else "Нет"}
[bold]Компонент {components_type_str}:[/bold] {len(components)}
        """.strip()

        print(Panel(info_text, title="Информация о графе", border_style="blue", expand=False))

    def prompt(self, message, *args, **kwargs):
        return prompt_toolkit.prompt(
            HTML(f"<prompt>{self.active_command}> </prompt><message>{message}</message>"),
            style=Style.from_dict(
                {
                    "prompt": "#72bcd4 bold",
                    "message": "#ffffff bold",
                }
            ),
            *args,
            **kwargs,
        )

    def choice(self, message, *args, **kwargs):
        return prompt_toolkit.choice(
            HTML(
                f"<prompt>{' ' * (len(self.active_command) - 1)}> </prompt>"
                f"<message>{message}</message>"
            ),
            style=Style.from_dict(
                {
                    "prompt": "#72bcd4 bold",
                    "message": "#ffffff bold",
                }
            ),
            *args,
            **kwargs,
        )

    def execute(self, command: str):
        self.active_command = command
        getattr(self, f"cmd_{command}")()

    def run(self):
        """Запуск интерактивной оболочки"""
        self.print_welcome()

        while True:
            try:
                command = (
                    self.command_prompt_session.prompt(
                        HTML("<prompt>graph> </prompt>"),
                    )
                    .strip()
                    .lower()
                )

                if not command:
                    continue

                if command == "exit" or command == "quit":
                    break

                if command == "help":
                    self.print_help()
                    continue

                if command not in self.commands:
                    print(f"[bold red]❌ Неизвестная команда: {command}[/bold red]")
                    print("Введите [bold]help[/bold] для списка доступных команд")
                    continue

                self.execute(command)

                print()

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"[bold red]❌ Ошибка: {e}[/bold red]")


if __name__ == "__main__":
    CLI().run()
