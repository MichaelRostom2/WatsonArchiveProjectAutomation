from google.genai import Client
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from os import path, makedirs, environ

def convert_month_to_number(month: str) -> int:
  month_dict = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
  }
  # TODO: this will fail if the month is not exactly as above
  return month_dict[month]

def open_driver() -> webdriver.Firefox:
  options = Options()
  options.add_argument("--headless")

  makedirs(path.expanduser("~/tmp"), exist_ok=True)
  environ['TMPDIR'] = path.expanduser("~/tmp")
  # Change depending on the path to geckodriver
  service = Service(executable_path='/usr/local/bin/geckodriver')
  driver = webdriver.Firefox(service=service, options=options)
  return driver

def open_url(url: str, driver: webdriver.Firefox = open_driver()) -> None:
  driver.get(url)
  WebDriverWait(driver, 10)
  driver.implicitly_wait(2)

def call_gemini(client: Client, prompt: str, context: str) -> str:
  response = client.models.generate_content(
      model="gemini-2.5-flash-lite",
      contents= "Execute the following command: " + prompt +
      "\n" +
      "Given the following context:" + context)

  return response.text