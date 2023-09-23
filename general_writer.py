# write to csv files that are used to populate every table besides the evaluation
import csv, time
from parse import Parser

def writeDB(sess, overviewURLs, parser):
    # write first row of each table
    with open('./Data/errors.csv', 'w') as f:
        error_writer = csv.writer(f)
        error_writer.writerow(('JOB_ID', 'ERROR'))

    with open('./Data/employer.csv', 'w') as f:
        employer_writer = csv.writer(f)
        employer_writer.writerow(("ID","NAME","HIRING_OFFICE","DESCRIPTION"))

    with open('./Data/job.csv', 'w') as f:
        job_writer = csv.writer(f)
        job_writer.writerow(('ID', 'EMPLOYER_ID', 'JOB_NAME', 'TYPE', 'LENGTH', 'DESCRIPTION',
            'HAZARDOUS', 'RESEARCH', 'THIRD_PARTY', 'QUALIFICATIONS', 'EXPERIENCE', 'LOCATION', 
            'TRANSPORTATION', 'TRAVEL', 'TRAVEL_INFO', 'COMPENSATION_STATUS', 'OTHER_COMPENSATION', 
            'DETAILS', 'HOURS', 'MINIMUM_GPA', 'CITIZENSHIP', 'SCREENING'))
    
    with open('./Data/job_major.csv', 'w') as f:
        job_major_writer = csv.writer(f)
        job_major_writer.writerow(('JOB_ID', 'MAJOR_ID'))

    with open('./Data/major.csv', 'w') as f:
        major_writer = csv.writer(f)
        major_writer.writerow(('ID', 'NAME'))

    # addresses the issue that majors don't have inherent id like jobs and employers 
    # does so by mapping each major to a particular id starting at 1
    major_id = {}
    

    # iterate through each overview url 
    counter = 1
    for url in overviewURLs:
        print(f'URL REQUESTED: {url}')
        time.sleep(.5)
        response4 = sess.get(url)
        
        # for debugging purposes 
        with open('./Data/test2.html', 'w') as f:
            f.write(response4.text)

        parser.setDoc(response4.text)

        # don't stop scraper but note which jobID caused the error 
        try:
            data = parser.relevantData()
        except Exception as e:
            with open('./Data/errors.csv', 'a') as f:
                errors_writer = csv.writer(f)
                errors_writer.writerow((url, e))

        for major in data['MAJOR']:
            # if the major is in the dictionary already, move on
            # otherwise, if searching for major yields an error, create a new key value pair 
            try:
                check = major_id[major] 
            except:
                major_id[major] = counter
                counter += 1                

        with open('./Data/employer.csv', 'a') as f:
            employer_writer = csv.writer(f)
            employer_writer.writerow(data['EMPLOYER'])

        with open('./Data/job.csv', 'a') as f:
            job_writer = csv.writer(f)
            job_writer.writerow(data['JOB'])

        with open('./Data/job_major.csv', 'a') as f:
            job_major_writer = csv.writer(f)
            # iterate through each major listed on a job, for each major, write the job id and the major id in csv to link tables
            for major in data['MAJOR']:
                job_major_writer.writerow((data['JOB'][0], major_id[major]))

    # populate major.csv with arbitrary key and title of major 
    with open('./Data/major.csv', 'a') as f:
        major_writer = csv.writer(f)
        for key in major_id:
            major_writer.writerow((major_id[key], key))