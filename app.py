from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            size INTEGER,
            cost REAL,
            gain REAL
        )
    ''')
    conn.commit()
    conn.close()

def get_all_projects():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, size, cost, gain FROM projects ORDER BY id ASC')
    rows = c.fetchall()
    conn.close()
    return rows

def insert_project(name, size, cost, gain):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO projects (name, size, cost, gain) VALUES (?, ?, ?, ?)',
              (name, size, cost, gain))
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# Add some sample data if empty
if len(get_all_projects()) == 0:
    sample = [
        ("Site Redesign", 12, 15000.0, 22000.0),
        ("Mobile App", 25, 35000.0, 50000.0),
        ("API Platform", 8, 9000.0, 12000.0)
    ]
    for s in sample:
        insert_project(*s)

@app.route('/')
def index():
    projects = get_all_projects()
    # Prepare data for charts
    labels = [p[1] for p in projects]
    sizes = [p[2] for p in projects]
    costs = [p[3] for p in projects]
    gains = [p[4] for p in projects]
    return render_template('index.html',
                           projects=projects,
                           labels=labels,
                           sizes=sizes,
                           costs=costs,
                           gains=gains)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        size = request.form.get('size') or 0
        cost = request.form.get('cost') or 0
        gain = request.form.get('gain') or 0
        try:
            size_i = int(size)
        except:
            size_i = 0
        try:
            cost_f = float(cost)
        except:
            cost_f = 0.0
        try:
            gain_f = float(gain)
        except:
            gain_f = 0.0
        insert_project(name, size_i, cost_f, gain_f)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<int:project_id>', methods=['POST'])
def delete(project_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__': 
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

