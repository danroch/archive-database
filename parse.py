from bs4 import BeautifulSoup
import re, unicodedata

class Parser:
    
    def __init__(self, html_doc):
        self.soup = BeautifulSoup(html_doc, 'html.parser')
        self.__jobIDS = []
        self.__overviewURLs = []
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

    def extract_URLs(self):
        # only select the first evaluation 
        url = f"https://banner.drexel.edu{self.soup.find('td', class_='ddlabel').a['href']}"
        self.__overviewURLs.append(url)

        # select all evaluations
        for extension in self.soup.find_all('td', class_="dddefault"):
            url = f"https://banner.drexel.edu{extension.a['href']}" 
            self.__evaluationURLs.append(url)

    def getOverviews(self):
        return self.__overviewURLs

    def getEvaluations(self):
        return self.__evaluationURLs

    # given some html document, extract all needed information to add to the database (with exception of evaluation db)
    def overviewData(self):
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
        other_compensation = 'NULL'
        for row in rows[1:]:
            cells = row.findChildren('td')
            for cell in cells:
                if cell.text.find("Division/Location/Company Description:") != -1:
                    company_description = re.sub('(\n|\r)', ' ', cell.parent.next_sibling.next_sibling.findChildren('td')[0].text)

                elif cell.text.find("Position Description:") != -1:
                    position_description = re.sub('(\n|\r)', ' ', cell.parent.next_sibling.next_sibling.findChildren('td')[0].text)
                # qualifications 
                elif cell.text.find("Recommended Qualifications: ") != -1:
                    position_qualifications = re.sub('(\n|\r)', ' ', cell.parent.next_sibling.next_sibling.findChildren('td')[0].text)
                    
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
                    #address = cell.text[len('Position Address: '):]
                    address = cell.get_text(separator=" ").strip()[len('Position Address:  '):]

                elif cell.text.find('Job Location: ') != -1:
                    address = unicodedata.normalize('NFKD', cell.text[len('Job Location: '):])
                # transportation 
                elif cell.text.find('Transportation to work:') != -1:
                    transportation = cell.text[len('Transportation to work: '):]

                # travel required?
                elif cell.text.find('Travel required for position: ') != -1:
                    travel_req = cell.text[len('Travel required for position: '):]
                    
                # anticipated travel information 
                elif cell.text.find('Anticipated travel information: ') != -1:
                    travel_info = cell.text[len('Anticipated travel information: '):]
                    if len(travel_info) == 0:
                        travel_info = 'NULL'
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
                    try:
                        hazardous = db_translation[cell.text[len('Exposure to hazardous and/or biohazardous materials: '):]]
                    except:
                        hazardous = 0
                # research position
                elif cell.text.find('Research Position: ') != -1:
                    try:
                        research = db_translation[cell.text[len('Research Position: '):]]
                    except:
                        research = 0 
                # 3rd party
                elif cell.text.find('Students are hired by a third-party employer: ') != -1:
                    try:
                        third_party = db_translation[cell.text[len('Students are hired by a third-party employer: '):]]
                    except:
                        third_party = 0
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
                    compensation_status = re.sub('(\n|\r)', '', cell.text[len('Compensation Status: '):])

                elif cell.text.find('Other Compensation: ') != -1:
                    other_compensation = re.sub('(\n|\r)', '', cell.text[len('Other Compensation: '):]).strip()
                    if other_compensation == '- None -' or other_compensation == 'None' or other_compensation == '':
                        other_compensation = 'NULL'
                elif cell.text.find('Other Compensation Details: ') != -1:
                    other_compensation_details = cell.text[len('Other Compensation Details: '):]
                    if other_compensation_details == '- None -' or other_compensation_details == 'None' or other_compensation_details == ' ':
                        other_compensation_details = 'NULL'
        # return dictionary containing data to populate 1 row of each table
        return {'MAJOR': (majors_list), 'EMPLOYER': (employer_id, employer_name, hiring_office_location, company_description), 'JOB': (job_id, employer_id, job_name, job_type, job_length, \
            position_description, hazardous, research, third_party, position_qualifications, lowest_experience, address, transportation, \
                travel_req, travel_info, compensation_status, other_compensation, other_compensation_details, hours, minimum_gpa, citizenship_restriction, screening)}

    def evaluation_data(self):
        tables = self.soup.find_all('table')

        # get job id of evaluation 
        job_id = re.search("\(\d+\)", tables[5].findChildren('td')[-1].text).group()[1:-1]
        # get terms of employment 
        terms_of_employment = tables[5].findChildren('td')[1].text
        # get which coop 
        which_coop_table = tables[8]
        divs = which_coop_table.find_all('div')[5:]
        for count, div in enumerate(divs):
            if div.text == 'X':
                which_coop = count
                break
        
        employment_information_table = tables[9]
        rows = employment_information_table.findChildren('tr')
        db_map = {'No': False, 'Yes': True, '-- Not Reported --': None}
        count = 0 
        for row in rows:
            cells = row.findChildren('td')
            for cell in cells:
                print(f'{count} : {cell.text.strip()}')
                if count == 1:
                    try:
                        department = db_map[cell.text.strip()]
                    except:
                        department = cell.text.strip()
                elif count == 3:
                    try:
                        weekly_schedule = db_map[cell.text.strip()]
                    except:
                        weekly_schedule = cell.text.strip()
                elif count == 5:
                    try:
                        days_per_week = int(cell.text.strip())
                    except:
                        days_per_week = None
                elif count == 7:
                    try:
                        stipend = db_map[cell.text.strip()]
                    except:
                        stipend = cell.text.strip()
                elif count == 9:
                    try:
                        transportation_assistance = db_map[cell.text.strip()]
                    except:
                        transportation_assistance = cell.text.strip()
                elif count == 11:
                    try:
                        meal_assitance = db_map[cell.text.strip()]
                    except:
                        meal_assitance = cell.text.strip()
                elif count == 13:
                    try:
                        housing_assistance = db_map[cell.text.strip()]
                    except:
                        housing_assistance = cell.text.strip()
                elif count == 15:
                    try:
                        relocation_assistance = db_map[cell.text.strip()]
                    except:
                        relocation_assistance = cell.text.strip()
                elif count == 17:
                    try:
                        other = db_map[cell.text.strip()]
                    except:
                        other = cell.text.strip()
                elif count == 21:
                    try:
                        shiftwork_required = db_map[cell.text.strip()]
                    except:
                        shiftwork_required = None
                # MUST CORRECT
                elif count == 23:
                    try:
                        overtime_required = db_map[cell.text.strip()]
                    except:
                        overtime_required = cell.text.strip()
                elif count == 25:
                    try:
                        overtime_hours = db_map[cell.text.strip()[len('If yes, how many hours per week? '):]]
                    except:
                        overtime_hours = int(cell.text.strip()[len('If yes, how many hours per week? '):])
                elif count == 27:
                    try:
                        travel_out_of_town_purpose = db_map[cell.text.strip()]
                    except:
                        travel_out_of_town_purpose = cell.text.strip()
                elif count == 29:
                    try:
                        public_transport_available = db_map[cell.text.strip()]
                    except:
                        public_transport_available = None
                elif count == 31:
                    try:
                        employer_assisted_housing = db_map[cell.text.strip()]
                    except:
                        employer_assisted_housing = None
                elif count == 33:
                    try:
                        wish_to_share_housing_information = db_map[cell.text.strip()]
                    except:
                        wish_to_share_housing_information = cell.text.strip()
                count += 1
    
        job_evaluation_table = tables[12]
        rows = job_evaluation_table.findChildren('tr')
        # rating will be stored as integer 
        # 1: very satisfied; 2: satisfied; 3 dissatisfied; 4 very dissatisfied;
        count = 0 
        for row in rows:
            cells = row.findChildren('td')
            for cell in cells:
                if 7 <= count <= 10 and cell.text == 'X':
                    ability_to_collaborate = count % 6
                elif 13 <= count <= 16 and cell.text == 'X':
                    quantity_and_variety = count % 6
                elif 19 <= count <= 22 and cell.text == 'X':
                    meaningful_professional_relationships = count % 6
                elif 25 <= count <= 28 and cell.text == 'X':
                    access_to_supervisor = count % 6
                elif 31 <= count <= 34 and cell.text == 'X':
                    training_provided = count % 6
                elif 37 <= count <= 40 and cell.text == 'X':
                    overall_job_satisfaction = count % 6 
                elif count == 43:
                    try: 
                        recommend_to_friend = db_map[cell.text.strip()]
                    except:
                        recommend_to_friend = None
                elif count == 45:
                    try:
                        accurate_description = db_map[cell.text.strip()]
                    except:
                        accurate_description = None
                elif count == 47:
                    try:
                        explain_if_not = db_map[cell.text.strip()]
                    except:
                        explain_if_not = cell.text.strip()
                elif count == 49:
                    try:
                        best_feature = db_map[cell.text.strip()]
                    except:
                        best_feature = cell.text.strip()
                elif count == 51:
                    try:
                        challenges_drawbacks = db_map[cell.text.strip()]
                    except:
                        challenges_drawbacks = cell.text.strip()
                elif count == 53:
                    try:
                        describe_on_resume = db_map[cell.text.strip()]
                    except:
                        describe_on_resume = cell.text.strip()                        
                count += 1
        # final table 
        career_competencies_table = tables[15]
        rows = career_competencies_table.findChildren('tr')
        # confusing but it's just an html parser don't worry about it
        db_map = {1 : 4, 2 : 3, 3 : 2, 4 : 1}
        count = 0
        for row in rows:
            cells = row.findChildren('td')
            for cell in cells:
                if 7 <= count <= 10 and cell.text == 'X':
                    written_communication = db_map[count % 6]
                elif 13 <= count <= 16 and cell.text == 'X':
                    verbal_communication = db_map[count % 6]
                elif 19 <= count <= 22 and cell.text == 'X':
                    adjusting_communication_style = db_map[count % 6]
                elif 25 <= count <= 28 and cell.text == 'X':
                    contributing_original_and_relevant = db_map[count % 6]
                elif 31 <= count <= 34 and cell.text == 'X':
                    critical_analysis = db_map[count % 6]
                elif 37 <= count <= 40 and cell.text == 'X':
                    accessing_relevant_information = db_map[count % 6]
                elif 43 <= count <= 46 and cell.text == 'X':
                    making_good_decisions = db_map[count % 6]
                elif 49 <= count <= 52 and cell.text == 'X':
                    upholding_ethical_standards = db_map[count % 6]
                elif 55 <= count <= 58 and cell.text == 'X':
                    appropriate_use_of_tech = db_map[count % 6]
                elif 61 <= count <= 64 and cell.text == 'X':
                    setting_goals = db_map[count % 6]
                elif 67 <= count <= 70 and cell.text == 'X':
                    diverse_backgrounds = db_map[count % 6]
                elif 73 <= count <= 76 and cell.text == 'X':
                    effective_work_habits = db_map[count % 6]
                elif 79 <= count <= 82 and cell.text == 'X':
                    proactively_addressing_issues = db_map[count % 6]
                count += 1
        return (
            job_id, 
            terms_of_employment, 
            which_coop,
            department, 
            weekly_schedule, 
            days_per_week, 
            stipend,
            transportation_assistance,
            meal_assitance,
            housing_assistance,
            relocation_assistance,
            other,
            shiftwork_required,
            overtime_required,
            overtime_hours,
            travel_out_of_town_purpose, 
            public_transport_available,
            employer_assisted_housing,
            wish_to_share_housing_information,
            ability_to_collaborate,
            quantity_and_variety,
            meaningful_professional_relationships,
            access_to_supervisor,
            training_provided,
            overall_job_satisfaction,
            recommend_to_friend,
            accurate_description,
            explain_if_not,
            best_feature,
            challenges_drawbacks,
            describe_on_resume,
            written_communication,
            verbal_communication,
            adjusting_communication_style,
            contributing_original_and_relevant,
            critical_analysis,
            accessing_relevant_information,
            making_good_decisions,
            upholding_ethical_standards,
            appropriate_use_of_tech,
            setting_goals,
            diverse_backgrounds,
            effective_work_habits,
            proactively_addressing_issues
        )

# for testing purposes
if __name__ == '__main__':
    with open('./Data/test2.html', 'r') as f:
        parser = Parser(f)
        parser.evaluation_data()
