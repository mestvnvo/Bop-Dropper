import torch
import requests
import os
from dotenv import load_dotenv

# gets spotify key from env to generate access token (lasts 1 hr)
# output: access token
def generate_access_token():
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

    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        print(f"Access Token: {access_token}")
        return access_token
    else:
        print(f"Failed to retrieve token: {response.status_code}")
        print(response.json())
        return None

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