import pprint

from rank_bm25 import BM25Okapi
from graph import Graph, load_research_graph
import numpy as np


class CustomBM25Okapi(BM25Okapi):
    def get_top_n_paper_score(self, query: list[str], documents: list[tuple[str, str]], n=200) -> list[list]:
        scores = self.get_scores(query)
        top_n = np.argsort(scores)[::-1][:n]
        return [[documents[i][0], documents[i][1], scores[i], 0] for i in top_n]


def get_corpus(g: Graph) -> list[tuple[str, str]]:
    graph_corpus = []
    for paper in g.vertices.values():
        graph_corpus.append((paper.item.paper_id, paper.item.title))
    return graph_corpus


def get_most_cited_score(paper_scores, graph):
    for i in range(len(paper_scores)):
        paper_id = paper_scores[i][0]
        num_cited_by = len(graph.vertices[paper_id].neighbours)
        paper_scores[i][3] = num_cited_by

    weight_sim = 0.7
    weight_cite = 0.3

    max_sim = max(x[2] for x in paper_scores)
    max_cite = max(x[3] for x in paper_scores) if max(x[3] for x in paper_scores) > 0 else 1

    sorted_data = sorted(
        paper_scores,
        key=lambda x: weight_sim * (x[2] / max_sim) + weight_cite * (x[3] / max_cite),
        reverse=True
    )

    return sorted_data[:20]


def get_paper_by_title(graph, title):
    return next((paper for paper in graph.vertices.values() if paper.item.title == title), None)


def truncate_title(title, max_length=50):
    return title if len(title) <= max_length else title[:max_length - 3] + "..."


def set_up_corpus(g: Graph):
    corpus = get_corpus(graph)
    tokenized_corpus = [x[1].split(" ") for x in corpus]
    bm25 = CustomBM25Okapi(tokenized_corpus)
    return corpus, bm25


def build_query_graph(mega_graph: Graph, weighted_papers: list) -> Graph:
    query_graph = Graph()
    pprint.pprint(weighted_papers)
    for paper in weighted_papers:
        query_graph.add_vertex(mega_graph.vertices[paper[0]].item)
        query_graph.vertices[mega_graph.vertices[paper[0]].item.paper_id].level = 1

    values = list(query_graph.vertices.values())
    for paper in values:
        # if paper.item.url == "https://www.google.com/404":
            # paper.item.url = get_doi(paper.item.title, paper.item.authors)
        p_id = paper.item.paper_id
        for x in paper.item.references[:10]:
            if x in mega_graph.vertices:
                x_paper = mega_graph.vertices[x]
                # if x_paper.item.url == "https://www.google.com/404":
                    # x_paper.item.url = get_doi(x_paper.item.title, x_paper.item.authors)
                query_graph.add_vertex(x_paper.item)
            if x in query_graph.vertices:
                query_graph.add_edge(p_id, x)

    return query_graph


def return_query(graph: Graph, query: str, bm25, corpus: list) -> Graph:
    result = bm25.get_top_n_paper_score(query.split(" "), corpus)

    weighted_papers = get_most_cited_score(result, graph)

    query_graph = build_query_graph(graph, weighted_papers)

    return query_graph


def calculate_weight(x: int) -> int:
    if x > 50:
        return 16
    elif x > 25:
        return 13
    elif x > 10:
        return 10
    elif x > 5:
        return 7
    elif x > 2:
        return 5
    else:
        return 3


if __name__ == "__main__":
    graph = load_research_graph()

    corpus = get_corpus(graph)
    tokenized_corpus = [x[1].split(" ") for x in corpus]
    bm25 = CustomBM25Okapi(tokenized_corpus)

    result = bm25.get_top_n_paper_score('artificial intelligence'.split(" "), corpus)

    weighted_papers = get_most_cited_score(result, graph)

    for i, paper in enumerate(weighted_papers):
        title = truncate_title(paper[1], max_length=50)
        print(f"{i + 1:>2}.) Paper ID: {paper[0]} | Title: {title:<53} | "
              f"BM25 Score: {paper[2]:>6.2f} | Cited By: {paper[3]:>4}")
