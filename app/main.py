from flask import Flask, render_template, url_for, request, redirect
from pymongo import MongoClient
from embed import model, processor
from utils import access_token
from dotenv import load_dotenv
import utils 
import embed
import os

load_dotenv()
mongo_user = os.getenv("MONGO_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_ROOT_PASSWORD")

# start Flask, MongoDB
app = Flask(__name__)
client = MongoClient(f"mongodb://{mongo_user}:{mongo_pass}@mongo:27017/") # for deployment
# client = MongoClient("localhost", 27017) # for local debugging purposes
db = client.bop_database
bops = db.bops

# validates if link IS a spotify track, if no error then search; otherwise display error
# output: none, redirect or updates visual
def handle_link(bop_link):
    error = utils.link_validation(bop_link)
    if error:
        return render_template("index.html",error=error)
    else:
        bop_id = bop_link.split("/")[-1].split('?')[0]
        return redirect(url_for("get_bop_recs",bop_id=bop_id))

# home router; can route to bop if given a valid Spotify track link
@app.route("/", methods=["GET","POST"])
def index():
    # if search button is clicked
    if request.method == "POST":
        bop_link = request.form["bop_link"]
        return handle_link(bop_link)
    
    return render_template("index.html", error=None)

# bop router; can route to other bops
@app.route("/bop/<bop_id>", methods=["GET","POST"])
def get_bop_recs(bop_id):
    # if search button is clicked
    if request.method == "POST":
        bop_link = request.form["bop_link"]
        return handle_link(bop_link)

    res = bops.find_one({"id":bop_id})
    bop_info = utils.get_bop_info(bop_id)
    # if bop IS in database, get recs; otherwise return ...
    # EVENTUALLY ADD OAUTH LOGIN AND WAY FOR PUBLIC TO REC SONGS TO ADD
    if res:
        all_bops = list(bops.find())

        # get recs
        ids, scores = utils.compare_embeddings(res, all_bops, k=6)
        recommendations = [{"id": id, "score": f"{score.item() * 100:.2f}%"} 
                        for id, score in zip(ids, scores)]
    else:
        error = "WIP"
        return render_template("index.html", bop_info=bop_info, error=error, not_db=True)

    return render_template("bop.html", bop_info=bop_info, recommendations=recommendations[1::])

# append new bops router; routes back to bop router on completion
# TEMPORARILY OUT OF SERVICE.. they secured their API :)

# @app.route("/add_bop/<bop_id>", methods=["GET","POST"])
# def add_bop(bop_id):
#     if request.method == "POST":
#         bop_info = u.get_bop_info(bop_id)

#         # downloads & embeds bop
#         link = e.get_download_link(bop_id)
#         e.download_with_link(link)
#         embeds = e.embed_bop("downloaded_file")

#         # post new bop
#         bop_info["embedding"] = embeds
#         bops.insert_one(bop_info)
#         return redirect(url_for("get_bop_recs",bop_id=bop_id))

#     return render_template("index.html", recommendations=[],in_db=False,add_button=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)