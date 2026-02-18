from __future__ import annotations

from collections import deque
from typing import Iterable

Edge = tuple[int, int]


def check_bipartite(n: int, edges: list[Edge]) -> tuple[bool, list[int]]:
    # граф красится в два цвета последовательно
    # если рядом обнаруживаются две вершины одного цвета, граф не двудольный
    colors = [-1] * n
    # список смежности
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # двудольный граф не обязан быть связным и faiap нам неважно,
    # какого цвета будут вершины в разных компонентах связности
    for start in range(n):
        if colors[start] != -1:
            continue
        colors[start] = 0
        q: deque[int] = deque([start])
        while q:
            v = q.popleft()
            for u in adj[v]:
                if colors[u] == -1:
                    # соседняя вершина не раскрашена
                    colors[u] = 1 - colors[v]
                    q.append(u)
                elif colors[u] == colors[v]:
                    # соседняя вершина уже покрашена, да еще и в тот же цвет
                    return False, colors # для полноты возвращаем неполный массив, вдруг пригодится

    # все соседние вершины покрашены в разные цвета, граф двудольный
    return True, colors

# в задании не указан алгоритм, поэтому выпендрился и сделал алгоритм Хопкрофта-Карпа
# можно было скопировать алгоритм Эдмондса-Карпа для макс потока, но так прикольнее (и быстрее)
def hopcroft_karp(n: int, edges: Iterable[Edge], left_partition: set[int]) -> list[Edge]:
    # много комментариев, но пишу для себя, что бы легко обновить память в будущем
    forward_adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        # строим ориентированный граф, в котором дуги идут только из левой доли в правую
        # проход в обратную сторону в алгоритме нужен только
        # для найденных пар, которые хранятся отдельно
        if u in left_partition:
            forward_adj[u].append(v)
        elif v in left_partition:
            forward_adj[v].append(u)

    # пары лево-право
    pair_v = [-1] * n
    # пары право-лево
    pair_u = [-1] * n
    dist = [float('inf')] * n

    # разделяем вершины графа на слои
    # заодно проверяем, есть ли путь увеличения в "остаточном" графе
    def bfs() -> bool:
        # deque - лучше popleft
        dq: deque[int] = deque()
        for v in left_partition:
            # если вершина свободна, то она может быть началом пути увеличения
            if pair_v[v] != -1:
                # не свободна
                dist[v] = float('inf')
            else:
                dist[v] = 0
                dq.append(v)

        found_path = False
        while dq:
            # проставляем слои
            v = dq.popleft()
            for u in forward_adj[v]:
                pu = pair_u[u]
                if pu == -1:
                    # у вершины справа нет пары
                    found_path = True
                elif dist[pu] == float('inf'):
                    # у вершины справа есть пара слева, но она ещё не посещалась
                    dist[pu] = dist[v] + 1
                    dq.append(pu)
        return found_path

    def dfs(v: int) -> bool:
        for u in forward_adj[v]:
            pu = pair_u[u]
            # рабочая лошадка алгоритма
            # если вершина справа свободна, то мы нашли путь увеличения
            # если вершина справа занята, но её пара слева находится в следующем слое,
            # то пробуем пройти глубже через её пару
            if pu == -1 or (dist[pu] == dist[v] + 1 and dfs(pu)):
                # дошли до конца пути увеличения, ура
                # на обратном пути обновляем пару для каждого пройденного ребра
                pair_v[v] = u
                pair_u[u] = v
                return True

        # если мы дошли сюда, значит из v никуда нельзя пройти
        # в этой фазе проходить из неё можно больше не пытаться
        dist[v] = float('inf')
        return False

    # каждый вызов bfs - переход на следующую "фазу" алгоритма
    # каждая фаза увеличивает кратчайший увел путь минимум на 1 ребро
    while bfs():  # пока существуют увеличивающие пути
        # запускаем dfs из каждой свободной вершины слева, пытаясь найти каждый в этой фазе

        # ещё можно создать dummy вершину, из которой есть путь во все левые,
        # и вызывать dfs прямо из неё
        for u in left_partition:
            if pair_v[u] == -1:
                dfs(u)

    # результат в виде списка пар (рёбер)
    matching: list[Edge] = []
    for u in left_partition:
        if pair_v[u] != -1:
            matching.append((u, pair_v[u]))

    return matching


def solve_matching(n: int, edges: list[Edge]) -> tuple[bool, list[Edge]]:
    is_bipartite, colors = check_bipartite(n, edges)
    if not is_bipartite:
        return False, []

    left_partition = {i for i, c in enumerate(colors) if c == 0}
    matching = hopcroft_karp(n, edges, left_partition)
    return True, matching
