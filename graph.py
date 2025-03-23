from __future__ import annotations
from typing import Any
import csv


class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.
    """
    item: Any
    neighbours: set[_Vertex]

    def __init__(self, item: Any, neighbours: set[_Vertex]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = neighbours

class Graph:
    """A graph.

    Representation Invariants:
    - all(item == self._vertices[item].item for item in self._vertices)
    """
    # Private Instance Attributes:
    #     - _vertices: A collection of the vertices contained in this graph.
    #                  Maps item to _Vertex instance.
    vertices: dict[Any, _Vertex]

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


def process_row(row) -> Paper:
    abstract = row[0]

    s = row[1].strip("[]").split(', ')
    authors = [item.strip("'\"") for item in s]

    n_citations = int(row[2])

    r = row[3].strip("[]").split(', ')
    references = [item.strip("'\"") for item in r]

    title = row[4]

    venue = row[5]

    year = int(row[6])

    paper_id = row[7]
    return Paper(abstract, authors, n_citations, references, title, venue, year, paper_id)


csv_path = '../dblp-v10-2.csv'

graph = Graph()

lst = []
with open(csv_path, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)
    print("Header:", header)
    for i, row in enumerate(reader):
        graph.add_vertex(process_row(row))

# Adding edges
for paper in graph.vertices:
    p_id = graph.vertices[paper].item.paper_id
    for x in graph.vertices[paper].item.references:
        if x in graph.vertices:
            graph.add_edge(x, p_id)

# Testing if edges work (THEY DO!)
print(graph.vertices["b24ba5c0-fee8-4a3e-9330-17f6564856cd"].item.title)
print("Cited by: ")
for x in graph.vertices["b24ba5c0-fee8-4a3e-9330-17f6564856cd"].neighbours:
    print(x.item.title)
