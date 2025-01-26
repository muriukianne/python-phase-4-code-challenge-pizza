#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask import jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/restaurants", methods = ["GET"])
def index():
    restaurants = Restaurant.query.all()
    restaurant_list = []

    for restaurant in restaurants:
        restaurant_list.append({
            'id':restaurant.id,
            'name':restaurant.name,
            'address':restaurant.address
        })
    return jsonify(restaurant_list)    

@app.route("/restaurants/<int:restaurant_id>", methods=["GET"])
def fetch_restaurant(restaurant_id):
    restaurant = db.session.get(Restaurant, restaurant_id)

    if restaurant:
        restaurant_pizzas = [
            {"id": restaurant_pizza.pizza.id, "name": restaurant_pizza.pizza.name} 
            for restaurant_pizza in restaurant.pizzas  
        ]

        return jsonify({
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': restaurant_pizzas
        }), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route("/restaurants/<int:restaurant_id>", methods=["DELETE"])
def delete_restaurant(restaurant_id):
    restaurant = db.session.get(Restaurant, restaurant_id)

    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204  
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()  
    
    pizza_list = [
        {
        'id': pizza.id, 
        'name': pizza.name, 
        'ingredients': pizza.ingredients}

        for pizza in pizzas
    ]

    return jsonify(pizza_list)        

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()  

   
    if data is None:
        return jsonify({"errors": ["Invalid JSON, could not parse the request body"]}), 400

    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

  
    if price < 1 or price > 30:
        return jsonify({"errors": ["validation errors"]}), 400

 
    new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)

 
    db.session.add(new_restaurant_pizza)
    db.session.commit()

   
    return jsonify({
        "id": new_restaurant_pizza.id,
        "price": new_restaurant_pizza.price,
        "pizza_id": new_restaurant_pizza.pizza_id,
        "restaurant_id": new_restaurant_pizza.restaurant_id,
        "pizza": {
            "id": new_restaurant_pizza.pizza.id,
            "name": new_restaurant_pizza.pizza.name
        },
        "restaurant": {
            "id": new_restaurant_pizza.restaurant.id,
            "name": new_restaurant_pizza.restaurant.name,
            "address": new_restaurant_pizza.restaurant.address
        }
    }), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
