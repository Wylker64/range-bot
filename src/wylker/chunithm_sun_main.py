import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# URL of the website
url = 'https://gamerch.com/chunithm/entry/491431'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def get_songs_info(url, start_line, level_header):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the webpage, Status Code:", response.status_code)
        return

    lines = response.content.decode().splitlines()
    html_content = '\n'.join(lines[start_line:])  # Start from specified line

    soup = BeautifulSoup(html_content, 'html.parser')

    song_table = soup.find('table')
    if not song_table:
        print(f"Failed to find the song table in the HTML content starting from line {start_line}.")
        return

    songs = []
    current_level = ''
    current_difficulty = ''
    current_genre = ''
    for row in song_table.find_all('tr'):
        cells = row.find_all('td')
        th_cells = row.find_all('th')

        # Handle level row
        if th_cells and level_header in th_cells[0].text:
            current_level = th_cells[0].text.strip()

        # Handle difficulty and genre row
        elif cells and 'background-color' in str(cells[0]):
            if len(cells) == 1 and cells[0].has_attr('rowspan'):
                current_difficulty = cells[0].text.strip()
            elif len(cells) > 1:
                current_genre = cells[0].text.strip()

        # Handle song row
        elif len(cells) == 4:
            title = cells[0].text.strip()
            notes = cells[1].text.strip()
            old_rating = cells[2].text.strip()

            song_info = {
                'level': current_level,
                'difficulty': current_difficulty,
                'genre': current_genre,
                'title': title,
                'notes': notes,
                'old_rating': old_rating
            }
            songs.append(song_info)

    return songs

# Fetching song information
songs_info_15 = get_songs_info(url, 445, 'Lv15')
songs_info_14_plus = get_songs_info(url, 507, 'Lv14+')
songs_info_14 = get_songs_info(url, 744, 'Lv14')
songs_info_13_plus = get_songs_info(url, 1030, 'Lv13+')

combined_songs_info = songs_info_15 + songs_info_14_plus + songs_info_14 + songs_info_13_plus

# Print song information
for song in combined_songs_info:
    print(song)

# Saving to JSON
with open('songs_info.json', 'w', encoding='utf-8') as f:
    json.dump(combined_songs_info, f, ensure_ascii=False, indent=4)

# Saving to CSV
df = pd.DataFrame(combined_songs_info)
df.to_csv('songs_info.csv', index=False)
