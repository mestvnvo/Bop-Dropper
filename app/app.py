from flask import Flask, render_template, url_for, request, redirect
from pymongo import MongoClient
import utils as u

app = Flask(__name__)
client = MongoClient("localhost", 27017)
db = client.bop_database
bops = db.bops
access_token = u.generate_access_token()

@app.route("/", methods=["GET","POST"])
def index():
    error = None
    if request.method == "POST":
        bop_link = request.form["bop_link"]
        if not u.link_validation(bop_link):
            # HANDLE EDM GENRE OR NOT?
            error = "Please enter a valid Spotify track link."
        else:
            bop_id = bop_link.split("/")[-1].split('?')[0]
            return redirect(url_for("get_bop_recs",bop_id=bop_id))
    
    return render_template("index.html", error=error, in_db=True)

@app.route("/bop/<bop_id>", methods=["GET","POST"])
def get_bop_recs(bop_id):
    error = None
    in_db = True
    if request.method == "POST":
        bop_link = request.form["bop_link"]
        if not u.link_validation(bop_link):
            # HANDLE EDM GENRE OR NOT?
            error = "Please enter a valid Spotify track link."
            return render_template("index.html",error=error)
        else:
            bop_id = bop_link.split("/")[-1].split('?')[0]
            return redirect(url_for("get_bop_recs",bop_id=bop_id))

    # get bop info and bop_db
    res = bops.find_one({"id":bop_id})
    bop_info = u.get_bop_info(bop_id, access_token)
    if res:
        all_bops = list(bops.find())

        # get recs
        ids, scores = u.compare_embeddings(res, all_bops, k=6)
        recommendations = [{"id": id, "score": f"{score.item() * 100:.4g}%"} 
                        for id, score in zip(ids, scores)]
    else:
        recommendations = []
        in_db = False
        # ADD NOT IN DB CASE
        # 1) ADD TO A PLAYLIST, ONCE REACHES N LENGTH, EMBED PLAYLIST
        # 2) EMBED SONG ON THE SPOT?

        # WE DO WANT ABILITY TO EMBED ENTIRE PLAYLISTS SO WE CAN EXPAND QUICKER

    return render_template("index.html",bop_info=bop_info, recommendations=recommendations, in_db=in_db)

if __name__ == "__main__":
    app.run(debug=True)