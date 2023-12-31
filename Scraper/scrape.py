import time, random, os, json, requests, writer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from parse import Parser 


# log in using selenium driver to extract cookies which will be used in the remaining requests 
def getCookies():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    driver.get("http://connect.drexel.edu")
    time.sleep(random.randint(0,1))
    username = input('Enter your username: ')
    password = input('Enter your password: ')
    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    time.sleep(random.randint(0,1))
    driver.find_element(By.NAME, '_eventId_proceed').click()
    # input 2FA code 
    while True:
        sms_code = input('Enter 2 factor authentication code: ')
        if len(sms_code) == 6:
            break
    driver.find_element(By.ID, 'j_mfaToken').send_keys(sms_code)
    # click continue
    driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div[1]/div[1]/form[2]/div[2]/button[1]').click()
    time.sleep(5)
    # click drexel one 
    driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[1]/div[1]/a').click()
    time.sleep(5)
    # click coop services
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/nav/div/ul/li[4]/a').click()
    time.sleep(5)
    # click esp archive
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div/div[2]/div/div/section/div/div/div/div[2]/div[1]/div/div/div[3]/div[3]/div[2]/div/div[1]/span/a').click()
    time.sleep(10)
    # handle driver window to make sure right tab is being handled when obtaining cookies
    original_window = driver.current_window_handle
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break
    time.sleep(10)
    print('Getting cookies...')
    all_cookies = driver.get_cookies()
    cookies_dict = {}
    for cookie in all_cookies:
        cookies_dict[cookie['name']] = cookie['value']

    with open(os.getcwd() + '/Data/cookies.json', 'w') as f:
        json.dump(cookies_dict, f, indent=4)
    print('Complete')
    return

if __name__ == '__main__':
    getCookies()
    # populate request data
    with open(os.getcwd() + '/Data/cookies.json', 'r') as f:
        cookies = json.load(f)
    with open(os.getcwd() + '/Data/headers.json', 'r') as f:
        headers = json.load(f)
    target_url = 'https://banner.drexel.edu/duprod/hwczkfsea.P_StudentESaPArchiveSearchVal'
    cci_payload = [
    ('i_user_type', 'S'),
    ('i_a_majors', '-'),
    ('i_a_gaols', '-'),
    ('i_empl_search', ''),
    ('i_a_majors', 'B-TIMS'),
    ('i_a_majors', 'CI-CI00'),
    ('i_a_majors', 'CI-CS'),
    ('i_a_majors', 'CI-CST'),
    ('i_a_majors', 'CI-DSCI'),
    ('i_a_majors', 'CI-IMAT'),
    ('i_a_majors', 'CI-ISYS'),
    ('i_a_majors', 'CI-IT'),
    ('i_a_majors', 'CI-SE'),
    ('i_jt_search', ''),
    ('i_wa_search', '0'),
    ('i_a_gaols', '-'),
    ]
    
    with requests.session() as sess:
        response = sess.post(
            'https://banner.drexel.edu/duprod/hwczkfsea.P_StudentESaPArchiveSearchVal', 
            cookies=cookies,
            headers=headers,
            data=cci_payload, 
        )

        # get initial page of job listings and instantiate parser object with that page
        parser = Parser(response.text)

        # determines how many job listings there are 
        total_recs = parser.howManyJobs()

        # display ALL listings on one page for easier scraping
        params = {
        'i_user_type': 'S',
        'i_total_recs': total_recs,
        'i_recs_per_page': total_recs,
        'i_curr_page': '1',
        }
        response2 = sess.get('https://banner.drexel.edu/duprod/hwczkfsea.P_StudentESaPArchiveList', params=params, verify=False)
        
        # get jobIDs 
        parser.setDoc(response2.text)
        jobIDs = parser.populateJobs()
        

        # get job page (shows list of links to job overviews) 
        for id in jobIDs[400:450]:
            time.sleep(1)
            params = {
            'i_user_type': 'S', 
            'i_job_num': id,
                }
            response3 = sess.get('https://banner.drexel.edu/duprod/hwczkfsea.P_StudentESaPArchiveJobDisplay', params=params)

            with open('./Data/test.html', 'w') as f:
                f.write(response3.text)

            parser.setDoc(response3.text)
            parser.extract_URLs()
            print(f'Job ID: {id}')

        # obtain overview and evaluation URLs 
        overviewURLs = parser.getOverviews()
        evaluationURLs = parser.getEvaluations()
        
        # write to csv file pertaining to job and employer overview tables 
        writer.overview_writer(sess=sess, overviewURLs=overviewURLs, parser=parser)
        
        # write to csv file pertaining to evaluation table 
        writer.evaluation_writer(sess=sess, evaluationURLs=evaluationURLs, parser=parser)