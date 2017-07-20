import sys

from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from flask import Flask,  render_template, json, request

app = Flask(__name__)

def to_dict(item):
    return {
        'score': item.score,
        'filename': item['filename'],
        'path': item['path']
    }

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/search/", methods=["GET"])
def search():
    keyword = request.args.get('q')
    ix = open_dir("indexdir")
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(keyword)
        results = searcher.search(query, limit=25)
        results = map(lambda x: to_dict(x), results)
        response = app.response_class(
            response=json.dumps(list(results)),
            status=200,
            mimetype='application/json'
        )
        return response

def main():
    app.run(debug=True)
 
if __name__ == '__main__':
    main()
