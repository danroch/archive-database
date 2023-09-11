from bs4 import BeautifulSoup
import re 

class Parser:
    
    def __init__(self, html_doc):
        self.soup = BeautifulSoup(html_doc, 'html.parser')
        self.__jobIDS = []
        self.__evaluationURLs = []

    # returns value to send another request for all jobs to be displayed on one page 
    def howManyJobs(self):
        return self.soup.find('div', class_='centeraligntext').get_text().split()[5]

    def setDoc(self, html_doc):
        self.soup = BeautifulSoup(html_doc, 'html.parser') 

    def populateJobs(self):
        # find all job records (data cells with class as dddefault)
        records = self.soup.findAll('td', class_='dddefault')
        for record in records:
            # searches using regular expression to find numbers enclosed within parentheses     
            if str(record).find('evaluation') != -1:
                self.__jobIDS.append(re.search("\(\d+\)", str(record)).group()[1:-1]) 
        return self.__jobIDS

    def extractEvalURL(self):
        # only select the first evaluation 
        url = f"https://banner.drexel.edu{self.soup.find('td', class_='ddlabel').a['href']}"
        self.__evaluationURLs.append(url)
        return url 

    def getEvaluations(self):
        return self.__evaluationURLs


    # given some html document, extract all needed information to add to the database
    def relevantData(self):

        # get employer_id
        paragraphs = self.soup.find_all('p')
        for paragraph in paragraphs:
            if paragraph.span != None:
                employer_name = str(paragraph)[str(paragraph).find('span>')+5:str(paragraph).find(' (')].strip()
                hiring_office_location = str(paragraph)[str(paragraph).rfind('span>')+5:str(paragraph).rfind(' (')].strip()                
                if paragraph.span.text == 'Employer: ':
                    employer_id = re.search("\(\d+\)", paragraph.text).group()[1:-1]

        spans = self.soup.find_all('span')
        for span in spans:
            # get job type 
            if span.text == "Job's Type: ":
                job_type = span.next_sibling.next_sibling.text
            # get job length 
            if span.text == "Job's Length: ":
                job_length = span.next_sibling.next_sibling.text

        main_table = self.soup.find('table', class_="borderland")

        rows = main_table.findChildren('tr')

        job_id = re.search("\(\d+\)", rows[0].findChildren('td')[0].text).group()[1:-1]
        job_name = rows[0].findChildren('td')[0].text[0:-len(job_id)-2]
            
        db_translation = {'Yes': 1, 'No': 0}
        lowest_experience = 'NULL'
        for row in rows[1:]:
            cells = row.findChildren('td')
            for cell in cells:
                if cell.text.find("Division/Location/Company Description:") != -1:
                    company_description = cell.parent.next_sibling.next_sibling.findChildren('td')[0].text

                elif cell.text.find("Position Description:") != -1:
                    position_description = cell.parent.next_sibling.next_sibling.findChildren('td')[0].text
                # qualifications 
                elif cell.text.find("Recommended Qualifications: ") != -1:
                    position_qualifications = cell.parent.next_sibling.next_sibling.findChildren('td')[0].text

                elif cell.text.find('Majors') != -1:
                    majors_list = [major.text.split(' - ')[1].strip(', ') for major in cell.find_all('span')[1:]]

                # experience level 
                elif cell.text.find('Level(s)') != -1:
                    levels = ['Beginner', 'Intermediate', 'Advanced']
                    # only records lowest experience level  
                    for level in levels:
                        if cell.text.find(level) != -1: 
                            lowest_experience = level
                            break
                        else:
                            lowest_experience = 'NULL'
    
                elif cell.text.find('Position Address: ') != -1:
                    address = cell.text[len('Position Address: '):]

                elif cell.text.find('Job Location: ') != -1:
                    address = cell.text[len('Job Location: ') + 1:]
                # transportation 
                elif cell.text.find('Transportation to work:') != -1:
                    transportation = cell.text[len('Transportation to work: '):]

                # travel required?
                elif cell.text.find('Travel required for position: ') != -1:
                    travel_req = cell.text[len('Travel required for position: '):]
                    
                # anticipated travel information 
                elif cell.text.find('Anticipated travel information: ') != -1:
                    anticipated = cell.text[len('Anticipated travel information: '):]
                    if len(anticipated) == 0:
                        anticipated = 'NULL'
                # hrs/week
                elif cell.text.find('Approximate Hours Per Week:') != -1:
                    try:
                        hours = float(cell.text[len('Approximate Hours Per Week: '):])
                    except:
                        hours = 'NULL'

                # minimum GPA 
                elif cell.text.find('Minimum GPA: ') != -1: 
                    try:
                        minimum_gpa = float(cell.text[len('Minimum GPA: '):])
                    except:
                        minimum_gpa = 'NULL'

                # hazardous
                elif cell.text.find('hazard') != -1:
                    hazardous = db_translation[cell.text[len('Exposure to hazardous and/or biohazardous materials: '):]]

                # research position
                elif cell.text.find('Research Position: ') != -1:
                    research = db_translation[cell.text[len('Research Position: '):]]

                # 3rd party
                elif cell.text.find('Students are hired by a third-party employer: ') != -1:
                    third_party = db_translation[cell.text[len('Students are hired by a third-party employer: '):]]
                
                # citizenship restriction
                elif cell.text.find('Citizenship Restriction: ') != -1:
                    citizenship_restriction = cell.text[len('Citizenship Restriction: '):]
                    if citizenship_restriction == '- None -' or citizenship_restriction == 'None':
                        citizenship_restriction = 'NULL'
                elif cell.text.find('Pre-Employment Screening Requirements: ') != -1:
                    screening = cell.text[len('Pre-Employment Screening Requirements: '):]
                    if screening == '- None -' or screening == 'None':
                        screening = 'NULL'

                elif cell.text.find('Compensation Status: ') != -1:
                    compensation_status = cell.text[len('Compensation Status: '):]

                elif cell.text.find('Other Compensation: ') != -1:
                    other_compensation = cell.text[len('Other Compensation: '):]
                    if other_compensation == '- None -' or other_compensation == 'None':
                        other_compensation = 'NULL'
                elif cell.text.find('Other Compensation Details: ') != -1:
                    other_compensation_details = cell.text[len('Other Compensation Details: '):]
                    if other_compensation_details == '- None -' or other_compensation_details == 'None':
                        other_compensation_details = 'NULL'
        # return dictionary containing data to populate 1 row of each table
        return {'MAJOR': (majors_list), 'EMPLOYER': (employer_id, employer_name, hiring_office_location, company_description), 'JOB': (job_id, job_name, job_type, job_length, \
            position_description, hazardous, research, third_party, position_qualifications, lowest_experience, address, transportation, \
                travel_req, compensation_status, other_compensation, other_compensation_details, anticipated, hours, minimum_gpa, citizenship_restriction, screening)}

if __name__ == '__main__':
    with open('./Data/test2.html', 'r') as f:
        parser = Parser(f)
        data = parser.relevantData()
        print(data)
