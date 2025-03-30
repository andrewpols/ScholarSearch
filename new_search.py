import math
import pprint
from collections import defaultdict
from graph import Graph, load_research_graph
from typing import List, Dict, Tuple

stop_words = {"the", "and", "of", "is", "about", "for", "paper", "study", "research", "result", "method",
              "approach", "show", "propose", "based", "analysis"}

def tokenize(text):
    return [word.lower() for word in text.split() if word.isalpha() and word.lower() not in stop_words]


class BM25:
    def __init__(self, tokenized_corpus: list, k1=1.25, b=0.75):
        self.k1 = k1
        self.b = b
        self.tokenized_corpus = tokenized_corpus
        self.doc_count = len(tokenized_corpus)
        self.doc_lengths = [len(doc) for doc in tokenized_corpus]
        self.average_doc_length = sum(self.doc_lengths) / self.doc_count if self.doc_count > 0 else 1
        self.df = defaultdict(int)
        self.idf = {}

        # Calculate document frequencies (DF)
        for doc_tokens in tokenized_corpus:
            unique_tokens = set(doc_tokens)
            for token in unique_tokens:
                self.df[token] += 1

        self.calculate_idf()

    def calculate_idf(self):
        """Compute IDF scores for all query items"""
        for token, freq in self.df.items():
            self.idf[token] = math.log((self.doc_count - freq + 0.5) / (freq + 0.5) + 1)

    def get_scores(self, query: str) -> list[float]:
        """Calculate BM25 scores for all documents"""
        query_tokens = tokenize(query)
        print(f"Filtered Query Tokens: {query_tokens}")
        scores = [0.0] * self.doc_count

        for i, doc_tokens in enumerate(self.tokenized_corpus):
            doc_length = self.doc_lengths[i]
            for token in query_tokens:
                if token not in self.idf:
                    continue
                tf = doc_tokens.count(token)
                numer = tf * (self.k1 + 1)
                denom = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.average_doc_length))
                scores[i] += self.idf[token] * numer / denom

        return scores

    def get_top_n_paper_score(self, query, corpus):
        """
        Get top N papers with scores (maintaining your original format)
        """
        scores = self.get_scores(query)
        results = [
            [corpus[i][0], corpus[i][1], scores[i], 0]
            for i in range(len(scores))
        ]
        return sorted(results, key=lambda x: x[2], reverse=True)[:200]


def get_corpus(g: Graph) -> list:
    graph_corpus = []
    for paper in g.vertices.values():
        title_words = tokenize(paper.item.title)
        graph_corpus.append((paper.item.paper_id, " ".join(title_words)))
    return graph_corpus


def get_most_cited_score(paper_scores, graph):
    for i in range(len(paper_scores)):
        paper_id = paper_scores[i][0]
        num_cited_by = len(graph.vertices[paper_id].neighbours)
        paper_scores[i][3] = num_cited_by

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


def truncate_title(title, max_length=50):
    return title if len(title) <= max_length else title[:max_length - 3] + "..."

def set_up_corpus(g: Graph):
    corpus = get_corpus(graph)
    tokenized_corpus = [tokenize(x[1]) for x in corpus]
    bm25 = BM25(tokenized_corpus)
    return corpus, bm25


def build_query_graph(mega_graph: Graph, weighted_papers: list) -> Graph:
    query_graph = Graph()
    pprint.pprint(weighted_papers)
    for paper in weighted_papers:
        query_graph.add_vertex(mega_graph.vertices[paper[0]].item)
        query_graph.vertices[mega_graph.vertices[paper[0]].item.paper_id].level = 1

    values = list(query_graph.vertices.values())
    for paper in values:
        p_id = paper.item.paper_id
        for x in paper.item.references[:10]:
            if x in mega_graph.vertices:
                x_paper = mega_graph.vertices[x]
                query_graph.add_vertex(x_paper.item)
            if x in query_graph.vertices:
                query_graph.add_edge(p_id, x)

    return query_graph


def return_query(graph: Graph, query: str, bm25, corpus: list) -> Graph:
    result = bm25.get_top_n_paper_score(query, corpus)

    weighted_papers = get_most_cited_score(result, graph)

    query_graph = build_query_graph(graph, weighted_papers)

    return query_graph


def filter_query(graph: Graph, citations: str, author: str, venue: str) -> Graph:
    print(venue)
    for paper in graph.vertices.values():
        if paper.item.n_citation < int(citations):
            paper.visible = False
    if author != "0":
        for paper in graph.vertices.values():
            if author not in paper.item.authors:
                paper.visible = False
    if venue != "0":
        for paper in graph.vertices.values():
            if venue != paper.item.venue:
                paper.visible = False
    return graph


def get_all_authors(graph: Graph) -> list[str]:
    authors = []
    for paper in graph.vertices.values():
        for author in paper.item.authors:
            authors.append(author)
    return authors


def get_all_venues(graph: Graph) -> list[str]:
    venues = []
    for paper in graph.vertices.values():
        if paper.item.venue not in venues:
            venues.append(paper.item.venue)
    return [x for x in venues if x.strip()]


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
    tokenized_corpus = [tokenize(x[1]) for x in corpus]

    bm25 = BM25(tokenized_corpus)

    # Search and rank
    results = bm25.get_top_n_paper_score("artificial intelligence", corpus)
    final_results = get_most_cited_score(results, graph)

    # Print results
    for i, (pid, title, score, cites) in enumerate(final_results, 1):
        title = truncate_title(title, 50)
        print(f"{i:>2}.) {pid} | {title:<50} | Score: {score:.2f} | Cites: {cites}")
