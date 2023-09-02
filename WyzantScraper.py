import os
import pickle
import time
import undetected_chromedriver as uc
import json
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""from selenium.webdriver.chrome.options import Options#to stop auto close
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
"""
"""

driver = webdriver.Chrome(options=options)
"""
def main():
    def read_info(filename = 'wyzant_info.json'):
        f = open(filename)
        j = json.load(f)
        f.close()
        return j

    INFO = read_info()
    USERNAME = INFO["USERNAME"]
    PASSWORD = INFO["PASSWORD"]
    WYZANT_HANDLE = INFO["WYZANT_HANDLE"]
    WANT_TO_APPLY_LIST = INFO["WANT_TO_APPLY_LIST"]
    RECENCY = INFO ["RECENCY"]

    def check_login_page(driver):
        try:
            login_form = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sso-login-form"))
            )
            username_form = login_form.find_element(By.ID,"Username")
            username_form.send_keys(USERNAME)
            password_form = driver.find_element(By.XPATH, '//div[@id="sso_login-landing"]/div/div/div/form/div[2]/input')
            password_form.send_keys(PASSWORD)
            login_button = login_form.find_element(By.XPATH, '//div[@id="sso_login-landing"]/div/div/div/form/button')
            login_button.click()
            #time.sleep(10)#wait for log in #better to wait for selector than to sleep
            # #wyzant is notoriously slow, better to wait for selector
            name_check = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//header/div/div/div/div/div/span"))
            )
            #print(name_check.text)
            cookies = driver.get_cookies()
            #print(cookies)
            pickle.dump(cookies, open("cookies.pkl","wb"))
            crawl_job_board(driver)
        except NoSuchElementException:
            print("already logged in")
            return

    def crawl_job_board(driver):
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            #if a domain mismatch happens, i need to disregard some of the cookies
            #uncomment
            #cookie['domain'] = '.wyzant.com'
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass
        login = driver.find_element(By.XPATH,r'//header/div/div/div/a[@href="/login"]').click()
        #driver.get('https://www.wyzant.com/tutor/jobs')
        apply_to_job_loop(driver)


    def check_recency(job_recency):
        job_recency = job_recency.strip()
        if 'd' == job_recency.lower()[-1]:
            t = int(job_recency[:-1])
            if t <= RECENCY:
                return True
            else:
                return False
        else:
            if 'm' == job_recency.lower()[-1] or 'h' == job_recency.lower()[-1]:
                return True
            return False

    def apply_to_job_loop(driver):
        page = 'https://www.wyzant.com/tutor/jobs?action=index&controller=tutor_facing%2Fjobs&page='
        page_range = 4
        try:
            for page_num in range(1,page_range):
                driver.get(page + str(page_num))
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="jobs-list"]/div'))
                )
                jobs = driver.find_elements(By.XPATH, '//div[@id="jobs-list"]/div')
                print("len jobs:",len(jobs))
                job_recencies = driver.find_elements(By.XPATH, '//div[@id="jobs-list"]/div/div/div/div/span[@class="text-semibold text-light"]')
                print("len job recencies:", len(job_recencies))
                #tst= job_recencies[1].text
                #print(tst)
                for i in range(len(jobs)):
                    job = jobs[i]
                    job_a_tag = job.find_element(By.XPATH, './div/div/h3/a')
                    job_subject = job_a_tag.text
                    print(job_subject)
                    #continue
                    job_recency = job_recencies[i].text
                    if job_subject in WANT_TO_APPLY_LIST and check_recency(job_recency):
                        print("entering")
                        job_a_tag.click()
                        apply_to_job(driver,job_subject)
                        apply_to_job_loop(driver)
            time.sleep(45)#sleep 45 seconds before starting over, could collect use data for peak hours of the day
        except:#A job from the list above has already been applied too, so this is the cause of the exception
            pass
        return apply_to_job_loop(driver)

    def apply_to_job(driver,job_subject):

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//select/option'))
        )
        options = driver.find_elements(By.XPATH, f'//select/option')#[@text="{job_subject}"]')
        for option in options:
            if option.text==job_subject:#use .text or .accessible_name
                message = option.get_attribute('value')
                option.click()
                break

        #print(message)
        money_box = None
        try:
            money_box = driver.find_element(By.ID, 'hourly_rate')
        except:#no money box, either already met with student and rate can't be changed, or
            try:#partnership program, must check box to agree to fixed rate
                check_box = driver.find_element(By.XPATH, '//form[@id="job_application_form"]/div/div/input[@type="checkbox"]').click()
            except:#submit button is different for checkbox case
                submit_button = driver.find_element(By.XPATH, '//div/div/form/input[@type="submit"]').click()
            submit_button = driver.find_element(By.XPATH, '//div/div/form/input[@type="submit"]').click()
            return
        reccomended_rate = driver.find_elements(By.XPATH, '//div/div/div/span/div/div/span')
        reccomended_rate = reccomended_rate[2].text#index subject to change with wyzant's UI
        rec_rate_number = ""
        print(reccomended_rate)
        for i in reccomended_rate:
            #print(i)
            if i.isdigit():
                rec_rate_number+=i

        if rec_rate_number == "":
            rec_rate_number = 55
        else:
            rec_rate_number = max(50,int(rec_rate_number)-5)

        money_box.clear()
        money_box.send_keys(str(rec_rate_number))
        submit_button = driver.find_element(By.XPATH, '//div/div/form/input[@type="submit"]').click()


        #input(str(rec_rate_number))
        pass


    #options = webdriver.ChromeOptions()
    #options.add_experimental_option('debuggerAddress', localhost:8888)
    os.environ['PATH'] += r"C:\Program Files\chromedriver-win64\chromedriver.exe"
    PATH = ""
    #driver = webdriver.Chrome()#options=options)
    driver = uc.Chrome()#better than ^
    #driver.get("http://127.0.0.1/wyzant_job_example.html")#test job apply
    #apply_to_job(driver, "Computer Programming")# apply test
    try:

        driver.get("https://wyzant.com/tutor/jobs") # program entry point

        #driver.get("http://127.0.0.1/wyzant_sign_in.html")#test login page
        #driver.get("http://127.0.0.1/wyzant_job_page.htm")#test scrape job board

        print('connected here')
        try:
            crawl_job_board(driver)
        except NoSuchElementException:
            check_login_page(driver)# checking login





        #input("press enter to close")
    except Exception as e:
        print(e,"main error")
        #input("press any key to close")
    #main()#catching errors in Selenium is very hard, as they are not always repeatable
    #the bright side of that is that restarting main usually does the trick
    #pretty sure I caught it: see "A job from the list"... above

if __name__ == '__main__':
    main()

"""
<img role="button" src="/static/media/close-icon.ba9ccf9b.svg" alt="Banner Close Icon" class="FullPageModal__StyledCloseIcon-sc-1tziext-0 eJtQsN">
"""