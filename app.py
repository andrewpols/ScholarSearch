import requests
from flask import Flask, render_template, request, redirect, url_for
from graph import Graph, load_research_graph
from search import CustomBM25Okapi, get_corpus, return_query, calculate_weight
from utils import is_partial_match

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


@app.route('/fetch_doi', methods=['POST'])
def fetch_doi():
    title = request.form.get('title')
    author = request.form.get('author')

    url = f"https://api.crossref.org/works?query.title={title}&query.author={author}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        items = data.get('message', {}).get('items', [])
        if items:
            doi_title = items[0].get('title', [''])[0]
            doi_url = items[0].get('URL', None)

            if doi_url and is_partial_match(title, doi_title):
                return redirect(doi_url)

        # Fallback to Google Scholar if no DOI found
        scholar_query = f"{title} {author}"
        encoded_query = requests.utils.requote_uri(scholar_query)
        return redirect(f'https://scholar.google.com/scholar?q={encoded_query}')

    except Exception as e:
        return str(e), 500


@app.route('/loading')
def loading():
    title = request.args.get('title')
    author = request.args.get('author')
    return render_template('loading.html', title=title, author=author)


if __name__ == '__main__':
    startup()
    app.run(debug=True)
