from typing import List

from selenium.webdriver.common.by import By

from utils import *

# TODO:
# 1. Error checking
# Specifically:
# - Url is from events @ brown
# - Handle Selenium errors with not finding elements
# - Handle Gemini errors
# 2. Figure out how to input this data back to Google Sheets

# Setup Gemini
load_dotenv(override=True)
api_key = getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=api_key)

def extract_event_details(url: str):
  driver = open_url(url)

  # Collect event details
  event_details = {}

  # Title is retrieved from the tab name
  event_details["title"] = driver.title.split('|')[0].strip()


  # Date is captured from the web page then converted to the required format
  numeric_date_list: List[str] = driver.find_element(By.ID, "lw_cal_this_day").text.split(" ")
  month_numeric: int = convert_month_to_number(numeric_date_list[0])
  day_numeric: str = numeric_date_list[1][:-1]
  year_numeric: str = numeric_date_list[2]
  event_details["date"] = str(month_numeric) + "/" + day_numeric + "/" + year_numeric

  # Semester is calculated from the month
  # TODO: double check month cutoff for semesters
  if 8 <= month_numeric <= 12:
    event_details["semester"] = "Fall"
  elif 1 <= month_numeric <= 5:
    event_details["semester"] = "Spring"
  elif 6 <= month_numeric <= 7:
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
                                          event_details["description"]).text

  # Topics are extracted by gemini from the description
  event_details["topics"] = call_gemini(gemini_client,
                                          "Extract key themes from the event description" 
                                          "Only return the one to three word themes separated by commas",
                                          event_details["description"]).text

  # Region is extracted by gemini from the description
  event_details["region"] = call_gemini(gemini_client,
                                        "Extract the region of the event"
                                        "Only return the region name"
                                        "Only pick from the following:"
                                        "Africa, Brazil, China, Europe, India & South Asia,"
                                        "Latin America & Caribbean, Middle East, Russia, United States",
                                        event_details["description"]).text

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
                                                event_details["description"]).text

  # The right column is retrieved from the web page
  # This includes data for location, room, sponsor, and description
  # right_col: List[str] = driver.find_element(By.ID,
  #                                            "lw_cal_event_detail_cols_right").text


  # for line in right_col.split('\n'):
  #   if "Sponsor" in line:
  #     event_details["sponsor"] = line.split(':')[1]
  #   if "Location" in line:
  #     event_details["location"] = line.split(':')[1]
  #   if "Room" in line:
  #     event_details["room"] = line.split(':')[1]
  #
  # event_details["url"] = url
  # # event_details["Link"] = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[1]/section/div[2]/div[2]/div/div/div/div[1]/a").get_attribute("href")

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