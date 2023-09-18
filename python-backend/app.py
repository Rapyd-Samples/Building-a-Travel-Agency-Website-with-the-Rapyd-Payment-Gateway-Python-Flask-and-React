from flask import  Flask, g, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import jwt
import datetime
import json
from rapyd_utils import make_request

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float(), default='0.00')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    trip = db.relationship('Trip', backref='bookings')

api_prefix = "/v1"

def create_rapyd_payment(amount, user_id, trip_id):
    path = '/v1/checkout'

    payment_data = {
        "amount": str(amount),
        "complete_payment_url": "http://example.com/complete",
        "country": "US",
        "currency": "USD",
        "error_payment_url": "http://example.com/error",
        "language": "en",
        "merchant_reference_id": f"booking_{user_id}_{trip_id}"
    }

    try:
        response = make_request(method='post', path=path, body=payment_data)

        if response['status']['status'] == "SUCCESS":
            response_data = response['data']
            return response_data
        else:
            print("Rapyd API returned an error status:", response['status']['status'])
            return None
    except Exception as e:
        print("Error creating Rapyd payment:", str(e))
        return None

def generate_token(username):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {
        'username': username,
        'exp': expiration_time
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def require_auth_token(route_function):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Authorization token missing'}), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return route_function(*args, **kwargs)

    return wrapper

def seed_trip():
    trips_data = [
        {'name': 'trip 1', 'description': 'This is a nice place', 'price': 599.99},
        {'name': 'trip 2', 'description': 'This is a nice place too', 'price': 899.99},
    ]

    for trip_info in trips_data:
        trip = Trip(**trip_info)
        db.session.add(trip)

    db.session.commit()

@app.route(api_prefix + '/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)

    try:
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'message': 'Username already exists'}), 400
        else:
            return jsonify({'message': 'An error occured'})

@app.route(api_prefix + '/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Login successful'})

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        token = generate_token(username)
        return jsonify({'user_id': user.id,'token': token,'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@app.route(api_prefix + '/trips', methods=['GET'])
@require_auth_token
def list_trips():
    trips = Trip.query.all()
    trip_list = [{'id': trip.id, 'name': trip.name, 'description': trip.description, 'price': trip.price} for trip in trips]
    return jsonify({'trips': trip_list}), 200

@app.route(api_prefix + '/bookings', methods=['POST'])
def book_trip():
    data = request.get_json()
    trip_id = data.get('trip_id')
    user_id = data.get('user_id')

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authorization token missing'}), 401

    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    if not trip_id:
        return jsonify({'message': 'Trip is required to make a booking'}), 400

    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'message': 'trip not found'}), 404

    payment_response = create_rapyd_payment(trip.price, user_id, trip_id)

    if payment_response:
        booking = Booking(user_id=user_id, trip_id=trip_id)
        db.session.add(booking)
        db.session.commit()

        return jsonify({'message': 'Booking successful', 'payment_response': payment_response}), 201
    else:
        return jsonify({'message': 'Failed to create payment', 'payment_response': payment_response}), 500


@app.route('/seed-trips', methods=['GET'])
def seed_trips():
    seed_trip()
    return jsonify({'message': 'Seeded!'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

