import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

### SETUP ###
# 1. make sure Python 3.11 is installed

# 2. install Python Virtual Environment and required packages into a virtual environment
# $ python -m venv .venv
# $ source .venv/bin/activate
# $ pip install -r requirements.txt

# 6. Run the script
# $ python app.py
# * A new Chrome Browser window with freelance.de in it will open.
# * Login into www.freelance.de there within 20 secs
# * The script will save the data into an Excel file.
# * The Chrome Browser window will close automatically.
# * No need to reauthenticate on next runs

### CONFIGURATION ###
mainurl = "https://www.freelance.de/projekte/IT-Entwicklung-Projekte/"
mainregex = r"https://www\.freelance\.de/Projekte/Projekt-\d+-[\w-]+"
excel_filename = "Projekte freelance.de.xlsx"
seconds_to_sleep = 20

chrome_options = Options()
chrome_options.add_argument("user-data-dir=selenium") 
driver = webdriver.Chrome(options=chrome_options)
driver.get(mainurl)
time.sleep(seconds_to_sleep)
cookies = driver.get_cookies()
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])
driver.quit()

response = session.get(mainurl)
assert response.status_code == 200, f"Failed to retrieve the page. Status code: {response.status_code}"
soup = BeautifulSoup(response.text, 'html.parser')

urls = []
pattern = re.compile(mainregex)
for tag_a in soup.find_all('a', href=True):
    href = tag_a['href']
    if pattern.match(href):
        urls.append(href)
unique_urls = list(set(urls))

print(f"💼 Projects found: {len(unique_urls)}")

table = []

for url in unique_urls:
    response = session.get(url)

    assert response.status_code == 200, f"Failed to retrieve the page. Status code: {response.status_code}"
    print(f"🔗 {str(unique_urls.index(url) + 1).zfill(len(str(len(unique_urls))))}/{len(unique_urls)}: {url}")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    position = soup.find('h1').get_text(strip=True)
    company_name = soup.find('p', class_='company-name').get_text(strip=True)

    start_date          = tag.find_parent('li').get_text(strip=True) if (tag:=soup.find('i', {'data-original-title': 'Geplanter Start'})) else ""
    end_date            = tag.find_parent('li').get_text(strip=True) if (tag:=soup.find('i', {'data-original-title': 'Voraussichtliches Ende'})) else ""
    project_location    = tag.find_parent('li').get_text(strip=True) if (tag:=soup.find('i', {'data-original-title': 'Projektort'})) else ""
    hourly_rate         = tag.find_parent('li').get_text(strip=True) if (tag:=soup.find('i', {'data-original-title': 'Stundensatz'})) else ""
    remote_possible     = tag.find_parent('li').get_text(strip=True) if (tag:=soup.find('i', {'data-original-title': 'Remote-Einsatz möglich'})) else ""
    last_update         = tag.find_parent('li').get_text(strip=True) if (tag:=soup.find('i', {'data-original-title': 'Letztes Update'})) else ""
    reference_number    = tag.find_parent('li').get_text(strip=True) if (tag:=soup.find('i', {'data-original-title': 'Referenz-Nummer'})) else ""

    project_description = tag.find_next('div').get_text(separator='\n', strip=True) if (tag:=soup.find('h2', string=re.compile(r'^Projektbeschreibung'))) else ""
    contact_details     = tag.find_next('div').get_text(separator='\n', strip=True) if (tag:=soup.find('h3', string="Kontaktdaten")) else ""

    row = {
        'Position': position,
        'Company Name': company_name,
        'Start Date': start_date,
        'End Date': end_date,
        'Project Location': project_location,
        'Hourly Rate': hourly_rate,
        'Remote Possible': remote_possible,
        'Last Update': last_update,
        'Reference Number': reference_number,
        'Project Description': project_description,
        'Contact Details': contact_details,
        'URL': url
    }

    table.append(row)

df = pd.DataFrame(table)
df.drop(columns=['URL'], inplace=True)

#df.to_excel(excel_filename, index=False)
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Projects')
    workbook = writer.book
    worksheet = writer.sheets['Projects']
    
    for row_num, row in enumerate(table, start=2):
        worksheet.write_url(f'A{row_num}', row['URL'], string=row['Position'])

print(f"📁 Excel file saved as {excel_filename}")

