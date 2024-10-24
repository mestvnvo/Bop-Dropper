import requests

#  extracts id, name, and artist(s)
# output: dict of data
def extract_bop_data(d):
    bop_info = {}
    bop_info["id"] = d.get("id")
    bop_info["name"] = d.get("name")
    bop_info["artists"] = [artist.get("name") for artist in d.get("artists", [])]
    return bop_info

# request to extract bop data
# output: dict of data
def get_bop_info(bop_id, access_token):
    url = f"https://api.spotify.com/v1/tracks/{bop_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})

    if response.status_code == 200:
        return extract_bop_data(response.json())
    else:
        print(f"Failed to retrieve bop info: {response.status_code}")
        print(response.json())