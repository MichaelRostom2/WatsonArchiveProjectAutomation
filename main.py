from typing import List

from selenium.webdriver.common.by import By
from os import getenv
from dotenv import load_dotenv
from google import genai
from utils import *

# TODO:
# 1. Error checking
# Specifically:
# - Url is from events @ brown
# - Handle Selenium errors with not finding elements
# - Handle Gemini errors
# - Handle if given month other than dictonary
# 2. Figure out how to input this data back to Google Sheets

# Setup Gemini
load_dotenv(override=True)
api_key = getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=api_key)


def extract_event_details(url: str) -> dict:
  print("Opening URL...")
  open_url(url, driver)

  # Collect event details
  print("Extracting event details...")
  event_details = {}

  # Title is retrieved from the tab name
  event_details["title"] = driver.title.split('|')[0].strip()

  # Date is captured from the web page then converted to the required format
  numeric_date_list: List[str] = driver.find_element(By.ID,
                                                     "lw_cal_this_day").text.split(
    " ")
  month_numeric: int = convert_month_to_number(numeric_date_list[0])
  day_numeric: str = numeric_date_list[1][:-1]
  year_numeric: str = numeric_date_list[2]
  event_details["date"] = str(
    month_numeric) + "/" + day_numeric + "/" + year_numeric

  # Semester is calculated from the month
  if 8 <= month_numeric <= 12 or month_numeric == 1:
    event_details["semester"] = "Fall"
  elif 2 <= month_numeric <= 5:
    event_details["semester"] = "Spring"
  elif 6 <= month_numeric <= 8:
    event_details["semester"] = "Summer"
  else:
    raise ValueError("Invalid month")

  # Year is inputted directly
  event_details["year"] = year_numeric

  # Description is extracted from the web page
  event_details["description"] = driver.find_element(By.CLASS_NAME,
                                                     "lw_calendar_event_description").text

  # Keywords are extracted by gemini from description
  event_details["keywords"] = call_gemini(gemini_client,
                                          "Extract keywords from the event description"
                                          "Only return the keywords separated by commas",
                                          event_details["description"])

  # Topics are extracted by gemini from the description
  event_details["topics"] = call_gemini(gemini_client,
                                        "Extract key themes from the event description"
                                        "Only return the one to three word themes separated by commas",
                                        event_details["description"])

  # Region is extracted by gemini from the description
  event_details["region"] = call_gemini(gemini_client,
                                        "Extract the region of the event"
                                        "Only return the region name"
                                        "Only pick from the following:"
                                        "Africa, Brazil, China, Europe, India & South Asia,"
                                        "Latin America & Caribbean, Middle East, Russia, United States",
                                        event_details["description"])

  # Country is extracted by gemini from the description
  event_details["country"] = call_gemini(gemini_client,
                                        "Extract the country of the event"
                                        "Only return the country name",
                                        event_details["description"])

  # Event series is chosen from standardized list
  # TODO: get the list and implement this

  # Center / Initiative / Program is chosen from standardized list
  # TODO: get the list and implement this

  # Research Theme is chosen by gemini from the description
  event_details["research_theme"] = call_gemini(gemini_client,
                                                "Choose from: Security, Development, Governance (definitions provided below)"
                                                "Only Return the chosen theme name"
                                                "Research Theme Definitions"
                                                "Security: Covers traditional and emerging global security concerns, including climate change, pandemics, cyber threats, and post-conflict reconstruction."
                                                "Development: Focuses on inequality, governance, urban transformation, democracy, and global economic systems."
                                                "Governance: Explores how globalization affects political and economic institutions and the need for new forms of global governance.",
                                                event_details["description"])

  # The right column is retrieved from the web page
  # This column includes data for location, room, sponsor
  right_col: List[str] = driver.find_element(By.ID,
                                             "lw_cal_event_detail_cols_right").text.split(
    '\n')

  for line in right_col:
    if "Location" in line:
      event_details["Building"] = line.split(':')[1]
    elif "Room" in line:
      event_details["Location"] = line.split(':')[1]
    elif "Sponsor" in line:
      # Sponsor is the same as center
      event_details["Sponsor"] = line.split(':')[1]


  # Student Run
  # NOTE: 90% of the time is no, but leave it empty for now
  event_details["student_run"] = ""

  # Privacy
  # TODO: This is dependent on whether the Youtube link is available


  # Link is inputted directly
  event_details["link"] = url

  # Watson Faculty
  # TODO: This is the description of the yt video

  # Youtube Link is extracted by gemini from the description
  # TODO: handle case when there is no youtube link
  # TODO: handle the privacy attribute from the result of the yt link
  # Right now it can't find it if the order of html elements changes
  # and fails if not found
  # event_details["yt_link"] = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[1]/section/div[2]/div[2]/div/div/div/div[1]/a").get_attribute("href")

  # Talent is extracted by gemini from the description
  talent_list: List[str] = call_gemini(gemini_client,
                                       "Extract the talent of the event"
                                       "Only names of people attending or speaking at the event"
                                       "return separated by commas",
                                       event_details["description"]).split(",")

  for i in range(len(talent_list)):
    if i > 3:
      # Can only enter 4 talents in the spreadsheet
      print("Too many talents, only entering the first 4")
      break
    event_details["talent" + str(i + 1)] = talent_list[i]

  driver.quit()
  return event_details


if __name__ == "__main__":
  driver = open_driver()
  events_details = extract_event_details(
    input("Enter the URL of the event from events@brown: "))
  # Example urls for testing
  # "https://events.brown.edu/event/303266-syria-after-assad-a-teach-in"
  # "https://events.brown.edu/event/immigrationjournalism"
  # "https://events.brown.edu/event/321735-understanding-the-government-shutdown-causes-and"

  for key, value in events_details.items():
    print(f"{key.capitalize()}: {value}")
