# Import 
from flask import Flask, jsonify

from builtins import dict

import datetime as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from datetime import timedelta

engine= create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

# Set Tables to parameters
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session (link) from Python to the DB
session = Session(engine)

# Set up Flask
app = Flask(__name__)

# Define static routes
@app.route("/")
def welcome():
    return (
        f" Climate Analysis Homepage:<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"

    )

# Convert the query results to a dictionary using date as the key and prcp as the value
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Set end_date and start_date
    end_month = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_month = dt.date.fromisoformat(end_month[0])
    start_month = end_month - timedelta(days=365)

    # Query data from table Measurement in the DB
    prcp_12mths_data = session.query(Measurement.date, Measurement.prcp)\
                        .filter(Measurement.date >= start_month)\
                        .order_by(Measurement.date.desc()).all()

    # Convert query results to dictionary                    
    prcp_12mths_data_dict = dict(prcp_12mths_data)

    # Show result as json file
    return jsonify(prcp_12mths_data_dict)

# Return a Json list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():

    stations_list = session.query(Station.station, Station.name).all()
    stations_dict = dict(stations_list)
    return jsonify(stations_dict)

# Query the dates and temperature observations of the most active station for the last year of data (USC00519281)
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():

    # Set end_date and start_date
    end_month = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_month = dt.date.fromisoformat(end_month[0])
    start_month = end_month - timedelta(days=365)

    # Query the date and tobs of station USC00519281
    temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281')\
                                                            .filter(Measurement.date >= start_month)\
                                                            .all()
    temp_dict = dict(temp)
    return jsonify(temp_dict)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")
def temp_stat(start):


    temp_result = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs) )\
                        .filter(Measurement.date >= start)\
                        .all()
    
    return jsonify(temp_result)

    
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):


    temp_result_2 = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs) )\
                        .filter(Measurement.date >= start)\
                        .filter(Measurement.date <= end)\
                        .all()
    
    return jsonify(temp_result_2)

if __name__ == '__main__':
    app.run(debug=True)