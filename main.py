import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import datetime as dt
import configparser

cfg = configparser.ConfigParser()
cfg.read('val.cfg')
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("cred.json", scope)
client = gspread.authorize(creds)
SHEET_ID = cfg["Sheet"]["SHEET_ID"]

sheet = client.open_by_key(SHEET_ID).worksheet("Sheet1")


def search_player(name):
    players = sheet.col_values(1)  # Assuming player names are in the first column
    if name in players:
        return True
    else:
        return False


# Function to fetch player info from SportsDB
def get_player_info(name):
    new_name = name.title().replace(" ", "_")
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p={new_name}"
    response = requests.get(url)
    data = response.json()
    if data['player']:
        return data['player'][0]  # Assuming first player in the list is the desired player
    else:
        return None


# Function to append player info to Google Sheet
def append_player_info(info):
    values = [info['strPlayer'], info['strSport'], info['strNationality'], info['strGender'],
              info.get('dateBorn', 'Unknown')]
    sheet.append_row(values)


# Streamlit app
st.title('Player Information Search')

player_name = st.text_input('Enter player name:').title()
print(player_name)


def find():
    player_info = None
    if search_player(player_name):
        st.success(f'Player "{player_name}" found in the database!')
        player_info = get_player_info(player_name)
    else:
        st.error(f'Player "{player_name}" not in the database. Searching in API...')
        player_info = get_player_info(player_name)

    if player_info:
        st.write('### Player Information:')
        st.write(f'Name: {player_info["strPlayer"]}')
        st.write(f'Sport: {player_info["strSport"]}')
        st.write(f'Nationality: {player_info["strNationality"]}')
        st.write(f'Gender: {player_info["strGender"]}')
        birth_year = player_info.get("dateBorn", "Unknown").split("-")[0]
        curr = dt.datetime.now().strftime("%Y")
        age = int(curr) - int(birth_year)
        st.write(f'Age: {age}')  # Date of birth may not be available
        st.write(f'About: {player_info["strDescriptionEN"]}')
        # Add more information as needed

        if not search_player(player_name):  # Append to sheet only if player not found before
            append_player_info(player_info)
            st.write(f'Player "{player_name}" appended to the database.')
    else:
        st.error('Player information not found on SportsDB.')


st.button('Search', on_click=find)
if len(player_name) != 0:
    find()
