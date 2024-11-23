from database import get_connection

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/request', methods=['POST'])
def request_ride():
    data = request.json
    request_number = data['request_number']
    pickup = data['pickup']
    drop_off = data['drop_off']

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
           SELECT id, location
           FROM driver
           WHERE status = 'online' and 'location' = 'pickup'
       """, (pickup, drop_off))
    driver = cur.fetchone()

    if not driver:
        return jsonify({"error": "No drivers available"}), 400

    driver_id = driver[0]

    cur.execute(
        "INSERT INTO request (request_number, pickup, drop_off, driver, status) VALUES (%s, %s, %s, %s, 'pending') RETURNING id",
        (request_number, pickup, drop_off, driver_id)
    )
    ride_id = cur.fetchone()[0]

    cur.execute("UPDATE driver SET status = 'busy' WHERE license = %s", (driver_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"request_number": request_number, "driver": driver_id}), 201

@app.route('/ride/<int:ride_number>/accept', methods=['PATCH'])
def accept_ride(ride_number):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE ride SET ride_status = 'accepted' WHERE driver = %s RETURNING driver_id",
        (ride_number,)
    )
    result = cur.fetchone()

    if not result:
        return jsonify({"error": "Ride not found"}), 404

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Ride accepted"}), 200

