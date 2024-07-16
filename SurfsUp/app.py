# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )

#@app.route("/api/v1.0/precipitation")
#def precipitation():
    # Create our session (link) from Python to the DB
#    session = Session(engine)

    # Query all precipitation
#    results = session.query(Measurement.date, Measurement.prcp).all()

#    session.close()

    # Convert list of tuples into dictionary
#    all_precipitation = {date: prcp for date, prcp in results}

#    return jsonify(all_precipitation)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Determine the latest date in the dataset
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - timedelta(days=365)

    # Query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp)\
                     .filter(Measurement.date >= one_year_ago)\
                     .all()

    session.close()

    # Convert list of tuples into dictionary
    all_precipitation = {date: prcp for date, prcp in results}

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Convert list of tuples into dictionary
    all_stations = {station: name for station, name in results}

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data
    # Assuming the most active station is USC00519281
    results = session.query(Measurement.date, Measurement.tobs)\
                     .filter(Measurement.station == 'USC00519281')\
                     .filter(Measurement.date >= '2016-08-23')\
                     .all()

    session.close()

    # Convert list of tuples into list of dictionaries
    all_tobs = [{date: tobs} for date, tobs in results]

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start_date).all()
        session.close()

        temps = list(np.ravel(results))
        return jsonify({
            'min_temperature': temps[0],
            'avg_temperature': temps[1],
            'max_temperature': temps[2]
        })
    except ValueError:
        session.close()
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        session.close()

        temps = list(np.ravel(results))
        return jsonify({
            'min_temperature': temps[0],
            'avg_temperature': temps[1],
            'max_temperature': temps[2]
        })
    except ValueError:
        session.close()
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400




if __name__ == '__main__':
    app.run(debug=True)

