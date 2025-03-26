from rank_bm25 import BM25Okapi
from graph import Graph, load_research_graph
import numpy as np


class CustomBM25Okapi(BM25Okapi):
    def get_top_n_paper_score(self, query: list[str], documents: list[str], n=200) -> list[list]:
        scores = self.get_scores(query)
        top_n = np.argsort(scores)[::-1][:n]
        return [[documents[i], scores[i], 0] for i in top_n]


def get_corpus(g: Graph) -> list[str]:
    graph_corpus = []
    for paper in g.vertices.values():
        graph_corpus.append(paper.item.title)

    return graph_corpus


def get_most_cited_score(paper_scores, graph):
    for i in range(len(paper_scores)):
        title = paper_scores[i][0]
        num_cited_by = len(get_paper_by_title(graph, title).neighbours)
        paper_scores[i][2] = num_cited_by
        # print(f"{i+1}.) Cited by: {num_cited_by}")

    # Weights: similarity matters more
    weight_sim = 0.7  # Weight for similarity
    weight_cite = 0.3  # Weight for citation count

    # Normalization: Find max values to scale scores
    max_sim = max(x[1] for x in paper_scores)  # Max similarity
    max_cite = max(x[2] for x in paper_scores)  # Max citation count

    # Sorting with weighted normalized scores
    sorted_data = sorted(
        paper_scores,
        key=lambda x: weight_sim * (x[1] / max_sim) + weight_cite * (x[2] / max_cite),
        reverse=True  # Higher weighted score is better
    )

    return sorted_data[:20]


def get_paper_by_title(graph, title):
    return next((paper for paper in graph.vertices.values() if paper.item.title == title), None)


# def get_top_n_papers(query: str, n: int = 100) -> None:
#     query = query.split()
#     result = bm25.get_top_n(query, corpus, n)
#     pprint.pprint(result)

def truncate_title(title, max_length=50):
    return title if len(title) <= max_length else title[:max_length-3] + "..."


if __name__ == "__main__":
    graph = load_research_graph()

    corpus = get_corpus(graph)
    tokenized_corpus = [x.split(" ") for x in corpus]
    bm25 = CustomBM25Okapi(tokenized_corpus)

    result = bm25.get_top_n_paper_score('aritificial intelligence'.split(" "), corpus)

    # pprint.pprint(result)

    weighted_papers = get_most_cited_score(result, graph)

    for i, paper in enumerate(weighted_papers):
        title = truncate_title(paper[0], max_length=50)  # Limit title length
        print(f"{i + 1:>2}.) Title: {title:<53} | BM25 Score: "
              f"{paper[1]:>6.2f} | Cited By: {paper[2]:>4}")
