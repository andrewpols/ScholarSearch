"""CSC111 Winter 2025 Project 2: Load Research Graph — (Graph Class and Paper Class)
This module contains the Graph, Vertex, and Paper classes.
It is responsible for loading the research graph from the csv file and returning a Graph object.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from kaggle.api.kaggle_api_extended import KaggleApi
import csv

KAGGLE_DATASET_INFO = {
    'user': 'nechbamohammed',
    'dataset': 'research-papers-dataset',
    'csv_file': 'dblp-v10.csv'
}


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
    """A graph used to represent the research papers.

    Representation Invariants:
    - all(isinsstance(vertex.item, paper) for vertex in self._vertices.values())
    - all(item == self._vertices[item.paper_id].item for item in self._vertices)
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
            - item.paper_id is a valid attribute

        >>> g = Graph()
        >>> p = Paper(['John Doe'], 10, ['1234'], 'A Study on Algorithms', 'Journal of Algorithms', '1234')
        >>> g.add_vertex(p)
        >>> g._vertices[p.paper_id].item == p
        True
        """
        self._vertices[item.paper_id] = _Vertex(item, set())

    def add_edge(self, id1: Any, id2: Any) -> None:
        """Add a directed edge from id1 to id2.

        Raise a ValueError if id1 or id2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2

        >>> g = Graph()
        >>> p1 = Paper(['John Doe'], 10, ['1234'], 'A Study on Algorithms', 'Journal of Algorithms', '1234')
        >>> p2 = Paper(['Jane Doe'], 5, ['1234'], 'A Study on Algorithms', 'Journal of Algorithms', '5678')
        >>> g.add_vertex(p1)
        >>> g.add_vertex(p2)
        >>> g.add_edge(p1.paper_id, p2.paper_id)
        >>> g._vertices[p2.paper_id] in g._vertices[p1.paper_id].neighbours
        True
        >>> g._vertices[p1.paper_id] in g._vertices[p2.paper_id].neighbours
        False
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

    Instance Attributes:
        - authors: The authors of the paper.
        - n_citation: The number of citations the paper has.
        - references: The references the paper has.
        - title: The title of the paper.
        - venue: The venue where the paper was published.
        - paper_id: The unique identifier of the paper.
    """
    abstract: str
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

    abstract = row[0]

    authors_pre_split = row[1].strip("[]").split(', ')
    authors = [item.strip("'\"") for item in authors_pre_split]

    n_citations = int(row[2])

    references_pre_split = row[3].strip("[]").split(', ')
    references = [item.strip("'\"") for item in references_pre_split]

    title = row[4]

    venue = row[5]

    paper_id = row[7]
    return Paper(abstract, authors, n_citations, references, title, venue, paper_id)


def download_kaggle_csv() -> None:
    """Download the .csv file associated with the kaggle dataset with name .... """
    user, dataset, csv_file = KAGGLE_DATASET_INFO['user'], KAGGLE_DATASET_INFO['dataset'], \
        KAGGLE_DATASET_INFO['csv_file']

    kaggle_api = KaggleApi()
    kaggle_api.authenticate()  # Either looks for ~/.kaggle/kaggle.json OR environment variables containing auth keys
    kaggle_api.dataset_download_files(dataset=f"{user}/{dataset}", path="../data", unzip=True)

    old_path = f"../data/{csv_file}"
    new_path = "../data/research-papers.csv"

    if os.path.exists(old_path):
        os.rename(old_path, new_path)
    else:
        raise IOError


def load_research_graph(csv_path: str = '../data/research-papers.csv') -> Graph:
    """
    Load the research graph from the csv file and return a Graph object.

    Preconditions:
        - csv_path is a valid path to the csv file.

    >>> g = load_research_graph('data/research-papers.csv')
    >>> 'Human intelligence needs artificial intelligence' in \
        {p.item.title for p in g.get_all_item_vertex_mappings().values()}
    True
    """
    if not os.path.exists('../data/research-papers.csv'):
        download_kaggle_csv()

    graph = Graph()

    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
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
    pass
    # Optional: Uncomment code for testing purposes
    # import python_ta.contracts
    #
    # python_ta.contracts.check_all_contracts()
    #
    # import doctest
    # doctest.testmod()
    # #
    # # import python_ta
    # #
    # # python_ta.check_all(config={
    # #     'extra-imports': ['csv'],  # the names (strs) of imported modules
    # #     'allowed-io': ['load_research_graph'],  # the names (strs) of functions that call print/open/input
    # #     'max-line-length': 120
    # # })
