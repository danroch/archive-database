from bs4 import BeautifulSoup
import re 

class Parser:
    
    def __init__(self, html_doc):
        self.soup = BeautifulSoup(html_doc, 'html.parser')
        self.__jobIDS = []

    # returns value to send another request for all jobs to be displayed on one page 
    def howManyJobs(self):
        return self.soup.find('div', class_='centeraligntext').get_text().split()[5]

    def populateJobs(self):
        # find all job records (data cells with class as dddefault)
        records = self.soup.find_all('td', class_='dddefault')
        for record in records:
            # searches using regular expression to find numbers enclosed within parentheses 
            self.__jobIDS.append(re.search("\([^)]*\d[^)]*\)", str(record)).group()[1:-1])
        return self.__jobIDS

if __name__ == '__main__':
    with open('Data/test.html', 'r') as html_test_doc:
        parser = Parser(html_test_doc)
        print(parser.populateJobs())
    