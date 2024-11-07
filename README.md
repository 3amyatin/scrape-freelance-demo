# Scrape freelance.de demo

## SETUP
1. make sure Python 3.11 is installed

2. install Python Virtual Environment and required packages into a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the script
```bash
python app.py
```
* A new Chrome Browser window with freelance.de in it will open.
* Authenticate in www.freelance.de within 20 secs
* The script will save the data into an Excel file.
* The Chrome Browser window will close automatically.
* No need to reauthenticate on next runs