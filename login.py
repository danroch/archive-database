import time, random, os, json, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


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
    print('GETTING COOKIES')
    all_cookies = driver.get_cookies()
    cookies_dict = {}
    for cookie in all_cookies:
        cookies_dict[cookie['name']] = cookie['value']

    with open(os.getcwd() + '/Data/cookies.json', 'w') as f:
        json.dump(cookies_dict, f, indent=4)
    return

if __name__ == '__main__':
    getCookies()
    # populate request data
    with open(os.getcwd() + '/Data/cookies.json', 'r') as f:
        cookies = json.load(f)
    with open(os.getcwd() + '/Data/headers.json', 'r') as f:
        headers = json.load(f)
    print(cookies)
    target_url = 'https://banner.drexel.edu/duprod/hwczkfsea.P_StudentESaPArchiveSearchVal'
    data = [
    ('i_user_type', 'S'),
    ('i_a_majors', '-'),
    ('i_a_gaols', '-'),
    ('i_empl_search', ''),
    ('i_a_majors', 'CI-CS'),
    ('i_jt_search', ''),
    ('i_wa_search', '0'),
    ('i_a_gaols', '-'),
    ]
    
    with requests.session() as s:
        response = s.post(
            'https://banner.drexel.edu/duprod/hwczkfsea.P_StudentESaPArchiveSearchVal', 
            cookies=cookies,
            headers=headers,
            data=data, 
        )
        print(response.text)
    
    
