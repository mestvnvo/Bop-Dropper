from flask import Flask, render_template, url_for, request, redirect, session
from pymongo import MongoClient
from dotenv import load_dotenv
import utils 
import embed
import os

load_dotenv()
mongo_user = os.getenv("MONGO_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_ROOT_PASSWORD")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI="https://bopdropper.com/callback"
# REDIRECT_URI=http://localhost:5000/callback

# start Flask, MongoDB
app = Flask(__name__)
app.secret_key = os.urandom(24)  # session management
app.config["SESSION_PERMANENT"] = False  # temporary session
app.config["SESSION_TYPE"] = "filesystem"

client = MongoClient(f"mongodb://{mongo_user}:{mongo_pass}@mongo:27017/") # for deployment
# client = MongoClient("localhost", 27017) # for local debugging purposes
db = client.bop_database
bops = db.bops

# step 1 of authorization code flow - router; routes to redirect
@app.route("/login")
def login():
    scope = "user-read-private"
    auth_url = (
        f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}"
        f"&response_type=code&redirect_uri={REDIRECT_URI}&scope={scope}"
    )
    return redirect(auth_url)

# step 2 of authorization code flow - router; routes back home
@app.route("/callback")
def callback():
    code = request.args.get("code")
    valid = utils.validate_admin(code)

    if valid:
        session["admin"] = True  # store admin session in a temporary session cookie
        return redirect(url_for("index",login="success"))
    
    return redirect(url_for("index",login="failed"))

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
def index(login=None):
    login = request.args.get('login')

    # if search button is clicked
    if request.method == "POST":
        bop_link = request.form["bop_link"]
        return handle_link(bop_link)
    
    return render_template("index.html", login=login)

# bop router; can route to other bops
@app.route("/bop/<bop_id>", methods=["GET","POST"])
def get_bop_recs(bop_id):
    # if search button is clicked
    if request.method == "POST":
        bop_link = request.form["bop_link"]
        return handle_link(bop_link)

    res = bops.find_one({"id":bop_id})
    bop_info = utils.get_bop_info(bop_id)

    # only get recs if bop exists in db, otherwise try to add
    if not res:
        return redirect(url_for("add_bop",bop_id=bop_id))
    else:
        all_bops = list(bops.find())

        # get recs
        ids, scores = utils.compare_embeddings(res, all_bops, k=6)
        recs = [{"id": id, "score": f"{score.item() * 100:.2f}%"} 
                        for id, score in zip(ids, scores)]

    return render_template("bop.html", bop_info=bop_info, recommendations=recs[1::])

# append new bops router; can route to login or other bops
@app.route("/add_bop/<bop_id>", methods=["GET","POST"])
def add_bop(bop_id):
    # if bop already exists, redirect to bop router
    res = bops.find_one({"id":bop_id})
    if res:
        redirect(url_for("get_bop_recs",bop_id=bop_id))

    bop_info = utils.get_bop_info(bop_id)

    if request.method == "POST":
        bop_link = request.form["bop_link"]
        return handle_link(bop_link)

    # if I'm logged in
    if session.get("admin"):
        # downloads & embeds bop
        link = embed.get_download_link(bop_id)
        embed.download_with_link(link)
        embeds = embed.embed_bop("downloaded_file")

        # post new bop
        bop_info["embedding"] = embeds
        bops.insert_one(bop_info)
        return redirect(url_for("get_bop_recs",bop_id=bop_id))

    return render_template("bop.html",bop_info=bop_info,recommendations=[],not_db=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)