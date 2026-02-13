from enum import Enum
from pathlib import Path

# вариант - 1.b) 2.b) 3.a) 4.a)
# хранение в виде матрицы смежности, расстояние алг Дейкстры, МОД методом Прима
# в файле на 1 строке хранится количество вершин
# затем каждая строка означает ребро в формате a b [w],
# где a - вершина откуда, b - вершина куда, w - вес (опционально)
# отсутствие веса везде означает вес "1", поэтому если добавить еще одно ребро с весом,
# то весь график "автоматически" станет взвешенным

class GraphOrientationType(Enum):
    DIRECTED = "directed"
    UNDIRECTED = "undirected"

class Graph:
    def __init__(self, graph_file_path: Path, graph_type: GraphOrientationType) -> None:
        """
        принимает путь к файлу, в котором хранится граф/орграф
        и тип (ориентированный/неориентированный)
        """
        self.graph_type = graph_type
       
        with open(graph_file_path, 'r') as f:
            lines = f.readlines()
        
        self.n = int(lines[0].strip())

        # None - нет ребра
        self.adj_matrix: list[list[float | None]] = [[None] * self.n for _ in range(self.n)]

        for i in range(self.n):
            self.adj_matrix[i][i] = 0.

        for line in lines[1:]:
            line = line.strip()
            if line:
                parts = line.split()
                a_i = int(parts[0])
                b_i = int(parts[1])
                weight = float(parts[2]) if len(parts) > 2 else 1. # вес по умолчанию, если нет

                self.adj_matrix[a_i][b_i] = weight

                # обратное ребро
                if graph_type == GraphOrientationType.UNDIRECTED:
                    self.adj_matrix[b_i][a_i] = weight

    def size(self) -> int:
        "возвращает количество вершин в графе/орграфе"
        return self.n


    def weight(self, a_i: int, b_i: int) -> float | None:
        """
        принимает номера двух вершин,
        возвращает вес ребра/дуги, связывающего их
        """
        if 0 <= a_i < self.n and 0 <= b_i < self.n: # обе вершины находятся в графе
            return self.adj_matrix[a_i][b_i]
        return None

    def is_edge(self, a_i: int, b_i: int) -> bool:
        """
        принимает номера двух вершин,
        возвращает существует ли ребро между двумя вершинами
        """
        return self.weight(a_i, b_i) is not None and a_i != b_i
        
    def add_vertex(self, a_i: int) -> None:
        """
        принимает номер вершины графа,
        добавляет соответствующую вершину в граф
        """
        if a_i < self.n:
            # вершина уже существует
            return

        new_size = a_i + 1

        # добавление столбцов к существующим строкам
        for row in self.adj_matrix:
            row.extend([None] * (new_size - self.n))
        
        for i in range(self.n, new_size):
            new_row: list[float | None] = [None] * new_size
            new_row[i] = 0. # диагональ
            self.adj_matrix.append(new_row)
        
        self.n = new_size

    def add_edge(self, a_i: int, b_i: int, weight: float = 1.) -> None:
        """
        принимает номера двух вершин и опционально вес ребра,
        добавляет соответствующее ребро в граф
        дополняет граф, если вершин не хватает
        """

        highest_vert = max(a_i, b_i)
        if highest_vert >= self.n:
            self.add_vertex(highest_vert)
        
        self.adj_matrix[a_i][b_i] = weight

        if self.graph_type == GraphOrientationType.UNDIRECTED:
            # дублирование ребра для неориентированных графов
            self.adj_matrix[b_i][a_i] = weight       

    def list_of_edges(self, a_i: int | None = None) -> list[tuple[int, int, float]]:
        """
        без аргументов возвращает список всех рёбер графа
        с аргументом (номер вершины) возвращает список рёбер графа,
        инцидентных данной вершине / дуг, исходящих из данной вершины
        """
        edges = []

        if a_i is not None: # исходящие из вершины ребра
            if 0 <= a_i < self.n:
                for j in range(self.n):
                    if self.adj_matrix[a_i][j] is not None and a_i != j:
                        edges.append((a_i, j, self.adj_matrix[a_i][j]))
            return edges

        for i in range(self.n):
            # в неориентированном графе ребра дублированы,
            # это значит можно пройти только по ребрам выше диагонали
            min_j =  0 if self.graph_type == GraphOrientationType.DIRECTED else i + 1
            for j in range(min_j, self.n):
                if self.adj_matrix[i][j] is not None and i != j: # вторая проверка нужна только для ориентированных графов
                    edges.append((i, j, self.adj_matrix[i][j]))
                    if self.graph_type == GraphOrientationType.UNDIRECTED:
                        # в неориентированном одно ребро в обе стороны
                        edges.append((j, i, self.adj_matrix[j][i]))

        return edges


def main():
    pass


if __name__ == '__main__':
    main()
