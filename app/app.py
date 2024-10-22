from flask import Flask, render_template, url_for, request, redirect
from pymongo import MongoClient
import utils

app = Flask(__name__)

client = MongoClient("localhost", 27017)

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "POST":
        bop_link = request.form["bop_link"].split("/")[-1].split('?')[0]
        # TO ADD: link verification
        # if link IS a spotify link, BUT ISN'T in my DB
        return redirect(url_for("get_bop_recs",bop_id=bop_link))
    return render_template("index.html")

@app.route("/bop/<bop_id>", methods=["GET","POST"])
def get_bop_recs(bop_id):
    if request.method == "POST":
        new_bop_link = request.form["bop_link"].split("/")[-1].split('?')[0]
        # TO ADD: link verification, etc
        return redirect(url_for("get_bop_recs",bop_id=new_bop_link))

    # get bop info and bop_db
    res = bops.find_one({"id":bop_id})
    all_bops = list(bops.find())

    bop_info = {
        "bop_name": res["name"],
        "artists": res["artists"]
    }

    # get recs
    names, artists, scores = utils.compare_embeddings(res, all_bops, k=6)

    recommendations = [{"name": name, "artists": artist, "score": f"{score.item() * 100:.4g}%"} 
                       for name, artist, score in zip(names, artists, scores)]

    return render_template("index.html",bop_info=bop_info, recommendations=recommendations)

db = client.bop_database
bops = db.bops

if __name__ == "__main__":
    app.run(debug=True)