import sqlite3 

conn = sqlite3.connect('archive.db')
c = conn.cursor()

# create major table
query = (''' CREATE TABLE IF NOT EXISTS MAJOR
            (ID     INTEGER     PRIMARY KEY, 
            NAME    TEXT        NOT NULL 
                );''')
c.execute(query)

# create employer table
query = (''' CREATE TABLE IF NOT EXISTS EMPLOYER
            (ID     INTEGER     PRIMARY KEY, 
            NAME    TEXT        NOT NULL 
                );''')
c.execute(query)

# create job table 
query = (''' CREATE TABLE IF NOT EXISTS JOB
            (ID             INTEGER     PRIMARY KEY, 
            EMPLOYER_ID     INTEGER     NOT NULL, 
            JOB_NAME        TEXT, 
            TYPE            TEXT, 
            LENGTH          TEXT,
            DESCRIPTION     TEXT,
            HAZARDOUS       INTEGER, 
            RESEARCH        INTEGER,
            THIRD_PARTY     INTEGER,
            QUALIFICATIONS  TEXT,
            EXPERIENCE      TEXT,
            LOCATION        TEXT,
            TRANSPORTATION  TEXT,
            TRAVEL          INTEGER,
            TRAVEL_INFO     TEXT, 
            COMPENSATION_STATUS TEXT, 
            OTHER_COMPENSATION  TEXT,
            DETAILS         TEXT, 
            HOURS           REAL, 
            MINIMUM_GPA     REAL, 
            CITIZENSHIP     TEXT,
            SCREENING       TEXT,
            FOREIGN KEY(EMPLOYER_ID) REFERENCES EMPLOYER(ID)
                );''')
c.execute(query)

# create link between job and major (many to many relationship)
query = (''' CREATE TABLE IF NOT EXISTS JOB_MAJOR
            (ID         INTEGER     PRIMARY KEY, 
            JOB_ID      INTEGER     NOT NULL, 
            MAJOR_ID    INTEGER     NOT NULL, 
            FOREIGN KEY(JOB_ID) REFERENCES JOB(ID),
            FOREIGN KEY(MAJOR_ID) REFERENCES MAJOR(ID) 
                );''')
c.execute(query)
