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

    def relevantData(self):

        paragraphs = self.soup.find_all('p')
        for paragraph in paragraphs:
            if paragraph.span != None:
                if paragraph.span.text == 'Employer: ':
                    employer = paragraph.text
                    #print(employer)

        spans = self.soup.find_all('span')
        for span in spans:
            if span.text == "Job's Type: ":
                job_type = span.next_sibling.next_sibling.text
                # print(job_type)
            if span.text == "Job's Length: ":
                job_length = span.next_sibling.next_sibling.text
                # print(job_length)

        main_table = self.soup.find('table', class_="borderland")
        rows = main_table.findChildren('tr')

        for row in rows:
            cells = row.findChildren('td')
            for cell in cells:

                if cell.text == "Division/Location/Company Description:":
                    company_description = cell.parent.next_sibling.next_sibling.findChildren('td')[0].text

                elif cell.text == "Position Description:":
                    position_description = cell.parent.next_sibling.next_sibling.findChildren('td')[0].text

                elif cell.text == "Recommended Qualifications: ":
                    position_qualifications = cell.parent.next_sibling.next_sibling.findChildren('td')[0].text

                elif cell.text.find('Majors') != -1:
                    majors_list = [major.text for major in cell.find_all('span')[1:]]

                # get experience level 
                elif cell.text.find('Level(s)') != -1:
                    levels = ['Beginner', 'Intermediate', 'Advanced']
                    # only records lowest experience level  
                    for level in levels:
                        if cell.text.find(level) != -1: 
                            lowest_experience = level
                            break
                    
                elif cell.text.find('Position Address:') != -1:
                    address = cell.text[len('Position Address:')+1:]


                elif cell.text.find('Transportation to work:') != -1:
                    transportation = cell.text[len('Transportation to work:')+1:]

                elif cell.text.find('Approximate Hours Per Week:') != -1:
                    hours = float(cell.text[len('Approximate Hours Per Week:')+1:])

                elif cell.text.find('Minimum GPA: ') != -1: 
                    minimum_gpa = float(cell.text[len('Minimum GPA: ')+1:])
                    print(minimum_gpa)

if __name__ == '__main__':
    with open('./Data/test2.html', 'r') as f:
        parser = Parser(f)
        data = parser.relevantData()
