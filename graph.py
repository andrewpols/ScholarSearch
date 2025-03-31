"""
This module contains the Graph, Vertex, and Paper classes.
It is responsible for loading the research graph from the csv file and returning a Graph object.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import csv


class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.
        - level: The nesting level of this vertex in the graph (1 if it was found using direct search,
                2 if it is a neighbour of direct search).
        - visible: Whether the vertex is visible on the graph
    """
    item: Any
    neighbours: set[_Vertex]
    level: int
    visible: bool

    def __init__(self, item: Any, neighbours: set[_Vertex]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = neighbours
        self.level = 2
        self.visible = True


class Graph:
    """A graph.

    Representation Invariants:
    - all(item == self._vertices[item].item for item in self._vertices)
    """
    # Private Instance Attributes:
    #     - _vertices: A collection of the vertices contained in this graph.
    #                  Maps item to _Vertex instance.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices
        """
        self._vertices[item.paper_id] = _Vertex(item, set())

    def add_edge(self, id1: Any, id2: Any) -> None:
        """Add a directed edge from id1 to id2.

        Raise a ValueError if id1 or id2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if id1 in self._vertices and id2 in self._vertices:
            v1 = self._vertices[id1]
            v2 = self._vertices[id2]

            # Add the new edge
            v1.neighbours.add(v2)
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError

    def get_all_item_vertex_mappings(self) -> dict[Any, _Vertex]:
        """Return a dictionary mapping items to their corresponding vertex in this graph."""
        return self._vertices


@dataclass
class Paper:
    """
    A dataclass representing a paper in the research graph.
    """
    authors: list[str]
    n_citation: int
    references: list[str]
    title: str
    venue: str
    paper_id: str


def process_row(row: list) -> Paper:
    """
    Process a row from the csv file and return a Paper object.

    Preconditions:
        - row is a list of length 8.
    """

    authors_pre_split = row[1].strip("[]").split(', ')
    authors = [item.strip("'\"") for item in authors_pre_split]

    n_citations = int(row[2])

    references_pre_split = row[3].strip("[]").split(', ')
    references = [item.strip("'\"") for item in references_pre_split]

    title = row[4]

    venue = row[5]

    paper_id = row[7]
    return Paper(authors, n_citations, references, title, venue, paper_id)


def load_research_graph(csv_path: str = '../dblp-v10-2.csv') -> Graph:
    """
    Load the research graph from the csv file and return a Graph object.

    Preconditions:
        - csv_path is a valid path to the csv file.
    """
    graph = Graph()

    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            graph.add_vertex(process_row(row))

    # Adding edges
    for paper in graph.get_all_item_vertex_mappings().values():
        p_id = paper.item.paper_id
        for x in paper.item.references:
            if x in graph.get_all_item_vertex_mappings():
                graph.add_edge(p_id, x)

    return graph


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['csv'],  # the names (strs) of imported modules
        'allowed-io': ['load_research_graph'],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
