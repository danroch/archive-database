from flask import Flask, render_template, request
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