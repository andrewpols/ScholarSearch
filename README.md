# ScholarSearch

## About
ScholarSearch is a Python-based web application that collects user queries on a scholarly subject and returns a graph of related papers.

Each query graph has the following structure:
- Blue nodes are highly relevant papers which are the most cited papers found on that topic.
- Orange nodes are papers which cite those of the blue nodes.
- The blue and orange nodes are interconnected with each other based on the citations between them to form a graph.
- The more times a paper has been cited, the larger its node.


## Installation
- Either download this repository or clone it with GitHub: 

      git clone https://github.com/andrewpols/ScholarSearch

- To generate recommended papers, the search algorithm requires candidate papers. The papers this app uses are from a Kaggle CSV dataset sourced from https://www.kaggle.com/datasets/nechbamohammed/research-papers-dataset.
- You may either
  1. Download the CSV directly, name it `research-papers.csv`, and place it in the `ScholarSearch/scholar-search/data` directory.
     OR
  2. Place your Kaggle API credentials in `ScholarSearch/scholar-search/src/.env`; the environment variables are already set up in the file. For information on how to obtain Kaggle API credentials (free), please see the "Authentication" section of https://www.kaggle.com/docs/api.


 - Finally, download all required libraries in `ScholarSearch/scholar-search/src/requirements.txt`.

## Running the Application
To run the web app, you may run the Flask App directly by moving to `ScholarSearch/scholar-search/src` and running:
  
    python __init__.py

You may also run this through the Gunicorn WSGI by moving to `ScholarSearch/scholar-search/src` and running:
        
      gunicorn --config gunicorn_config.py wsgi:app

or by specifying your own Gunicorn config settings.

## Usage
Proceed to the localhost specified in the terminal. You will be met with a search screen to type in your queries. From there, you may search, drag, and interact with your generated graph. 
Clicking on a node will direct you to the paper's link via its DOI with Crossref. In rare cases where no link is found, the search is redirected to Google Scholar.
Happy searching!
