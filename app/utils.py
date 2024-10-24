import torch
import requests

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
def extract_track_data(d):
    track_info = {}
    track_info["id"] = d.get("id")
    track_info["name"] = d.get("name")
    track_info["artists"] = [artist.get("name") for artist in d.get("artists", [])]
    return track_info

# request to extract bop data
# output: dict of data
def get_track_info(song_id, access_token):
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})

    if response.status_code == 200:
        return extract_track_data(response.json())
    else:
        print(f"Failed to retrieve song info: {response.status_code}")
        print(response.json())