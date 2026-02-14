import heapq
from enum import Enum
from pathlib import Path

# Вариант - 1.a) 2.b) 3.a) 4.a)
# Хранение в виде матрицы смежности, расстояние алг Дейкстры, МОД методом Прима
# В файле на 1 строке хранится количество вершин,
# затем каждая строка означает ребро в формате a b [w],
# где a - вершина откуда, b - вершина куда, w - вес (опционально)
# Отсутствие веса везде означает вес "1", поэтому если добавить еще одно ребро с весом,
# то весь график "автоматически" станет взвешенным


class GraphOrientationType(Enum):
    DIRECTED = "ориентированный"
    UNDIRECTED = "неориентированный"


class Graph:
    def __init__(
        self,
        graph_file_path: Path | None = None,
        graph_type: GraphOrientationType = GraphOrientationType.UNDIRECTED,
        size: int = 0,
    ) -> None:
        """
        Создает граф из файла или пустой граф

        Принимает путь к файлу, в котором хранится размер и граф/орграф,
        а также тип (ориентированный/неориентированный)

        Если путь не указан, создается пустой граф с заданным размером
        """
        self.graph_type = graph_type

        if graph_file_path is None:
            # пустой граф
            self.n = size
            self.adj_matrix: list[list[float | None]] = [[None] * self.n for _ in range(self.n)]

            for i in range(self.n):
                self.adj_matrix[i][i] = 0.0
            return

        # граф из файла
        with open(graph_file_path, "r") as f:
            lines = f.readlines()

        self.n = int(lines[0].strip())

        # None - нет ребра
        self.adj_matrix: list[list[float | None]] = [[None] * self.n for _ in range(self.n)]

        for i in range(self.n):
            self.adj_matrix[i][i] = 0.0

        for line in lines[1:]:
            line = line.strip()
            if line:
                parts = line.split()
                a_i = int(parts[0])
                b_i = int(parts[1])
                weight = float(parts[2]) if len(parts) > 2 else 1.0  # вес по умолчанию, если нет

                self.adj_matrix[a_i][b_i] = weight

                # обратное ребро
                if graph_type == GraphOrientationType.UNDIRECTED:
                    self.adj_matrix[b_i][a_i] = weight

    def size(self) -> int:
        "Возвращает количество вершин в графе/орграфе"
        return self.n

    def weight(self, a_i: int, b_i: int) -> float | None:
        """
        Принимает номера двух вершин

        Возвращает вес ребра/дуги, связывающего их
        """
        if 0 <= a_i < self.n and 0 <= b_i < self.n:  # обе вершины находятся в графе
            return self.adj_matrix[a_i][b_i]

    def is_edge(self, a_i: int, b_i: int) -> bool:
        """
        Принимает номера двух вершин

        Проверяет существование ребра между двумя вершинами
        """
        return self.weight(a_i, b_i) is not None and a_i != b_i

    def add_vertex(self, a_i: int) -> None:
        """
        Принимает номер вершины графа

        Добавляет соответствующую вершину (и все вершины ниже ее индексом) в граф
        """
        if a_i < self.n:
            # вершина уже существует
            return

        new_size = a_i + 1

        # добавление столбцов к существующим строкам
        for row in self.adj_matrix:
            row.extend([None] * (new_size - self.n))

        # новые строки
        for i in range(self.n, new_size):
            new_row: list[float | None] = [None] * new_size
            new_row[i] = 0.0  # диагональ
            self.adj_matrix.append(new_row)

        self.n = new_size

    def add_edge(self, a_i: int, b_i: int, weight: float = 1.0) -> None:
        """
        Принимает номера двух вершин и опционально вес ребра

        Добавляет соответствующее ребро в граф

        Дополняет граф вершинами, если соответствующих вершин в графе нет
        """
        highest_vert = max(a_i, b_i)
        if highest_vert >= self.n:
            self.add_vertex(highest_vert)

        self.adj_matrix[a_i][b_i] = weight

        if self.graph_type == GraphOrientationType.UNDIRECTED:
            # дублирование ребра для неориентированных графов
            self.adj_matrix[b_i][a_i] = weight

    def remove_vertex(self, a_i: int) -> None:
        """
        Принимает номер вершины графа

        Удаляет соответствующую вершину (смещая все последующие на -1) в граф
        """
        if not (0 <= a_i < self.n):
            return

        # удаление строки
        self.adj_matrix.pop(a_i)

        # удаление вершины
        for row in self.adj_matrix:
            row.pop(a_i)

        self.n -= 1

    def remove_edge(self, a_i: int, b_i: int) -> None:
        """
        Принимает номера двух вершин

        Добавляет соответствующее ребро из графа
        """
        if not (0 <= a_i < self.n and 0 <= b_i < self.n):
            return

        self.adj_matrix[a_i][b_i] = None

        if self.graph_type == GraphOrientationType.UNDIRECTED:
            self.adj_matrix[b_i][a_i] = None  # обратное ребро

    def list_of_vertices(self) -> list[int]:
        """
        Возвращает список всех рёбер графа
        """
        # дааааааааааааааааааааа
        return list(range(self.n))

    def list_of_edges(self, a_i: int | None = None) -> list[tuple[int, int, float]]:
        """
        Без аргументов возвращает список всех рёбер графа

        С аргументом (номер вершины) возвращает список рёбер графа,
        инцидентных данной вершине / дуг, исходящих из данной вершины
        """
        edges = []

        if a_i is not None:  # исходящие из вершины ребра
            if 0 <= a_i < self.n:
                for j in range(self.n):
                    if self.adj_matrix[a_i][j] is not None and a_i != j:
                        edges.append((a_i, j, self.adj_matrix[a_i][j]))
            return edges

        for i in range(self.n):
            # в неориентированном графе ребра дублированы,
            # это значит нам достаточно пройти только по ребрам выше диагонали
            min_j = 0 if self.graph_type == GraphOrientationType.DIRECTED else i + 1
            for j in range(min_j, self.n):
                if (
                    self.adj_matrix[i][j] is not None and i != j
                ):  # и вторая проверка нужна только для ориентированных графов
                    edges.append((i, j, self.adj_matrix[i][j]))
                    if self.graph_type == GraphOrientationType.UNDIRECTED:
                        # в неориентированном одно ребро в обе стороны
                        edges.append((j, i, self.adj_matrix[i][j]))

        return edges

    def is_connected(self) -> bool:
        """
        Проверяет граф на связность
        """
        # альтернативно можно запустить поиск из одной вершины
        # и сравнить размеры компоненты и графа, но мне лень
        if self.n == 0:
            return True

        components = self.connected_components()
        return len(components) == 1

    def connected_components(self) -> list[set[int]]:
        """
        Возвращает компоненты связности графа/компоненты слабой связности орграфа
        """
        components: list[set[int]] = []
        visited = [False] * self.n

        for i in range(self.n):
            # из каждой вершины пытаемся нащупать компоненту простым dfs,
            # если ещё не были в этой компоненте
            if visited[i]:
                continue

            component = set()
            q = [i]
            while q:
                v = q.pop()
                if visited[v]:
                    continue

                visited[v] = True
                component.add(v)

                for u in range(self.n):
                    if (
                        self.adj_matrix[v][u] is not None or self.adj_matrix[u][v] is not None
                    ) and v != u:
                        q.append(u)

            components.append(component)

        return components


def dijkstra(graph: Graph, start: int, end: int) -> tuple[float | None, list[int]]:
    """
    Находит кратчайший путь между двумя вершинами
    при помощи алгоритма Дейкстры

    Возвращает кортеж (расстояние, список вершин: путь от start до end включительно)
    O(nlogn + m)
    """
    n = graph.size()

    if not (0 <= start < n and 0 <= end < n):
        return (None, [])  # вершина за пределом графа

    dist: list[float] = [float("inf")] * n
    dist[start] = 0.0
    prev: list[int | None] = [None] * n

    # приоритетная очередь (расстояние, вершина)
    queue = [(0.0, start)]

    while queue:  # yes, that works!
        cur_dist, v = heapq.heappop(queue)

        # если придя в эту вершину длина до нее больше, чем уже сохранена,
        # то мы уже нашли кратчайший путь в эту вершину ранее. и никаких булевых массивов!
        # хорошо только на разреженных графах
        if cur_dist > dist[v]:
            continue

        if v == end:
            # дошли до конечной вершины
            break

        for u in range(n):
            # все соседние вершины, которые ещё не посещены
            if (weight := graph.weight(v, u)) is not None and v != u:
                new_dist = dist[v] + weight

                # найден более быстрый маршрут
                if new_dist < dist[u]:
                    dist[u] = new_dist
                    prev[u] = v
                    heapq.heappush(queue, (new_dist, u))

    if dist[end] == float("inf"):
        # нет пути из start в end
        return (float("inf"), [])

    # восстановление пути с конца в начало
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = prev[current]

    path.reverse()  # теперь с начала в конец

    return (dist[end], path)


def dijkstra_all(graph: Graph, start: int) -> list[tuple[float, list[int]]]:
    """
    Находит кратчайший путь между двумя вершинами
    при помощи алгоритма Дейкстры

    Возвращает кортеж (расстояние, список вершин: путь от start до end включительно)
    O(nlogn + m)
    """
    # та же тема, что и выше, но нет раннего выхода и видоизменено восстановление маршрута
    # теперь это восстановление маршрут*ов*. да, это вся разница
    n = graph.size()

    if not (0 <= start < n):
        return []  # вершина за пределом графа

    dist: list[float] = [float("inf")] * n
    dist[start] = 0.0
    prev: list[int | None] = [None] * n

    # приоритетная очередь (расстояние, вершина)
    queue = [(0.0, start)]

    while queue:  # yes, that works!
        cur_dist, v = heapq.heappop(queue)

        # если придя в эту вершину длина до нее больше, чем уже сохранена,
        # то мы уже нашли кратчайший путь в эту вершину ранее. и никаких булевых массивов!
        # хорошо только на разреженных графах, иначе очередь может вырасти вплоть до n^2 (это плохо)
        if cur_dist > dist[v]:
            continue

        for u in range(n):
            # все соседние вершины, которые ещё не посещены
            if (weight := graph.weight(v, u)) is not None and v != u:
                new_dist = dist[v] + weight

                # найден более быстрый маршрут
                if new_dist < dist[u]:
                    dist[u] = new_dist
                    prev[u] = v
                    heapq.heappush(queue, (new_dist, u))

    # восстановление путей с конца в начало
    result_paths: list[tuple[float, list[int]]] = []
    for end in range(n):
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = prev[current]

        path.reverse()  # теперь с начала в конец
        result_paths.append((dist[end], path))

    return result_paths


def prim(graph: Graph, start: int) -> list[tuple[int, int, float]]:
    """
    Находит минимальное остовное дерево из вершины
    методом Прима

    Возвращает список ребер минимального остовного дерева [(вершина1, вершина2, вес)]
    """
    n = graph.size()

    if not (0 <= start < n):
        # а граф-то ПУСТОЙ
        return []

    min_edge: list[float] = [float("inf")] * n
    min_edge[start] = 0.0
    prev: list[int | None] = [None] * n

    # приоритетная очередь (вес, вершина)
    queue = [(0.0, start)]

    while queue:
        cur_weight, v = heapq.heappop(queue)

        # если придя в эту вершину вес ребра, через которое мы пришли, больше, чем уже сохранено,
        # то мы уже явно приходили в эту вершину ранее. и никаких булевых массивов!
        # хорошо только на разреженных графах, иначе очередь может вырасти вплоть до n^2 (это плохо)
        if cur_weight > min_edge[v]:
            continue

        for u in range(n):
            if v == u:
                continue

            # у нам могут быть орграфы, а значит надо проходиться
            # как по исходящим дугам, так и входящим (матрица смежности my beloved 💘)
            # если дуги идут друг в друга, берем меньший вес
            min_weight = min(graph.weight(v, u) or float("inf"), graph.weight(u, v) or float("inf"))

            if min_weight != float("inf") and min_edge[u] > min_weight:
                prev[u] = v
                min_edge[u] = min_weight
                heapq.heappush(queue, (min_weight, u))

    # восстановление путей с конца в начало
    result_paths = []
    for end in range(n):
        # восстановление путей с конца в начало
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = prev[current]

        path.reverse()  # теперь с начала в конец
        result_paths.append(path)

    return result_paths
