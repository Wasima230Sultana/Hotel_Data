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
    error = None
    if request.method == "POST":
        try:
            location = request.form.get("location", "")
            min_price = int(request.form.get("min_price", 0))
            max_price = int(request.form.get("max_price", 20000))
            amenities = [a.strip() for a in request.form.get("amenities", "").split(",") if a.strip()]
            min_rating = float(request.form.get("rating", 0))
        except (TypeError, ValueError):
            error = "Price and rating must be valid numbers."
        else:
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
        hotels=hotels.to_dict(orient="records") if hotels is not None else None,
        error=error
    )

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.json or {}
    try:
        budget = tuple(data.get("budget", [0, 20000]))
        if len(budget) != 2:
            raise ValueError("budget must be [low, high]")
        budget = (float(budget[0]), float(budget[1]))
        min_rating = float(data.get("rating", 0))
        top_n = int(data.get("top_n", 3))
    except (TypeError, ValueError):
        return jsonify({"error": "budget must be [low, high] numbers; rating and top_n must be numbers"}), 400

    hotels = recommend_hotels(
        df=df,
        location=data.get("location", ""),
        budget=budget,
        amenities=data.get("amenities", []),
        min_rating=min_rating,
        top_n=top_n
    )
    return jsonify(hotels.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
