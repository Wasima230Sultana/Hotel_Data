from flask import Flask, request, render_template, jsonify
import pickle
from hotel_recommendation import recommend_hotels  # import function

app = Flask(__name__)

# Load only the DataFrame
with open("model.pkl", "rb") as f:
    df = pickle.load(f)["df"]

@app.route("/", methods=["GET", "POST"])
def index():
    hotels = None
    if request.method == "POST":
        location = request.form.get("location", "")
        min_price = int(request.form.get("min_price", 0))
        max_price = int(request.form.get("max_price", 20000))
        amenities = [a.strip() for a in request.form.get("amenities", "").split(",") if a.strip()]
        min_rating = float(request.form.get("rating", 0))

        hotels = recommend_hotels(
            df=df,
            location=location,
            budget=(min_price, max_price),
            amenities=amenities,
            min_rating=min_rating,
            top_n=5
        )

    return render_template(
        "index.html",
        hotels=hotels.to_dict(orient="records") if hotels is not None else None
    )

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.json or {}
    hotels = recommend_hotels(
        df=df,
        location=data.get("location", ""),
        budget=tuple(data.get("budget", [0, 20000])),
        amenities=data.get("amenities", []),
        min_rating=data.get("rating", 0),
        top_n=data.get("top_n", 3)
    )
    return jsonify(hotels.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
