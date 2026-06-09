from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except Exception:
            return []
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def next_id(tasks):
    return max((t["id"] for t in tasks if "id" in t), default=0) + 1

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add_task():
    data = request.get_json() if request.is_json else request.form
    text = (data.get("task") or "").strip()
    if not text:
        return jsonify({"success": False, "error": "Empty task"}), 400
    tasks = load_tasks()
    task = {
        "id": next_id(tasks),
        "text": text,
        "completed": False,
        "priority": data.get("priority", "medium"),
        "due_date": data.get("due_date", ""),
        "created_at": datetime.now().isoformat()
    }
    tasks.append(task)
    save_tasks(tasks)
    return jsonify({"success": True, "task": task})

@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = not t.get("completed", False)
            save_tasks(tasks)
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    data = request.get_json() if request.is_json else request.form
    text = (data.get("task") or "").strip()
    if not text:
        return jsonify({"success": False, "error": "Empty task"}), 400
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["text"] = text
            t["priority"] = data.get("priority", "medium")
            t["due_date"] = data.get("due_date", "")
            save_tasks(tasks)
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route("/delete/<int:task_id>", methods=["DELETE", "POST"])
def delete_task(task_id):
    tasks = load_tasks()
    new = [t for t in tasks if t["id"] != task_id]
    if len(new) == len(tasks):
        return jsonify({"success": False}), 404
    save_tasks(new)
    return jsonify({"success": True})

@app.route("/clear-completed", methods=["POST"])
def clear_completed():
    tasks = [t for t in load_tasks() if not t.get("completed")]
    save_tasks(tasks)
    return jsonify({"success": True})

@app.route("/api/tasks")
def api_tasks():
    return jsonify({"success": True, "tasks": load_tasks()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
