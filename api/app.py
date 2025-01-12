import os
import bcrypt
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from prometheus_flask_exporter import PrometheusMetrics

MAKE_RESERVATION = "INSERT INTO reservations (customer_id,restaurant_id, make_date, reservation_date, num_persons, optional_message) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id"
GET_RESERVATION_BY_USER = "select * from reservations where customer_id = %s"
GET_RESERVATION_BY_RESTAURANT = "select * from reservations where restaurant_id = %s"

load_dotenv()

app = Flask(__name__)
cors = CORS(app)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Restaurant Management API Info', version='1.0.0')

def check_database_connection():
    """
    Checks if the database connection is active and operational.
    Raises an exception if the database is not reachable.
    """
    try:
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        cursor.execute('SELECT 1')  
        connection.close()
        print("Database is connected!")
    except OperationalError as err:
        raise Exception("Database is not reachable: " + str(err))

@app.route('/health')
def health_check():
    """
    Health check endpoint to verify the service's status.
    Returns:
        - "Service is healthy" with a 200 status if the database connection is operational.
        - "Service is unhealthy" with a 500 status if the connection check fails.
    """
    try:
        check_database_connection()
        return "Service is healthy", 200
    except:
        return "Service is unhealthy", 500
        
@app.post("/make_reservation")
@cross_origin()
def make_reservation():
    """
    Creates a new reservation.
    Receives reservation details in the request body and stores them in the database.
    Returns:
        - Success: JSON object with reservation ID and a success message (status 200).
    """
    data = request.get_json()
    customer_id = data["customer_id"]
    restaurant_id = data["restaurant_id"]
    make_date = data["make_date"]
    reservation_date = data["reservation_date"]
    num_persons = data["num_persons"]
    optional_message = data["optional_message"]

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                MAKE_RESERVATION,
                (
                    customer_id,
                    restaurant_id,
                    make_date,
                    reservation_date,
                    num_persons,
                    optional_message,
                ),
            )
            reservation_id = cursor.fetchone()[0]

    return (
        jsonify(
            {
                "reservation_id": reservation_id,
                "Message": f"Reservation {reservation_id} created.",
            }
        )
    )


@app.get("/get_reservations_by_user")
@cross_origin()
def get_reservations_by_user():
       """
    Retrieves all reservations made by a specific user.
    Accepts the user ID as a query parameter and fetches the corresponding reservations from the database.
    Returns:
        - Success: JSON object with a list of reservations (status 200).
        - Failure: JSON object with an error message if no reservations are found.
    """
    customer_id = request.args.get("customer_id")

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_RESERVATION_BY_USER, (customer_id,))
            reservations = cursor.fetchall()

    if not reservations:
        return jsonify({"error": "No reservations found"})

    else:
        reservations_list = [
            {
                "reservation_id": row[0],
                "restaurant_id": row[2],
                "reservation_date": row[4],
                "number_guests": row[5],
                "message": row[6],
            }
            for row in reservations
        ]

    return jsonify({"reservations": reservations_list})


@app.get("/get_reservations_by_restaurant")
@cross_origin()
def get_reservations_by_restaurant():
    """
    Retrieves all reservations for a specific restaurant.
    Accepts the restaurant ID as a query parameter and fetches the corresponding reservations from the database.
    Returns:
        - Success: JSON object with a list of reservations (status 200).
        - Failure: JSON object with an error message if no reservations are found.
    """
    restaurant_id = request.args.get("restaurant_id")

    connection = psycopg2.connect(os.getenv("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_RESERVATION_BY_RESTAURANT, (restaurant_id,))
            reservations = cursor.fetchall()

    if not reservations:
        return jsonify({"error": "No reservations found"})

    else:
        reservations_list = [
            {
                "reservation_id": row[0],
                "user_id": row[1],
                "reservation_date": row[4],
                "number_guests": row[5],
                "message": row[6],
            }
            for row in reservations
        ]

    return jsonify({"reservations": reservations_list})


if __name__ == "__main__":
    print("Starting app...")
    app.run(host="0.0.0.0", port=5002)
