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

        spans = self.soup.find_all('span')
        for span in spans:
            if span.text == "Job's Type: ":
                job_type = span.next_sibling.next_sibling.text
            if span.text == "Job's Length: ":
                job_length = span.next_sibling.next_sibling.text

        main_table = self.soup.find('table', class_="borderland")
        rows = main_table.findChildren('tr')
        for row in rows:
            cells = row.findChildren('td')
            for cell in cells:
                print(cell.text)
                
if __name__ == '__main__':
    with open('./Data/test2.html', 'r') as f:
        parser = Parser(f)
        data = parser.relevantData()
