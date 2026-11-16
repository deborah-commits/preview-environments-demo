import os
import time

import psycopg
from flask import Flask, abort, redirect, render_template_string, request
from psycopg.rows import dict_row

APP_TITLE = "Updated PR preview task board"
ACCENT = "#087f8c"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8192


def connect():
    url = os.environ.get("DATABASE_URL")
    if url:
        return psycopg.connect(url, row_factory=dict_row, connect_timeout=5)
    return psycopg.connect(
        host=os.environ["PG_HOST"], port=os.environ.get("PG_PORT", "5432"),
        dbname=os.environ["PG_DATABASE"], user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],
        sslmode=os.environ.get("PGSSLMODE", "require"),
        row_factory=dict_row, connect_timeout=5,
    )


def initialise():
    for attempt in range(20):
        try:
            with connect() as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS demo_tasks (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    title VARCHAR(120) NOT NULL UNIQUE,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )""")
                for title in ["Review the new homepage", "Check the signup flow", "Share feedback on the pull request"]:
                    conn.execute("INSERT INTO demo_tasks (title) VALUES (%s) ON CONFLICT (title) DO NOTHING", (title,))
            return
        except psycopg.OperationalError:
            if attempt == 19:
                raise
            print("Waiting for the demo database...", flush=True)
            time.sleep(2)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title>
<style>
:root{--accent:{{ accent }}}*{box-sizing:border-box}body{margin:0;background:#f5f6fb;color:#18213a;font-family:system-ui,-apple-system,sans-serif}
main{max-width:830px;margin:70px auto;padding:0 24px}.eyebrow{color:var(--accent);font-weight:750;font-size:12px;letter-spacing:2px;text-transform:uppercase}
h1{font-size:42px;letter-spacing:-1.5px;margin:12px 0}p{color:#68718a;line-height:1.6}.card{background:#fff;border:1px solid #e4e7f0;border-radius:18px;padding:28px;margin-top:30px;box-shadow:0 12px 40px #202d5410}
.stats{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #eef0f6;padding-bottom:20px;margin-bottom:20px}.stats strong{font-size:19px}.badge{font-size:12px;color:#16754c;background:#e8f7ef;border-radius:30px;padding:7px 12px}
.add{display:flex;gap:10px;margin-bottom:20px}input{flex:1;min-width:0;border:1px solid #dce0ec;border-radius:9px;padding:13px;font:inherit}button{cursor:pointer;font:inherit;border:0;border-radius:9px;padding:12px 18px;background:var(--accent);color:#fff;font-weight:650}
.task{display:flex;align-items:center;gap:14px;padding:17px 0;border-top:1px solid #eef0f6}.task .toggle{padding:0;background:transparent;color:#5f6980;font-size:24px;width:30px;height:32px}.task span{flex:1}.task.done span{text-decoration:line-through;color:#959caf}.delete{background:transparent;color:#8a93a9;padding:8px;font-size:12px}.footer{font-size:12px;margin-top:20px}button:focus-visible,input:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
@media(max-width:600px){main{margin:32px auto}h1{font-size:32px}.card{padding:20px}.badge{display:none}}
</style></head><body><main>
<div class="eyebrow">Pull request demo</div><h1>{{ title }}</h1>
<p>A small app for trying changes before they reach your users.</p>
<section class="card"><div class="stats"><strong>{{ remaining }} tasks remaining</strong><span class="badge">Connected to PostgreSQL</span></div>
<form class="add" method="post" action="/tasks"><input name="title" aria-label="New task" placeholder="Add a task to test this preview..." maxlength="120" required><button>Add task</button></form>
{% for task in tasks %}<div class="task {% if task.done %}done{% endif %}">
<form method="post" action="/tasks/{{ task.id }}/toggle"><button class="toggle" aria-label="Toggle task: {{ task.title }}">{{ '☑' if task.done else '☐' }}</button></form>
<span>{{ task.title }}</span><form method="post" action="/tasks/{{ task.id }}/delete"><button class="delete" aria-label="Delete task: {{ task.title }}">Delete</button></form></div>{% endfor %}
</section><p class="footer">Demo data only. Tasks are saved in this environment's database.</p>
</main></body></html>"""


@app.get("/")
def index():
    with connect() as conn:
        tasks = conn.execute("SELECT * FROM demo_tasks ORDER BY id").fetchall()
    return render_template_string(PAGE, title=APP_TITLE, accent=ACCENT, tasks=tasks,
                                  remaining=sum(not t["done"] for t in tasks))


@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    if not 1 <= len(title) <= 120:
        abort(400)
    with connect() as conn:
        conn.execute("INSERT INTO demo_tasks (title) VALUES (%s) ON CONFLICT (title) DO NOTHING", (title,))
    return redirect("/", code=303)


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    with connect() as conn:
        conn.execute("UPDATE demo_tasks SET done = NOT done WHERE id = %s", (task_id,))
    return redirect("/", code=303)


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    with connect() as conn:
        conn.execute("DELETE FROM demo_tasks WHERE id = %s", (task_id,))
    return redirect("/", code=303)


@app.get("/health")
def health():
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok"}
    except psycopg.Error:
        return {"status": "unavailable"}, 503


initialise()
