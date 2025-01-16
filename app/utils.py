import torch
import requests
import os
import time
from dotenv import load_dotenv

# gets spotify key from env to generate access token (lasts 1 hr)
# output: none, but sets access_token var
def generate_access_token():
    global access_token, token_expiration_time
    load_dotenv()
    SPOTIFY_KEY = os.getenv("SPOTIFY_KEY")

    headers = {
        "Authorization": f"Basic {SPOTIFY_KEY}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    token_expiration_time = time.time() + 3600

    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        print(f"Access Token: {access_token}")
        return None
    else:
        print(f"Failed to retrieve token: {response.status_code}")
        print(response.json())
        return None

# if current time has past 1 hr limit of token, refresh token
# output: none
def check_token():
    if time.time() >= token_expiration_time:
        generate_access_token()

# compares one bop to collection of bops
# output: top k names, artists, scores
def compare_embeddings(new_bop, collection, k=5):
    new_embedding = torch.tensor(new_bop['embedding']).unsqueeze(0)  # shape [1, 512]
    embeddings = torch.stack([torch.tensor(bop['embedding']) for bop in collection])

    # compute cosine similarity between new_track embedding and all embeddings in collection
    similarities = torch.nn.functional.cosine_similarity(new_embedding, embeddings, dim=1)

    # get the top-k most similar embeddings
    top_k_scores, top_k_indices = torch.topk(similarities, k, largest=True)
    top_k_ids = [collection[i]['id'] for i in top_k_indices]

    return top_k_ids, top_k_scores

# extracts id, name, and artist(s)
# output: dict of data
def extract_bop_data(d):
    bop_info = {}
    bop_info["id"] = d["id"]
    bop_info["name"] = d["name"]
    bop_info["artists"] = [artist.get("name") for artist in d.get("artists", [])]
    bop_info["image"] = d["album"]["images"][0]["url"]
    return bop_info

# request to extract bop data
# output: dict of data
def get_bop_info(bop_id):
    check_token()

    url = f"https://api.spotify.com/v1/tracks/{bop_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})

    if response.status_code == 200:
        return extract_bop_data(response.json())
    else:
        print(response.json())
        return None

# validates link, first ensuring it's a track link, then if it's an actual track (not just a series of numbers after /track/)
# output: None if IS track; str if ISN'T
def link_validation(url):
    id = url.split("/")[-1].split('?')[0]
    if url.startswith("https://open.spotify.com/track/") and get_bop_info(id):
        return None
    else:
        return "Please enter a valid Spotify track link."
    
# instantiate global access_token & exp. time
access_token = generate_access_token()
token_expiration_time = 0