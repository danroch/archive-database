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

@app.route('/employer/<int:employer_id>')
def employer_detail(employer_id):
    con = sqlite3.connect('./Scraper/Data/archive.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    query = f'''
    SELECT e.ID, AVG(ev.JOB_SATISFACTION) as avg_job_satisfaction, AVG(ev.TRAINING) AS avg_training
    FROM EMPLOYER AS e
    LEFT JOIN JOB AS j on e.ID = j.EMPLOYER_ID
    LEFT JOIN EVALUATION AS ev ON j.ID = ev.JOB_ID
    WHERE e.ID = {employer_id};
    '''
    cur.execute(query)
    employer = cur.fetchone()

    if employer:
        avg_job_satisfaction = f"{employer['avg_job_satisfaction']: .2f}"
        return render_template('employer_detail.html', employer=employer, avg_job_satisfaction=avg_job_satisfaction)
    else:
        return "Employer not found", 404

if __name__=='__main__':
    app.run(debug=True)