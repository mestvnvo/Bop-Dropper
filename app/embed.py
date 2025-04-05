import requests
import os
import librosa
import torch
from transformers import ClapModel, ClapProcessor
from bs4 import BeautifulSoup

# instantiates CLAP model/processor
sampling_rate = 48000
model = None
processor = None

# implements lazy singleton because droplet keeps crashing on second embed
# output: model, processor
def get_model_and_processor():
    global model, processor
    if model is None or processor is None:
        model = ClapModel.from_pretrained("laion/larger_clap_music")
        processor = ClapProcessor.from_pretrained("laion/larger_clap_music")
    return model, processor

# steals csrf token in a BS4 session
# output: POST creds
def get_csrf_token(url):
    session = requests.Session()
    response = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    if response.status_code != 200:
        print("Failed to load page:", response.status_code)
        return None, None

    # parse html for exposed csrf token & retain cookies
    soup = BeautifulSoup(response.text, "html.parser")
    csrf_token = soup.find("meta", {"name": "csrf-token"})
    csrf_token_value = csrf_token["content"] if csrf_token else None

    cookies = session.cookies.get_dict()

    return csrf_token_value, cookies

# gets download link from spowload with bop id
# output: download link
def get_download_link(id):
    url = f"https://spowload.com/spotify/track-{id}"

    csrf_token, cookies = get_csrf_token(url)

    if not csrf_token or not cookies:
        print("Failed to fetch CSRF token or cookies.")
        return None

    headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token,
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://spowload.com/",
    }

    data = {"urls": f"https://open.spotify.com/track/{id}"}

    response = requests.post("https://spowload.com/convert", json=data, headers=headers, cookies=cookies)

    if response.status_code == 200:
        print("Conversion Successful:", response.json())
        return response.json()["url"]
    else:
        print("Conversion Failed:", response.status_code, response.text)
        return None

# downloads file
# output: None
def download_with_link(link):
    response = requests.get(url=link)

    if response.status_code == 200:
        with open("downloaded_file.mp3", "wb") as file:
            file.write(response.content)
        print("MP3 file downloaded successfully.")
    else:
        print("Failed to download MP3 file. Status code:", response.status_code)

# embed one bop and deletes mp3 file afterwards
# output: embeddings as a [512] list
def embed_bop(name):
    mp3_file = os.path.join(f"{name}.mp3")

    if not os.path.isfile(mp3_file):
        print(f"MP3 file for {name} not found.")
        return None

    audio_data, _ = librosa.load(mp3_file, sr=sampling_rate)
    model, processor = get_model_and_processor()

    # process and embed audio
    inputs = processor(audios=[audio_data], sampling_rate=sampling_rate, return_tensors="pt")
    with torch.no_grad():
        audio_embed = model.get_audio_features(**inputs)

    # convert the tensor to a list (to make it JSON serializable)
    audio_embed_list = audio_embed.squeeze().tolist()

    # delete file after embedding to save space
    try:
        os.remove(mp3_file)
        print(f"{mp3_file} deleted successfully.")
    except Exception as e:
        print(f"Failed to delete {mp3_file}: {e}")

    return audio_embed_list