"""CSC111 Winter 2025 Project 2: Main Flask Application — ScholarNet
This module contains the main Flask application for the project. It is responsible for handling the user interface and
interacting with the backend to display the search results.
"""
from typing import Union

import requests
from flask import Flask, Response, render_template, request, redirect, url_for
from graph import load_research_graph
from search import BM25, filter_query, get_corpus, return_query, get_all_authors, \
    get_all_venues, tokenize
from utils import is_partial_match, calculate_weight


app = Flask(__name__)


@app.route('/')
def home() -> str:
    """
    Return the string redirecting to the main page of the application.
    """
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search() -> Response:
    """
    Return a Response associated with the search query provided by the user. Redirect the user to the results page
    with the given data to display the search results.
    """
    query = request.form['query']
    citations_filter = request.form.get('citations_filter', 0)
    author_filter = request.form.get('author_filter', "0")
    venue_filter = request.form.get('venue_filter', "0")
    return redirect(url_for('results', query=query, citations_filter=citations_filter,
                            author_filter=author_filter, venue_filter=venue_filter))


@app.route('/results')
def results() -> str:
    """
    Return a string redirecting the user to the results page based on the searched query and filters.
    This is the main search results page where the user can see the search results and apply filters based on their
    input. The search results are visualized as a graph with nodes representing papers and edges representing citations.
    """
    query = request.args.get('query', '')
    if query not in search_history[-3:]:
        search_history.append(query)
    citations_filter = request.args.get('citations_filter', '')
    author_filter = request.args.get('author_filter', '0')
    venue_filter = request.args.get('venue_filter', '0')

    query_graph = filter_query(return_query(mega_graph, query, bm25, corpus), citations_filter, author_filter,
                               venue_filter)
    authors = get_all_authors(query_graph)
    venues = get_all_venues(query_graph)
    query_dict = query_graph.get_all_item_vertex_mappings()
    nodes_data = [{"id": query_dict[key].item.paper_id,
                   "title": query_dict[key].item.title,
                   "weight": calculate_weight(len(query_dict[key].neighbours)),
                   "group": query_dict[key].level,
                   "authors": query_dict[key].item.authors}
                  for key in query_dict if query_dict[key].visible]
    links_data = []
    for paper in query_dict:
        for x in query_dict[paper].item.references:
            if x in query_dict and query_dict[x].visible and query_dict[paper].visible:
                links_data.append({"source": query_dict[x].item.paper_id,
                                   "target": query_dict[paper].item.paper_id})
    return render_template('query.html', nodesData=nodes_data, linksData=links_data, query=query,
                           authors=authors, venues=venues, searchHistory=search_history)


@app.route('/fetch_doi', methods=['POST'])
def fetch_doi() -> Union[Response | tuple[str, int]]:
    """
    Return the Response associated with the DOI link for a paper based on the title and author provided by the user.
    If a DOI is found, redirect the user. Otherwise, redirect to Google Scholar.

    Return an error message if the request fails.
    """
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

    except requests.exceptions.RequestException as e:
        return str(e), 500


@app.route('/loading')
def loading() -> str:
    """
    Return a string redirecting the user to the loading page with the title and author of the paper passed as a query,
    along with a loading message during the retrieval.
    """
    title = request.args.get('title')
    author = request.args.get('author')
    return render_template('loading.html', title=title, author=author)


if __name__ == '__main__':
    # Optional: Uncomment code for testing purposes
    # import python_ta.contracts
    #
    # python_ta.contracts.check_all_contracts()
    #
    # import python_ta
    #
    # python_ta.check_all(config={
    #     # the names (strs) of imported modules
    #     'extra-imports': ['requests', 'flask', 'search', 'utils', 'graph', 'typing', 'calculate_weight'],
    #     'allowed-io': [],  # the names (strs) of functions that call print/open/input
    #     'max-line-length': 120
    # })

    csv_path = 'data/research-papers.csv'
    mega_graph = load_research_graph(csv_path)
    corpus = get_corpus(mega_graph)
    tokenized_corpus = [tokenize(x[1]) for x in corpus]
    bm25 = BM25(tokenized_corpus)
    search_history = []

    app.run(debug=True)
