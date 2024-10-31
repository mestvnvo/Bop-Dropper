from flask import Flask, render_template, url_for, request, redirect
from pymongo import MongoClient
from embed import model, processor
from utils import access_token
import utils as u
import embed as e

# start Flask, MongoDB
app = Flask(__name__)
client = MongoClient("localhost", 27017)
db = client.bop_database
bops = db.bops

# home router; can route to bop if given a valid Spotify track link
@app.route("/", methods=["GET","POST"])
def index():
    error = None
    if request.method == "POST":
        bop_link = request.form["bop_link"]
        error = u.link_validation(bop_link, access_token)
        if error:
            return render_template("index.html",error=error, in_db=True)
        else:
            bop_id = bop_link.split("/")[-1].split('?')[0]
            return redirect(url_for("get_bop_recs",bop_id=bop_id))
    
    return render_template("index.html", error=error, in_db=True, add_button=False)

# bop router; can route to other bops...
@app.route("/bop/<bop_id>", methods=["GET","POST"])
def get_bop_recs(bop_id):
    error = None
    in_db = True
    if request.method == "POST":
        bop_link = request.form["bop_link"]
        error = u.link_validation(bop_link, access_token)
        if error:
            return render_template("index.html",error=error, in_db=in_db)
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
        return redirect(url_for("add_bop",bop_id=bop_id))

    return render_template("index.html",bop_info=bop_info, recommendations=recommendations[1::], in_db=in_db, add_button=False)

@app.route("/add_bop/<bop_id>", methods=["GET","POST"])
def add_bop(bop_id):
    if request.method == "POST":
        bop_info = u.get_bop_info(bop_id,access_token)

        # downloads & embeds bop
        link = e.get_download_link(bop_id)
        e.download_with_link(link)
        embeds = e.embed_bop("downloaded_file")

        # post new bop
        bop_info["embedding"] = embeds
        bops.insert_one(bop_info)
        return redirect(url_for("get_bop_recs",bop_id=bop_id))

    return render_template("index.html", recommendations=[],in_db=False,add_button=True)

if __name__ == "__main__":
    app.run(debug=False)