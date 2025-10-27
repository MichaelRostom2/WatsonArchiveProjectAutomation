from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# TODO:
# 1. Error checking, make sure that the program doesn't stop if it doesn't find the element
# 2. Figure out how to input this data back to Google Sheets
# 3. Setup call to LLM for some data:
#     - Keywords
#     - Topic
#     - Research
#     - Country
#     - Region

#     - Professor
#     - Talent 1 & 2 & 3

def extract_event_details(url: str):
  event_details = {}

  options = Options()
  options.add_argument("--headless")
  # Change to where your geckodriver is installed
  service = Service(executable_path='/usr/local/bin/geckodriver')
  driver = webdriver.Firefox(service=service, options=options)

  driver.get(url)
  WebDriverWait(driver, 10)
  driver.implicitly_wait(2)

  # Collect event details
  event_details["date"] = driver.find_element(By.ID, "lw_cal_this_day").text
  right_col = driver.find_element(By.ID,
                                  "lw_cal_event_detail_cols_right").text.split(
      '\n')
  event_details["title"] = driver.title.split('|')[0].strip()
  for str in right_col:
    if "Sponsor" in str:
      event_details["sponsor"] = str.split(':')[1]
    if "Location" in str:
      event_details["location"] = str.split(':')[1]
    if "Room" in str:
      event_details["room"] = str.split(':')[1]
  event_details["description"] = driver.find_element(By.CLASS_NAME,
                                                     "lw_calendar_event_description").text
  event_details["url"] = url
  event_details["Link"] = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[1]/section/div[2]/div[2]/div/div/div/div[1]/a").get_attribute("href")

  driver.quit()
  print("Event Details:")
  for key, value in event_details.items():
    print(f"{key.capitalize()}: {value}")



# Example usage
url = "https://events.brown.edu/event/303266-syria-after-assad-a-teach-in"
# url = input("Enter the URL of the event: ")
# url = "https://events.brown.edu/event/immigrationjournalism"

print("Extracting event details...")
extract_event_details(url)