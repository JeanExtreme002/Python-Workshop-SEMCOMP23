from flask import Flask, render_template, request, send_file
from tempfile import NamedTemporaryFile
import music_tag

from bs4 import BeautifulSoup
import wikipedia
import os


def get_music_year(music_title):
    titles = wikipedia.search(f"{music_title} music")
    if not titles: return

    page = wikipedia.page(titles[0])

    soup = BeautifulSoup(page.html(), "html.parser")
    infobox = soup.select_one(".infobox")

    if not infobox: return
    
    index = -1
    
    for label in infobox.select(".infobox-label"):
        index += 1
        
        if label.text.lower() == "released":
            break
    
    if index != -1:
        date = infobox.select(".infobox-data")[index].contents[0]
        return int(date.split(",")[-1].strip())
    

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")
	
@app.route("/upload", methods = ["POST"])
def upload():
    music = request.files["music"]
    image = request.files["image"]

    with NamedTemporaryFile(delete = False) as temp_music:
        temp_music.write(music.read())

    file = music_tag.load_file(temp_music.name)
    
    file["album"] = request.form["album"]
    file["artwork"] = image.read()

    title = os.path.splitext(music.filename)[0]
    file["year"] = get_music_year(title)
    
    file.save()

    return send_file(temp_music.name, download_name = music.filename, as_attachment = True)

		
if __name__ == "__main__":
    app.run(port = 5000, debug = True)
