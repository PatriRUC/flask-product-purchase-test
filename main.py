from flask import Flask, request, jsonify
from flask import redirect, url_for
from flask_cors import CORS
from geo import find_events, find_detail, find_venue

app = Flask(__name__)
CORS(app)  

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('static', filename='try.html'))

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get("keyword", "")
    distance = request.args.get("distance", "10")
    category = request.args.get("category", "Default")
    location = request.args.get("location", "")
    return_data = jsonify(find_events(keyword, distance, category, location))
    return return_data

@app.route('/details', methods=['GET'])
def details():
    id = request.args.get("id", "")
    return_data = jsonify(find_detail(id))
    return return_data

@app.route('/venues', methods=['GET'])
def venues():
    keyword = request.args.get("keyword", "")
    return_data = jsonify(find_venue(keyword))
    return return_data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)

