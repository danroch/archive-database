from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


@app.route("/job_list")
def job_list():
    con = sqlite3.connect('./Scraper/Data/archive.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM JOB")
    rows = cur.fetchall()
    con.close()
    return render_template('job_list.html', rows=rows)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    con = sqlite3.connect('./Scraper/Data/archive.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM JOB WHERE ID = ?", (job_id,))
    job = cur.fetchone()

    con.close()
    
    if job:
        return render_template('job_detail.html', job=job)
    else:
        return "Job not found", 404


