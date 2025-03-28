from flask import Flask, render_template
from graph import Graph, load_research_graph, Paper
from search import CustomBM25Okapi, set_up_corpus, get_corpus, return_query, calculate_weight
import csv

app = Flask(__name__)
mega_graph = Graph()
corpus = []
bm25 = None


def startup():
    csv_path = '../dblp-v10-2.csv'
    global mega_graph
    global corpus
    global bm25

    mega_graph = load_research_graph(csv_path)
    corpus = get_corpus(mega_graph)
    tokenized_corpus = [x[1].split(" ") for x in corpus]
    bm25 = CustomBM25Okapi(tokenized_corpus)

    # mega_graph.add_vertex(Paper("Some Paper 1", ["Raihaan", "Shahmeer", "Andrew"], 5,
    #                          ["2", "3"], "Paper 1", "Toronto", 2025, "1"))
    # mega_graph.add_vertex(Paper("Some Paper 2", ["Raihaan", "Shahmeer", "Andrew"], 2,
    #                          [], "Paper 2", "Toronto", 2025, "2"))
    # mega_graph.add_vertex(Paper("Some Paper 3", ["Raihaan", "Shahmeer", "Andrew"], 1,
    #                          ["2"], "Paper 3", "Toronto", 2025, "3"))
    # mega_graph.add_vertex(Paper("Some Paper 4", ["Raihaan", "Shahmeer", "Andrew"], 4,
    #                          ["2", "1"], "Paper 4", "Toronto", 2025, "4"))
    # mega_graph.add_vertex(Paper("Some Paper 5", ["Raihaan", "Shahmeer", "Andrew"], 3,
    #                          ["4"], "Paper 4", "Toronto", 2025, "5"))
    # # Adding edges
    # for paper in mega_graph.vertices:
    #     p_id = mega_graph.vertices[paper].item.paper_id
    #     for x in mega_graph.vertices[paper].item.references:
    #         if x in mega_graph.vertices:
    #             mega_graph.add_edge(x, p_id)


@app.route('/')
def home():
    global mega_graph
    global corpus
    global bm25
    query = "clinical trials"
    query_graph = return_query(mega_graph, query, bm25, corpus)
    nodes_data = [{"id": query_graph.vertices[key].item.paper_id,
                   "title": query_graph.vertices[key].item.title,
                   "weight": calculate_weight(len(query_graph.vertices[key].neighbours)),
                   "group": query_graph.vertices[key].level,
                   "authors": query_graph.vertices[key].item.authors}
                  for key in query_graph.vertices]
    links_data = []
    for paper in query_graph.vertices:
        print(len(query_graph.vertices[paper].neighbours))
        for x in query_graph.vertices[paper].item.references:
            if x in query_graph.vertices:
                links_data.append({"source": query_graph.vertices[x].item.paper_id,
                                   "target": query_graph.vertices[paper].item.paper_id})

    return render_template('index.html', nodesData=nodes_data, linksData=links_data, query=query)


@app.route('/loading')
def loading():
    return render_template("loading.html")


if __name__ == '__main__':
    startup()
    app.run(debug=True)
