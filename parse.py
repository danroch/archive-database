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
        url = f"https://banner.drexel.edu/{self.soup.find('td', class_='ddlabel').a['href']}"
        self.__evaluationURLs.append(url)

    def getEvaluations(self):
        return self.__evaluationURLs

    def populateDatabase(self):
        pass

if __name__ == '__main__':
    with open('./Data/test.html', 'r') as f:
        parser = Parser(f)
        links = parser.getEvalURL()
        print(links)
