"""
This module contains the BM25 model for information retrieval and the functions to return the query graph based on the
given query.
It is responsible for tokenizing the text, calculating the BM25 scores, and building the query graph based on the
weighted papers with the highest scores (i.e. most related to the given query).
"""

import math
from collections import defaultdict

from graph import Graph, load_research_graph
from utils import tokenize


class BM25:
    """
    A BM25 ranking model for information retrieval.

    Instance Attributes:
    - k1: Term frequency saturation parameter.
    - b: Document length normalization parameter.
    - tokenized_corpus: Tokenized documents.
    - doc_count: Total number of documents.
    - doc_lengths: Lengths of documents.
    - average_doc_length: Average document length.
    - frequencies: (DF: doc frequency, IDF: inverse doc frequency).
    """

    k1: float
    b: float
    tokenized_corpus: list
    doc_count: int
    doc_lengths: list[int]
    average_doc_length: float
    frequencies: tuple[dict, dict]

    def __init__(self, tokenized_corpus_list: list, k1: float = 1.25, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.tokenized_corpus = tokenized_corpus_list
        self.doc_count = len(tokenized_corpus_list)
        self.doc_lengths = [len(doc) for doc in tokenized_corpus_list]
        self.average_doc_length = sum(self.doc_lengths) / self.doc_count if self.doc_count > 0 else 1
        self.frequencies = (defaultdict(int), {})  # (DF, IDF)

        # Calculate document frequencies (DF)
        for doc_tokens in tokenized_corpus_list:
            unique_tokens = set(doc_tokens)
            for token in unique_tokens:
                self.frequencies[0][token] += 1

        self.calculate_idf()

    def calculate_idf(self) -> None:
        """Compute IDF scores for all query items"""
        for token, freq in self.frequencies[0].items():
            self.frequencies[1][token] = math.log((self.doc_count - freq + 0.5) / (freq + 0.5) + 1)

    def get_scores(self, query: str) -> list[float]:
        """Calculate BM25 scores for all documents"""
        query_tokens = tokenize(query)
        scores = [0.0] * self.doc_count

        for i, doc_tokens in enumerate(self.tokenized_corpus):
            doc_length = self.doc_lengths[i]
            for token in query_tokens:
                if token not in self.frequencies[1]:
                    continue
                tf = doc_tokens.count(token)
                numer = tf * (self.k1 + 1)
                denom = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.average_doc_length))
                scores[i] += self.frequencies[1][token] * numer / denom

        return scores

    def get_top_n_paper_score(self, query: str, corpus_list: list) -> list:
        """
        Return a list of the top N papers with scores (maintaining your original format)
        """
        scores = self.get_scores(query)
        score_results = [
            [corpus_list[i][0], corpus_list[i][1], scores[i], 0]
            for i in range(len(scores))
        ]
        return sorted(score_results, key=lambda x: x[2], reverse=True)[:200]


def get_corpus(g: Graph) -> list:
    """
    Return a list of the corpus (paper titles) for the BM25 model.
    The corpus is a list of tuples where each tuple contains the paper ID and the tokenized title.
    This is used to calculate the BM25 scores for the papers.
    """
    graph_corpus = []
    for paper in g.get_all_item_vertex_mappings().values():
        title_words = tokenize(paper.item.title)
        graph_corpus.append((paper.item.paper_id, " ".join(title_words)))
    return graph_corpus


def get_most_cited_score(paper_scores: list, g: Graph) -> list:
    """
    Return a list of the top 100 papers with the highest scores. The score is calculated as a weighted sum of the BM25
    score and the number of citations.
    """
    for paper in paper_scores:
        paper_id = paper[0]
        num_cited_by = len(g.get_all_item_vertex_mappings()[paper_id].neighbours)
        paper[3] = num_cited_by

    weight_sim = 0.7
    weight_cite = 0.3

    max_sim = max(x[2] for x in paper_scores) if any(x[2] > 0 for x in paper_scores) else 1
    max_cite = max(x[3] for x in paper_scores) if any(x[3] > 0 for x in paper_scores) else 1

    sorted_data = sorted(
        paper_scores,
        key=lambda x: weight_sim * (x[2] / max_sim) + weight_cite * (x[3] / max_cite),
        reverse=True
    )

    return sorted_data[:100]


def build_query_graph(mega_graph: Graph, weighted_papers: list) -> Graph:
    """
    Return a query graph based on the weighted papers with the highest scores.
    This is a helper function for the return_query function meant to build the query graph based on the
    given weighted papers.
    """
    query_graph = Graph()
    for paper in weighted_papers:
        query_graph.add_vertex(mega_graph.get_all_item_vertex_mappings()[paper[0]].item)

        paper_vertex = mega_graph.get_all_item_vertex_mappings()[paper[0]]

        query_graph.get_all_item_vertex_mappings()[paper_vertex.item.paper_id].level = 1

    values = list(query_graph.get_all_item_vertex_mappings().values())
    for paper in values:
        p_id = paper.item.paper_id
        for x in paper.item.references[:10]:
            if x in mega_graph.get_all_item_vertex_mappings():
                x_paper = mega_graph.get_all_item_vertex_mappings()[x]
                query_graph.add_vertex(x_paper.item)
            if x in query_graph.get_all_item_vertex_mappings():
                query_graph.add_edge(p_id, x)

    return query_graph


def return_query(g: Graph, query: str, bm25_model: BM25, corpus_list: list) -> Graph:
    """
    Return a query graph based on the given query, BM25 model, and corpus.
    """
    result = bm25_model.get_top_n_paper_score(query, corpus_list)

    weighted_papers = get_most_cited_score(result, g)

    query_graph = build_query_graph(g, weighted_papers)

    return query_graph


def filter_query(g: Graph, citations: str, author: str, venue: str) -> Graph:
    """
    Filter the query graph based on the given citations, author, and venue.
    """
    for paper in g.get_all_item_vertex_mappings().values():
        if paper.item.n_citation < int(citations):
            paper.visible = False
    if author != "0":
        for paper in g.get_all_item_vertex_mappings().values():
            if author not in paper.item.authors:
                paper.visible = False
    if venue != "0":
        for paper in g.get_all_item_vertex_mappings().values():
            if venue != paper.item.venue:
                paper.visible = False
    return g


def get_all_authors(g: Graph) -> list[str]:
    """
    Return a list of all authors in the graph.
    """
    authors = []
    for paper in g.get_all_item_vertex_mappings().values():
        for author in paper.item.authors:
            authors.append(author)
    return authors


def get_all_venues(g: Graph) -> list[str]:
    """
    Return a list of all venues in the graph.
    """
    venues = []
    for paper in g.get_all_item_vertex_mappings().values():
        if paper.item.venue not in venues:
            venues.append(paper.item.venue)
    return [x for x in venues if x.strip()]


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['math', 'collections', 'graph', 'utils'],  # the names (strs) of imported modules
        'allowed-io': ['BM25.get_scores', 'filter_query'],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })

    graph = load_research_graph()
    corpus = get_corpus(graph)
    tokenized_corpus = [tokenize(x[1]) for x in corpus]

    bm25 = BM25(tokenized_corpus)

    # Search and rank
    results = bm25.get_top_n_paper_score("artificial intelligence", corpus)
    final_results = get_most_cited_score(results, graph)
