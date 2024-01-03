import requests
from bs4 import BeautifulSoup

# URL of the website
url = 'https://gamerch.com/chunithm/entry/491431'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def get_songs_info(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the webpage, Status Code:", response.status_code)
        return

    lines = response.content.decode().splitlines()
    html_content = '\n'.join(lines[446:])  # Starting from line 447 (0-based indexing)

    soup = BeautifulSoup(html_content, 'html.parser')

    song_table = soup.find('table')
    if not song_table:
        print("Failed to find the song table in the HTML")
        return

    level_15_4_songs = []
    collect_data = False
    for row in song_table.find_all('tr'):
        if '15.4' in row.text:
            collect_data = True  # Start collecting data
            continue
        if '15.3' in row.text:
            break  # Stop collecting data

        if collect_data:
            cells = row.find_all('td')
            if cells and len(cells) >= 5:  # Ensure there are enough cells
                song_info = {
                    'title': cells[2].find('a').text.strip() if cells[2].find('a') else cells[2].text.strip(),
                    'notes': cells[3].text.strip(),
                    'old_rating': cells[4].text.strip()
                }
                level_15_4_songs.append(song_info)

    return level_15_4_songs

# Call the function and print the results
songs_info = get_songs_info(url)
for song in songs_info:
    print(song)
