from flask import Flask, render_template, request, redirect, url_for
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


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    return redirect(url_for('results', query=query))


@app.route('/results')
def results():
    query = request.args.get('query', '')
    query_graph = return_query(mega_graph, query, bm25, corpus)
    nodes_data = [{"id": query_graph.vertices[key].item.paper_id,
                   "title": query_graph.vertices[key].item.title,
                   "weight": calculate_weight(len(query_graph.vertices[key].neighbours)),
                   "group": query_graph.vertices[key].level,
                   "authors": query_graph.vertices[key].item.authors}
                  for key in query_graph.vertices]
    links_data = []
    for paper in query_graph.vertices:
        for x in query_graph.vertices[paper].item.references:
            if x in query_graph.vertices:
                links_data.append({"source": query_graph.vertices[x].item.paper_id,
                                   "target": query_graph.vertices[paper].item.paper_id})
    return render_template('query.html', nodesData=nodes_data, linksData=links_data, query=query)


@app.route('/loading')
def loading():
    return render_template("loading.html")


if __name__ == '__main__':
    startup()
    app.run(debug=True)
