from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

# Create Flask app
app = Flask(__name__)

# Function to scrape movies from TamilMV
def tamilmv():
    main_url = 'https://www.1tamilmv.legal/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
    movie_list = []
    real_dict = {}

    try:
        web = requests.get(main_url, headers=headers, timeout=10)
        web.raise_for_status()
        soup = BeautifulSoup(web.text, 'lxml')
        temps = soup.find_all('div', {'class': 'ipsType_break ipsContained'})

        for i in range(min(21, len(temps))):
            title = temps[i].find_all('a')[0].text.strip()
            link = temps[i].find('a')['href']
            movie_list.append(title)

            movie_details = get_movie_details(link)
            real_dict[title] = movie_details

    except requests.exceptions.RequestException as e:
        return [], {"error": str(e)}

    return movie_list, real_dict

# Function to scrape movie details
def get_movie_details(url):
    try:
        html = requests.get(url, timeout=10)
        html.raise_for_status()
        soup = BeautifulSoup(html.text, 'lxml')

        mag = [a['href'] for a in soup.find_all('a', href=True) if 'magnet:' in a['href']]
        filelink = [a['href'] for a in soup.find_all('a', {"data-fileext": "torrent", 'href': True})]
        movie_title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Title"

        movie_details = []
        for p in range(len(mag)):
            movie_details.append({
                "title": movie_title,
                "magnet_link": mag[p],
                "torrent_file_link": filelink[p] if p < len(filelink) else None
            })

        return movie_details
    except Exception as e:
        return {"error": str(e)}

# Define routes
@app.route("/")
def home():
    return jsonify({"message": "Welcome to Flask on Vercel!"})

@app.route("/fetch_movies", methods=["GET"])
def fetch_movies():
    movie_list, movie_details = tamilmv()
    return jsonify({
        "movies": movie_list,
        "details": movie_details
    })

# Expose the app as `app`
if __name__ == "__main__":
    app.run()
