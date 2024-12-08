#muuttujat
from muuttujat import *

#Web scraping
from bs4 import BeautifulSoup as bs
import requests

import json

import uuid

#datetime
from datetime import datetime, timedelta

#mongoDB
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


#############################################################################################################
#WILMA


import requests

def wilma_signin():
    '''Kirjautuu Wilmaan ja palauttaa kirjautumisen sekä sessionin'''

    login_url = WILMA_URL
    login = WILMA_LOGIN
    password = WILMA_PASSWORD
    login_route = LOGIN_ROUTE
    URL = login_url
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'origin': URL,
        'referer': URL + login_route
    }

    session = requests.session()

    initial_response = session.get(URL + login_route, headers=HEADERS)


    soup = bs(initial_response.text, 'html.parser')
    login_form = soup.find('form', {'id': 'loginForm'})
    hidden_fields = login_form.find_all('input', {'type': 'hidden'})

    # Construct the payload
    login_payload = {
        'Login': login,
        'Password': password,
    }
    for field in hidden_fields:
        login_payload[field['name']] = field['value']

    # Perform the login POST request
    login_req = session.post(URL + login_route, headers=HEADERS, data=login_payload)
    
    # Check if login was successful
    print(f"Wilma login status code: {login_req.status_code}")

    # Save the cookies after login
    cookies = login_req.cookies

    return login_req, session



#Oppilaan hakeminen Wilmasta
def wilma_student(login_req, session, wilma_student=WILMA_STUDENT):
    '''Oppilaan hakeminen Wilmasta'''

    soup = bs(login_req.text, 'html.parser')
    # Etsitään linkki, joka sisältää oppilaan nimen
    oppilas_link = soup.find('a', string=wilma_student)
    if oppilas_link:
        # Oppilaan linkki
        oppilas_url = oppilas_link['href']
        return oppilas_url
    else:
        print("There is no such student.")

def wilma_subject(session, oppilas_url):
    '''Siirrytään oppilaan sivulle. Haetaan oppilaan sivulta aineet. Palautetaan tuple listan aineiden url ja aineen.'''

    oppilaansivu=session.get(WILMA_URL + oppilas_url)

    soup=bs(oppilaansivu.text, 'html.parser')
    tables = soup.select('#main-content .table', {"class": "table index-table"})

    links = []
    #links.append(("linkkiurl", "link_text"))
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            link_element = row.select_one('td:nth-of-type(1) a')
            if link_element:
                link_url = link_element.get('href')
                link_text = link_element.get_text(separator=' ', strip=True)
                #Lisätään listaan tuple (link_url, link_text)     
                links.append((link_url, link_text))
                # wilma_homeworks(session, link_url, link_text)
    
    return links

def wilma_homeworks(session, link_url, linktext):
    '''Haetaan kotitehtävät'''
 
    # Siirrytään aineen sivulle
    kotitehtavasivu=session.get(WILMA_URL + link_url)
    if kotitehtavasivu.status_code != 200:
        raise Exception(f"Ei saatu yhteyttä sivustoon: {kotitehtavasivu.status_code}")
    
    soup=bs(kotitehtavasivu.content, 'html.parser')
    
    # Sellainen taulu, jossa on "Kotitehtävät" theadissa
    target_table = None
    for table in soup.find_all("table"):
        if table.find("thead"):
            th_elements = table.find("thead").find_all("th")
            if any("Kotitehtävät" in th.get_text() for th in th_elements):
                target_table = table
                break

    if not target_table or not target_table.find("tbody"):
        #print("Table with 'Kotitehtävät' not found or no tbody.")
        return []
    
    # onko tällä tbody
 
    rows = target_table.find("tbody").find_all("tr")
    homeworks = []

    for row in rows:
        # jokaiselta riviltä haetaan solut
        cells = row.find_all("td")
        if len(cells) >= 2:
            start = cells[0].get_text(strip=True)
            description = cells[1].get_text(strip=True)
            start_obj = datetime.strptime(start, "%d.%m.%Y")
            #Lisättään yksi tunti, jotta olisi klo 01:00
            start_aamu = start_obj + timedelta(hours=1)
            start = start_aamu.isoformat()
            # Luodaan loppuaika, joka on yksi tunti alkamisen jälkeen
            yksitunti = start_aamu + timedelta(hours=2)
            stop = yksitunti.isoformat()

            homeworks.append({
                "description": linktext,
                "subject": description,
                "start": start,
                "stop": stop,
                "start_obj": start_obj
            })
    return homeworks


#############################################################################################################
#MONGODB
            
#yhdistää tietokantaan ja palauttaa kokoelman
def connect_mongodb(collection):
    '''Yhdistää tietokantaan ja palauttaa kokoelman'''
    #mongoDB
    atlas_uri = ATLAS_URI
    client = MongoClient(atlas_uri, server_api=ServerApi('1'))
    db = client["wilma"]
    collection_db = db[collection]

    return collection_db

def add_homework_to_db(subject_text, homework, db):
    days = datetime.now() - timedelta(days=5)
    if homework["start_obj"] > days:
        print("Adding to database")
        if not db.find_one({"subject": subject_text, "description": homework["description"], "start": homework["start"]}):
            db.insert_one({
                "subject": subject_text,
                "description": homework["description"],
                "start": homework["start"],
                "stop": homework["stop"]
            })
            print("Added to MongoDB")
       
def add_unique_item_mongodb(homework, db):
    '''Tallennetaan tietokantaan, jos ei ole jo olemassa'''
    now = datetime.now()
    doc = {
        "summary": homework["subject"],
        "description": homework["description"],
        'start': {
            'dateTime': homework["start"],
            'timeZone': "Europe/Helsinki",
        },
        'end': {
            'dateTime': homework["stop"],
            'timeZone': "Europe/Helsinki",
        },
        'created': now
        }
    
    # Tarkistetaan, onko samanlainen dokumentti jo olemassa
    exists = db.find_one({"summary": doc["summary"], "description": doc["description"]})

    if not exists:
        # Jos samanlaista dokumenttia ei löydy, lisätään se kokoelmaan
        lisatty=db.insert_one(doc).inserted_id
        print(f"Document added {lisatty}")
    else:
        print("Document already exists")

#löytää dokumentit tietokannasta
def find_items_mongodb(collection, query={}):
    '''Etsii dokumentit tietokannasta annetun queryn avulla'''
    documents = collection.find(query)

    return list(documents)

#############################################################################################################
#TODOIST

def add_item_to_project(access_token, command):
    url = "https://api.todoist.com/sync/v9/sync"
   
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    payload = {
        "commands": json.dumps([command])
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        print("Item added successfully!")
        response_data = response.json()
        print("Sync status:", response_data.get("sync_status", {}))
        print("Temp ID mapping:", response_data.get("temp_id_mapping", {}))
    else:
        response.raise_for_status()


def main():

##AJASTETTU!!!!
#$trigger = New-ScheduledTaskTrigger -Daily -At 14:20
    # ############################################################################################################
    # #Haetaan oppilaslista
    wilma_students = WILMA_STUDENTS
    wilma_stundent = wilma_students.split(",")

    #Kirjaudutaan Wilmaan
    login, session = wilma_signin()


    all_homeworks = []

    for student in wilma_stundent:
        print(f"Student: {student}")
        oppilasuri=wilma_student(login, session, student)
        links_list = wilma_subject(session, oppilasuri)
        #Linkkilista ei ole tyhjä
        if links_list:
            for linkuri, linktext in links_list:
               #Haetaan kotitehtävät

                homeworks = wilma_homeworks(session, linkuri, linktext)
                all_homeworks.extend(homeworks)
        else:
            print("No links found")
       
        

    # ############################################################################################
    # #Fetches homework from Wilma and stores it in the database

    kotitehtava_db = connect_mongodb("kotitehtavat")
    for homework in all_homeworks:
        add_unique_item_mongodb(homework, kotitehtava_db)

    #################################################
    #TODOIST
     
    # # Query, jolla haetaan mongodb:stä, muuten palauttaa kaikki
    one_minute_ago = datetime.now() - timedelta(hours=0, minutes=10)
    query = {"created": {"$gte": one_minute_ago}}
    print(f"Searched from {one_minute_ago}")
    homeworks_from_db=find_items_mongodb(connect_mongodb("kotitehtavat"), query)
    access_token = API_KEY_TODOIST  
    for homework in homeworks_from_db:
        due_datetime = homework['start']['dateTime']

        command = {
            "type": "item_add",
            "temp_id": str(uuid.uuid4()),
            "uuid": str(uuid.uuid4()),
            "args": {
                "content": homework['summary'],
                "project_id": PROJECT_ID,
                "section_id": SECTION_ID_E,
                "description": homework['description'],
                "due": {
                    "date": due_datetime
                }
            }
        }
        print(command)
        try:
            add_item_to_project(access_token, command)
        except requests.exceptions.HTTPError as e:
            print(f"Failed to add item: {e}")
    
if __name__ == "__main__":
  main()