#!/usr/bin/env python3
"""
The Core Brief - Story Review Dashboard
Simple Flask app to review, filter, and rank aggregated stories.
"""

from flask import Flask, render_template, jsonify, send_from_directory
from pathlib import Path
import json
from datetime import datetime

app = Flask(__name__)

DATA_DIR = Path(__file__).parent.parent / "data" / "cache"


def load_latest_cache():
    """Load the most recent cache file."""
    cache_files = sorted(DATA_DIR.glob("fetch_*.json"), reverse=True)
    if not cache_files:
        return None
    
    with open(cache_files[0]) as f:
        return json.load(f)


@app.route('/')
def index():
    """Main dashboard page."""
    data = load_latest_cache()
    if not data:
        return "<h1>No data yet</h1><p>Run the aggregator first: <code>python src/aggregator.py</code></p>"
    
    return render_template('index.html', 
                         fetched_at=data['fetched_at'],
                         item_count=data['item_count'])


@app.route('/api/stories')
def api_stories():
    """Return stories as JSON."""
    data = load_latest_cache()
    if not data:
        return jsonify({'error': 'No data available'}), 404
    
    return jsonify(data)


@app.route('/api/stories/category/<category>')
def api_stories_by_category(category):
    """Filter stories by category."""
    data = load_latest_cache()
    if not data:
        return jsonify({'error': 'No data available'}), 404
    
    filtered = [item for item in data['items'] if item['category'] == category]
    return jsonify({'items': filtered, 'count': len(filtered)})


if __name__ == '__main__':
    app.run(debug=True, port=5050)
