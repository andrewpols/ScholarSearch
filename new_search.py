import math
from collections import defaultdict
from typing import List, Dict, Tuple
import numpy as np

stop_words = {"the", "and", "of", "is", "about", "for", "paper", "study", "research", "result", "method",
              "approach", "show", "propose", "based", "analysis"}
# excluding certain keywords from consideration in the BM25 algorithm for enhanced efficiency

class BM25:
    def __init__(self, k1=1.25, b=0.75):
        self.k1 = k1  # free parameter (typically in the interval [1.2, 2]
        self.b = b  # free parameter (typically = .75)
        self.corpus = []
        self.doc_lengths = []
        self.average_doc_length = 0  # average document length
        self.df = defaultdict(int)  # document frequency
        self.idf = {}
        self.doc_count = 0

    def add_document(self, document: str):


    def calculate_idf(self):
        """Compute IDF scores for all query items"""
        for token, freq in self.df.items():
            self.idf[token] = math.log((self.doc_count - freq + 0.5) / (freq + 0.5) + 1)

    def calculate_scores(self, query: str):
        """Calculate BM25 scores for all documents"""
        query_tokens = query.lower().split()
        self.calculate_idf()
        scores = np.zeros(self.doc_count)

        for i, doc_tokens in enumerate(self.corpus):
            doc_length = self.doc_lengths[i]
            for token in query_tokens:
                if token not in self.idf:
                    continue
                else:
                    tf = doc_tokens.count(token)
                    numer = tf * (self.k1 + 1)
                    denom = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.average_doc_length))
                    scores[i] += self.idf[token] * numer/denom  # IDF(q) * TF(q,D)(k+1)/(TF(q,D) + k(1 - b + b(theta)))

        return scores


def get_corpus(g: Graph) -> list[tuple[str, str]]:
    graph_corpus = []
    for paper in g.vertices.values():
        title_words = [word.lower() for word in paper.item.title.split() if word.lower() not in stop_words]
        graph_corpus.append((paper.item.paper_id, " ".join(title_words)))
    return graph_corpus
