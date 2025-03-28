from __future__ import annotations
from typing import Any
import requests
import csv


class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.
        - level: The nesting level of this vertex in the graph (1 if it was found using direct search,
                2 if it is a neighbour of direct search).
    """
    item: Any
    neighbours: set[_Vertex]
    level: int

    def __init__(self, item: Any, neighbours: set[_Vertex]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = neighbours
        self.level = 2


class Graph:
    """A graph.

    Representation Invariants:
    - all(item == self._vertices[item].item for item in self._vertices)
    """
    # Private Instance Attributes:
    #     - _vertices: A collection of the vertices contained in this graph.
    #                  Maps item to _Vertex instance.
    vertices: dict[Any, _Vertex]  # TODO: private attribute <_vertices>

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self.vertices = {}

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices
        """
        self.vertices[item.paper_id] = _Vertex(item, set())

    def add_edge(self, id1: Any, id2: Any) -> None:
        """Add a directed edge from id1 to id2.

        Raise a ValueError if id1 or id2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if id1 in self.vertices and id2 in self.vertices:
            v1 = self.vertices[id1]
            v2 = self.vertices[id2]

            # Add the new edge
            v1.neighbours.add(v2)
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError


class Paper:
    abstract: str
    authors: list[str]
    n_citation: int
    references: list[str]
    title: str
    venue: str
    year: int
    paper_id: str
    level: int
    url: str

    def __init__(self, abstract: str, authors: list[str],
                 n_citation: int, references: list[str], title: str, venue: str, year: int, paper_id: str) -> None:
        self.abstract = abstract
        self.title = title
        self.authors = authors
        self.references = references
        self.n_citation = n_citation
        self.venue = venue
        self.year = year
        self.paper_id = paper_id
        self.url = "https://www.google.com/404"


def process_row(row: list) -> Paper:
    abstract = row[0]

    authors_pre_split = row[1].strip("[]").split(', ')
    authors = [item.strip("'\"") for item in authors_pre_split]

    n_citations = int(row[2])

    references_pre_split = row[3].strip("[]").split(', ')
    references = [item.strip("'\"") for item in references_pre_split]

    title = row[4]

    venue = row[5]

    year = int(row[6])

    paper_id = row[7]
    return Paper(abstract, authors, n_citations, references, title, venue, year, paper_id)


def load_research_graph(csv_path: str = '../dblp-v10-2.csv') -> Graph:
    graph = Graph()

    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        print("Header:", header)
        for row in reader:
            graph.add_vertex(process_row(row))

    # Adding edges
    for paper in graph.vertices.values():
        p_id = paper.item.paper_id
        for x in paper.item.references:
            if x in graph.vertices:
                graph.add_edge(p_id, x)

    return graph
