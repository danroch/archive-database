import sqlite3 
import csv 


conn = sqlite3.connect('archive.db')
c = conn.cursor()

# create major table
query = (''' CREATE TABLE IF NOT EXISTS MAJOR
            (ID     INTEGER     PRIMARY KEY, 
            NAME    TEXT        NOT NULL, 
            UNIQUE(NAME)
                );''')
c.execute(query)

# create employer table
query = (''' CREATE         TABLE IF NOT EXISTS EMPLOYER
            (ID             INTEGER     PRIMARY KEY, 
            NAME            TEXT        NOT NULL, 
            HIRING_OFFICE   TEXT,
            DESCRIPTION     TEXT,  
            UNIQUE(NAME)
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

# create evaluation table and link with job (many to one relationship) 
query = (''' CREATE TABLE IF NOT EXISTS EVALUATION
            (ID                         INTEGER     PRIMARY_KEY, 
            JOB_ID                      INTEGER     NOT NULL,
            TERMS_OF_EMPLOYMENT         TEXT, 
            WHICH_COOP                  INTEGER, 
            DEPARTMENT                  TEXT, 
            WEEKLY_SCHEDULE             TEXT, 
            DAYS_PER_WEEK               INTEGER, 
            STIPEND                     TEXT, 
            TRANSPORTATION_ASSISTANCE   TEXT, 
            MEAL_ASSISTANCE             TEXT, 
            HOUSING_ASSISTANCE          TEXT, 
            RELOCATION_ASSISTANCE       TEXT,
            OTHER_INFORMATION           TEXT, 
            WAS_SHIFT_WORK_REQUIRED     INTEGER,
            OVERTIME_REQUIRED           INTEGER, 
            OVERTIME_HOURS              INTEGER,
            TRAVEL_PURPOSE              TEXT, 
            PUBLIC_TRANSPORT_ACCESS     INTEGER,
            EMPLOYER_ASSISTED_HOUSING   TEXT,
            NON_PHILLY_HOUSING_ARRANGE  TEXT, 
            COLLABORATION               INTEGER, 
            QUANTITY_AND_VARIETY        INTEGER, 
            FORM_MEANINGFUL_RELATIONS   INTEGER, 
            SUPERVISOR_ACCESS           INTEGER, 
            TRAINING                    INTEGER, 
            JOB_SATISFACTION            INTEGER, 
            RECOMMEND_TO_FRIEND         INTEGER, 
            ACCURATE_DESCRIPTION        INTEGER, 
            EXPLAIN_IF_NOT_ACCURATE     TEXT, 
            BEST_FEATURES               TEXT, 
            DRAWBACKS                   TEXT, 
            DESCRIBE_ON_RESUME          TEXT, 
            WRITTEN_COMMUNICATION       INTEGER, 
            VERBAL_COMMUNICATION        INTEGER, 
            ADJUSTING_STYLE             INTEGER, 
            CONTRIBUTING_IDEAS          INTEGER, 
            COMPLEX_PROBLEM_SOLVING     INTEGER, 
            EVALUATING_REL_INFO         INTEGER, 
            GOOD_DECISIONS              INTEGER, 
            ETHICAL_STANDARDS           INTEGER, 
            APPROPRIATE_TECHNOLOGY      INTEGER, 
            GOALS_AND_PROGRESS          INTEGER, 
            DIVERSE_BACKGROUND          INTEGER, 
            EFFECTIVE_WORK_HABITS       INTEGER, 
            PROACTIVE_SOLVING           INTEGER,        
            FOREIGN KEY(JOB_ID) REFERENCES JOB(ID),
            );''')

# populate major table 
with open('./Data/major.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        c.execute(
            "INSERT OR IGNORE INTO MAJOR (ID, NAME) VALUES (?, ?)", (row['ID'], row['NAME'])
        )

# populate employer table
with open('./Data/employer.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        c.execute(
                    "INSERT OR IGNORE INTO EMPLOYER (ID, NAME, HIRING_OFFICE, DESCRIPTION) VALUES (?, ?, ?, ?)",
                    (row['ID'], row['NAME'], row['HIRING_OFFICE'], row['DESCRIPTION'])
                )

# populate job table 
with open('./Data/job.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        c.execute(
                    "INSERT OR IGNORE INTO JOB (ID, EMPLOYER_ID, JOB_NAME, TYPE, LENGTH, DESCRIPTION, HAZARDOUS, RESEARCH, \
                    THIRD_PARTY, QUALIFICATIONS, EXPERIENCE, LOCATION, TRANSPORTATION, \
                    TRAVEL, TRAVEL_INFO, COMPENSATION_STATUS, OTHER_COMPENSATION, DETAILS, HOURS, MINIMUM_GPA, CITIZENSHIP, SCREENING) \
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (row['ID'], row['EMPLOYER_ID'], row['JOB_NAME'], row['TYPE'], row['LENGTH'], row['DESCRIPTION'], row['HAZARDOUS'],
                    row['RESEARCH'], row['THIRD_PARTY'], row['QUALIFICATIONS'], row['EXPERIENCE'], row['LOCATION'], row['TRANSPORTATION'],
                    row['TRAVEL'], row['TRAVEL_INFO'], row['COMPENSATION_STATUS'], row['OTHER_COMPENSATION'], row['DETAILS'], row['HOURS'],
                    row['MINIMUM_GPA'], row['CITIZENSHIP'], row['SCREENING'])
                )       

# populate job_major table
with open('./Data/job_major.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        c.execute(
            "INSERT OR IGNORE INTO JOB_MAJOR (JOB_ID, MAJOR_ID) VALUES (?, ?)", (row['JOB_ID'], row['MAJOR_ID'])
        )

conn.commit()