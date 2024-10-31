import requests
import os
import librosa
import torch
from transformers import ClapModel, ClapProcessor

# instantiates model/processor
sampling_rate = 16000
model = ClapModel.from_pretrained("laion/larger_clap_music")
processor = ClapProcessor.from_pretrained("laion/larger_clap_music", sampling_rate=sampling_rate)

def get_download_link(id):
    url = f"https://api.spotifydown.com/download/{id}"

    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://spotifydown.com',
    'priority': 'u=1, i',
    'referer': 'https://spotifydown.com/',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(response.json().get("link"))
        return response.json().get("link")
    else:
        print("Failed to get download link.")
        return None

def download_with_link(link):
    response = requests.get(url=link)
    print(response)
    if response.status_code == 200:
        with open("downloaded_file.mp3", "wb") as file:
            file.write(response.content)
        print("MP3 file downloaded successfully.")
    else:
        print("Failed to download MP3 file. Status code:", response.status_code)

# embed one bop
def embed_bop(name):
    mp3_file = os.path.join(f"{name}.mp3")

    if not os.path.isfile(mp3_file):
        print(f"MP3 file for {name} not found.")
        return None

    audio_data, _ = librosa.load(mp3_file, sr=sampling_rate)

    # process and embed audio
    inputs = processor(audios=[audio_data], return_tensors="pt")
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