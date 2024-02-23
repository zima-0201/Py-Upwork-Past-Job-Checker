import os
import requests
import dotenv
import tkinter as tk
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta, timezone
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import telegram
from telegram import Bot  # Make sure to import Bot correctly

# Load environment variables
dotenv.load_dotenv()

# Use os.getenv to retrieve environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
UPWORK_USERNAME = os.getenv("UPWORK_USERNAME")
UPWORK_PASSWORD = os.getenv("UPWORK_PASSWORD")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
def login_to_website(driver, username, password, login_url):
    try:
        driver.get(login_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'login_username')))
        username_field = driver.find_element(By.ID, 'login_username')
        submit_button = driver.find_element(By.ID, 'login_password_continue')

        username_field.send_keys(username)
        submit_button.click()
        time.sleep(5)
        
        password_field = driver.find_element(By.ID, 'login_password')
        submit_button_login = driver.find_element(By.ID, 'login_control_continue')
        password_field.send_keys(password)
        submit_button_login.click()
        
        WebDriverWait(driver, 10).until(EC.url_changes(login_url))
        if "login" not in driver.current_url.lower():
            return True
        time.sleep(10)
    except TimeoutException as e:
        print(f"Login timeout: {e}. Retrying...")
        driver.quit()        
    except Exception as e:
        print(f"Login error: {e}")
        driver.quit()
    return False

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = None  # Define driver outside try-except to ensure it's in scope for quit()

    for attempt in range(3):  # Try twice
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            break  # Exit loop if successful
        except Exception as e:
            if driver:  # Check if driver was initialized
                driver.quit()
            time.sleep(5)  # Wait before retrying
            if attempt == 1:  # Last attempt
                print(f"Failed to initialize driver after 2 attempts: {e}")
                return None  # Return None or raise an exception

    return driver

async def send_mail(content):
    bot = telegram.Bot(TELEGRAM_TOKEN)
    async with bot:
        chat_id = (await bot.get_updates())
        await bot.send_message(text=content, chat_id=TELEGRAM_CHAT_ID)

def main():
    
    driver = init_driver()
    login_url = 'https://www.upwork.com/ab/account-security/login'
    username = UPWORK_USERNAME
    password = UPWORK_PASSWORD

    try:
        driver.get(login_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'login_username')))
        username_field = driver.find_element(By.ID, 'login_username')
        submit_button = driver.find_element(By.ID, 'login_password_continue')

        username_field.send_keys(username)
        submit_button.click()
        time.sleep(3)
        
        password_field = driver.find_element(By.ID, 'login_password')
        submit_button_login = driver.find_element(By.ID, 'login_control_continue')
        password_field.send_keys(password)
        submit_button_login.click()
        
        WebDriverWait(driver, 10).until(EC.url_changes(login_url))                    
        time.sleep(3)
    except TimeoutException as e:
        print(f"Login timeout: {e}. Retrying...")
        driver.quit() 
    except Exception as e:
        print(f"Login error: {e}")
        driver.quit()
    
    max_index = 40
    for index in range(max_index, 0, -1):
        if index % 3 == 0:
            driver.quit()
            time.sleep(2)
            driver = init_driver()
            login_url = 'https://www.upwork.com/ab/account-security/login'
            username = UPWORK_USERNAME
            password = UPWORK_PASSWORD

            try:
                driver.get(login_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'login_username')))
                username_field = driver.find_element(By.ID, 'login_username')
                submit_button = driver.find_element(By.ID, 'login_password_continue')

                username_field.send_keys(username)
                submit_button.click()
                time.sleep(5)
                
                password_field = driver.find_element(By.ID, 'login_password')
                submit_button_login = driver.find_element(By.ID, 'login_control_continue')
                password_field.send_keys(password)
                submit_button_login.click()
                
                WebDriverWait(driver, 10).until(EC.url_changes(login_url))                    
                time.sleep(5)
            except TimeoutException as e:
                print(f"Login timeout: {e}. Retrying...")
                driver.quit() 
                continue       
            except Exception as e:
                print(f"Login error: {e}")
                driver.quit()
                continue
            
        page_url = f'https://www.upwork.com/nx/search/jobs?amount=500-999&category2_uid=531770282580668418&hourly_rate=10-&page={index}&payment_verified=1&q=%28scrap,%20OR%20extraction,%20OR%20python,%20OR%20automation,%20OR%20image%29&sort=recency&t=0,1'
        try:
            print(page_url)
            driver.get(page_url)
            time.sleep(5)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'card-list-container')))
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            div_elements = soup.find_all(attrs={"data-ev-label": "search_results_impression"})
            div_elements = div_elements[::-1]
            for div in div_elements:
                project_url = "https://www.upwork.com" + div.find('a', class_='up-n-link').get('href')
                project_title = div.find('a', class_='up-n-link').text.strip()
                project_posted = div.find(attrs={"data-test": "JobTileHeader"}).find('small').find_all('span')[1].text.replace('\n', '').strip()
                jst_timezone = timezone(timedelta(hours=9))
                # Get the current date and time in JST
                current_date_time_jst = datetime.now(jst_timezone)
                # Format the date and time
                posted_time = current_date_time_jst.strftime("%m-%d %H:%M")
                if div.find(attrs={"data-test": "total-spent"}):
                    project_spent = div.find(attrs={"data-test": "total-spent"}).text.replace('\n', '').strip().split(' ')[0]
                else:
                    project_spent = 'No spent'
                project_location = div.find(attrs={"data-test": "location"}).text.replace('\n', '').strip()
                if 'Hourly' in div.find(attrs={"data-test": "JobInfoFeatures"}).text:
                    project_price = div.find(attrs={"data-test": "job-type-label"}).text.replace(':', '').strip()
                else:
                    project_price = div.find(attrs={"data-test": "is-fixed-price"}).find_all('strong')[1].text.replace('\n', '').strip()
                project_details = div.find(attrs={"data-test": "JobInfoFeatures"}).text
                project_description = div.find(attrs={"data-test": "UpCLineClamp JobDescription"}).text.strip()
                if len(project_description) > 2500:
                    project_description = project_description[:2500]
                if div.find(attrs={"data-test": "TokenClamp JobAttrs"}):
                    project_skills = ', '.join(span.text for span in div.find(attrs={"data-test": "TokenClamp JobAttrs"}).find_all(attrs={"data-test": "token"}))
                else:
                    project_skills = "No skills"
                
                try:
                    driver.get(project_url)
                    proposals = 0
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'job-details-content')))
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    for script_element in soup.find_all('script'):
                        if 'clientActivity' in script_element.text:
                            data = script_element.text
                            json_initial_text = data.split('clientActivity:{')[1].split('},weeklyRetainerBudget')[0]
                            proposals = str(json_initial_text.split(',')[1].split(':')[1])
                            break
                        else:
                            proposals = 'c'
                    print(json_initial_text)
                    activity_items = soup.find('ul', class_='client-activity-items list-unstyled').find_all('li')
                    viewed_time = 'Not viewed'  
                    hires = '0' 
                    
                    if soup.find(attrs={'data-qa': 'client-location'}):
                        client_location = soup.find(attrs={'data-qa': 'client-location'}).find('strong').text.strip()
                    else:
                        client_location = 'Unknown'
                        
                    if soup.find(attrs={'data-qa': 'client-job-posting-stats'}):
                        posted_jobs = soup.find(attrs={'data-qa': 'client-job-posting-stats'}).find('strong').text.strip().split(' ')[0]
                        hire_rate = soup.find(attrs={'data-qa': 'client-job-posting-stats'}).find('div').text.strip().split(' ')[0]
                    else:
                        posted_jobs = 'Unknown'
                        hire_rate = 'Unknown'  
                                                                                
                    if soup.find(attrs={'data-qa': 'client-contract-date'}):
                        member_since = soup.find(attrs={'data-qa': 'client-contract-date'}).text.strip().replace('Member since ', '')
                    else:
                        member_since = 'Unknown'
                                                
                    for item in activity_items:
                        chars_to_check = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}

                        if 'Proposals:' in item.text and any(c in proposals.lower() for c in chars_to_check):
                            proposals = str(item.find(class_='value').text.replace('\n', '').strip())
                        if 'Last viewed by client' in item.text:
                            viewed_time = str(item.find(class_='value').text.replace('\n', '').strip())
                        if 'Hires:' in item.text:
                            hires = str(item.find(class_='value').text.replace('\n', '').strip())
                        if 'Interviewing' in item.text:
                            interviews = str(item.find(class_='value').text.replace('\n', '').strip())
                        if 'Invites sent:' in item.text:
                            invites_sent = str(item.find(class_='value').text.replace('\n', '').strip())
                        if 'Unanswered invites:' in item.text:
                            unanswered_invites = str(item.find(class_='value').text.replace('\n', '').strip())
                    mark = '*****************************************************************'
                    if int(interviews) < 1 and int(hires) < 1:
                        mark = '==================================================='
                        line = '-----------------------------------------------------------------------------------------------------'
                        message = mark + '\n' + project_posted + ' from ' + posted_time + '\n' + project_title + '\n' + project_url + "\n\n" + 'Price:  ' + project_price + '\n'+ line + '\n' + '𝑨𝒃𝒐𝒖𝒕 𝒕𝒉𝒆 𝑪𝒍𝒊𝒆𝒏𝒕' + '\n\n' + 'Location:  ' + client_location + '\n' + 'Posted Jobs:  ' + posted_jobs + '\n' + 'Hire Rate:  ' + hire_rate + '\n' + 'Total Spent:  ' + project_spent + '\n' + 'Member Since:  ' + member_since + "\n" + line + '\n' + '𝑱𝒐𝒃 𝑫𝒆𝒔𝒄𝒓𝒊𝒑𝒕𝒊𝒐𝒏' + '\n\n' + project_description + "\n" + line + '\n' + '𝑺𝒌𝒊𝒍𝒍𝒔' + '\n\n' + project_skills + '\n' + line + '\n' + '𝑨𝒄𝒕𝒊𝒗𝒊𝒕𝒚 𝒐𝒏 𝒕𝒉𝒊𝒔 𝒋𝒐𝒃' '\n\n' + 'Proposals:  ' + proposals  + '\n' + 'Last viewed by client:  ' + viewed_time  + '\n' + 'Hires:  ' + hires  + '\n' + 'Interviewing:  ' + interviews  + '\n' + 'Invites sent:  ' + invites_sent  + '\n' + 'Unanswered invites:  ' + unanswered_invites + '\n' + mark
                                                    
                        asyncio.run(send_mail(message))
                        print('\n')
                                            
                except TimeoutException as e:    
                    print(f"Error: {e}")  
                    continue                              
                # except Exception as e:   
                #     print(f"Error: {e}")                                 
                #     continue                              

            time.sleep(2)
        except TimeoutException as e:    
            print(f"Error: {e}")        
            driver.quit()
            time.sleep(5)
            driver = init_driver()
            login_url = 'https://www.upwork.com/ab/account-security/login'
            username = UPWORK_USERNAME
            password = UPWORK_PASSWORD

            try:
                driver.get(login_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'login_username')))
                username_field = driver.find_element(By.ID, 'login_username')
                submit_button = driver.find_element(By.ID, 'login_password_continue')

                username_field.send_keys(username)
                submit_button.click()
                time.sleep(5)
                
                password_field = driver.find_element(By.ID, 'login_password')
                submit_button_login = driver.find_element(By.ID, 'login_control_continue')
                password_field.send_keys(password)
                submit_button_login.click()
                
                WebDriverWait(driver, 10).until(EC.url_changes(login_url))                    
                time.sleep(10)
            except TimeoutException as e:
                print(f"Login timeout: {e}. Retrying...")
                driver.quit()        
            except Exception as e:
                print(f"Login error: {e}")
                driver.quit()
        # except Exception as e:  
        #     print(f"Error: {e}")         
        #     driver.quit()
        #     time.sleep(5)
        #     driver = init_driver()
        #     login_url = 'https://www.upwork.com/ab/account-security/login'
        #     username = UPWORK_USERNAME
        #     password = UPWORK_PASSWORD

        #     try:
        #         driver.get(login_url)
        #         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'login_username')))
        #         username_field = driver.find_element(By.ID, 'login_username')
        #         submit_button = driver.find_element(By.ID, 'login_password_continue')

        #         username_field.send_keys(username)
        #         submit_button.click()
        #         time.sleep(5)
                
        #         password_field = driver.find_element(By.ID, 'login_password')
        #         submit_button_login = driver.find_element(By.ID, 'login_control_continue')
        #         password_field.send_keys(password)
        #         submit_button_login.click()
                
        #         WebDriverWait(driver, 10).until(EC.url_changes(login_url))                    
        #         time.sleep(10)
        #     except TimeoutException as e:
        #         print(f"Login timeout: {e}. Retrying...")
        #         driver.quit()        
        #     except Exception as e:
        #         print(f"Login error: {e}")
        #         driver.quit()
    driver.quit()

if __name__ == "__main__":
    main()