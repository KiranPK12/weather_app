import os
import requests
from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
url = "https://api.openweathermap.org/data/2.5/weather"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///MyTrackingCities.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Cities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False, unique=True)


db.create_all()


def weather_data_retrive():
    all_cities = db.session.query(Cities).all()
    weather_data = []
    for cities in all_cities:
        params = {
            'q': cities.city,
            'appid': api_key,
            'units': 'metric'
        }
        response = requests.get(url, params=params)
        data = response.json()
        weather = {
            'city': cities.city,
            'city_id': cities.id,
            'temp': f"{data['main']['temp']}°C",
            'weather_description': data['weather'][0]['description'],
            "weather_icon_url": f"https://openweathermap.org/img/w/{data['weather'][0]['icon']}.png"
        }
        weather_data.append(weather)
    return weather_data


def add_city(city_name):
    new_city = Cities(
        city=city_name
    )
    db.session.add(new_city)
    db.session.commit()
    return flash(message="City added successful")


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        city_name = request.form.get("city")
        all_cities = db.session.query(Cities).all()
        list_of_cities = [cities.city for cities in all_cities]
        if city_name in list_of_cities:
            flash(message="That city already exists.")
            return redirect(url_for('home'))

        elif city_name:
            params = {
                'q': city_name,
                'appid': api_key,
                'units': 'metric'
            }

            response = requests.get(url, params=params)
            data = response.json()
            try:
                message = data["message"]
            except KeyError:
                add_city(city_name=city_name)

            else:
                if message == "city not found":
                    flash(message="City not found")
                    return redirect(url_for('home'))

        return render_template("weather.html", weather_data=weather_data_retrive())
    return render_template("weather.html", weather_data=weather_data_retrive())


@app.route("/new", methods=["GET", "POST"])
def delete_city():
    city_id = request.args.get("id")
    city_to_delete = Cities.query.get(city_id)
    db.session.delete(city_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
