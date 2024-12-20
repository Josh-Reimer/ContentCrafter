from flask import Flask, request, jsonify
from functools import wraps
import sqlite3
from flask import *

app = Flask(__name__)

# Sample credentials
USERNAME = "admin"
PASSWORD = "password123"

# Authentication decorator
def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

# Database initialization
def init_db():
    conn = sqlite3.connect('cms.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/pages', methods=['GET'])

def get_pages():
    """Get all pages."""
    conn = sqlite3.connect('cms.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content FROM pages')
    pages = cursor.fetchall()
    conn.close()
    return jsonify({str(page[0]): {"title": page[1], "content": page[2]} for page in pages})

@app.route('/api/pages/<int:page_id>', methods=['GET'])
@require_auth
def get_page(page_id):
    """Get a specific page by ID."""
    conn = sqlite3.connect('cms.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content FROM pages WHERE id = ?', (page_id,))
    page = cursor.fetchone()
    conn.close()
    if page:
        return jsonify({"title": page[1], "content": page[2]})
    return jsonify({"error": "Page not found"}), 404

@app.route('/api/pages', methods=['POST'])
@require_auth
def create_page():
    """Create a new page."""
    data = request.json
    title = data.get("title", "")
    content = data.get("content", "")
    conn = sqlite3.connect('cms.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pages (title, content) VALUES (?, ?)', (title, content))
    conn.commit()
    page_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Page created", "id": page_id}), 201

@app.route('/api/pages/<int:page_id>', methods=['PUT'])
@require_auth
def update_page(page_id):
    """Update an existing page."""
    data = request.json
    title = data.get("title", None)
    content = data.get("content", None)
    conn = sqlite3.connect('cms.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM pages WHERE id = ?', (page_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Page not found"}), 404
    cursor.execute('''
        UPDATE pages 
        SET title = COALESCE(?, title), content = COALESCE(?, content)
        WHERE id = ?
    ''', (title, content, page_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Page updated"})

@app.route('/api/pages/<int:page_id>', methods=['DELETE'])
@require_auth
def delete_page(page_id):
    """Delete a page."""
    conn = sqlite3.connect('cms.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pages WHERE id = ?', (page_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Page deleted"})
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "URL not found haha", "message": str(request.url)}), 404
@app.route("/editor.html")
def get_editor():
    return render_template("editor.html")

@app.route("/index.html")
@app.route("/")
def get_index():
    return render_template("index.html")

if __name__ == '__main__':
    init_db()
    app.run(debug=True,host='localhost')
