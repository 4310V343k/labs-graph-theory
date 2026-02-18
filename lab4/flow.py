from __future__ import annotations

from collections import deque
from dataclasses import dataclass

WeightedEdge = tuple[int, int, float]


@dataclass
class FlowEdge:
    to: int
    rev_i: int
    capacity: float
    flow: float = 0.0

    @property
    def residual_capacity(self) -> float:
        return self.capacity - self.flow


# в задании указано "соответствующую версию алгоритма"
# непонятно, что означает "соответствующая", поэтому реализовал метод Форда–Фалкерсона
# поиском в ширину (алгоритм Эдмондса-Карпа)
def edmonds_karp(n: int, edges: list[WeightedEdge], source: int, sink: int) -> tuple[float, list[FlowEdge]]:
    """Вычисляет максимальный поток и потоки по рёбрам (в порядке ввода)."""
    if n <= 0 or not (0 <= source < n) or not (0 <= sink < n):
        return 0.0, []

    if source == sink:
        return 0.0, [FlowEdge(e[0], e[1], e[2], 0.0) for e in edges]

    # перевод графа в вид остаточного графа, с рёбрами в обоих направлениях
    # в структурах ребер на месте обратной вершины хранится не вершина,
    # а индекс рёбра в списке смежности, чтобы быстро находить обратное ребро
    graph: list[list[FlowEdge]] = [[] for _ in range(n)]
    forward_edges: list[FlowEdge] = []

    for e in edges:
        v, u, cap = e
        # len тут указывает на индекс *нового* ребра
        forward_edge = FlowEdge(v, len(graph[v]), cap)
        backward_edge = FlowEdge(u, len(graph[u]), 0.0)

        graph[v].append(forward_edge)
        graph[u].append(backward_edge)

        # дополнительно сохраняем только передние ребра в порядке ввода,
        # чтобы потом отчитаться по ним
        forward_edges.append(forward_edge)

    max_flow = 0.0

    while True:
        # ищем увеличивающий (кратчайший в остаточной сети) путь с помощью BFS
        parent: list[tuple[int, FlowEdge] | None] = [None] * n
        queue: deque[int] = deque([source])
        while queue and parent[sink] is None:
            v = queue.popleft()
            for edge in graph[v]:
                # пропускаем рёбра, по которым уже нельзя пустить поток
                if edge.residual_capacity <= 0:
                    continue
                # пропускаем уже посещённые вершины
                if parent[edge.to] is not None or edge.to == source:
                    continue
                # расширяем путь
                parent[edge.to] = (v, edge)
                queue.append(edge.to)

        if parent[sink] is None:
            break

        path_flow = float("inf")

        # ищем максимальный поток по найденному пути
        cur = sink
        while cur != source:
            prev, edge = parent[cur]  # type: ignore[misc]
            path_flow = min(path_flow, edge.residual_capacity)
            cur = prev

        # пускаем поток по найденному пути
        cur = sink
        while cur != source:
            prev, edge = parent[cur]  # type: ignore[misc]
            edge.flow += path_flow
            graph[edge.to][edge.rev_i].flow -= path_flow
            cur = prev

        max_flow += path_flow

    # сохраняя порядок рёбер из ввода
    result_edges: list[FlowEdge] = []
    for orig_edge, flow_edge in zip(edges, forward_edges):
        result_edges.append(FlowEdge(orig_edge[0], orig_edge[1], orig_edge[2], flow_edge.flow))

    return max_flow, result_edges
