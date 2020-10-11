#################################################
# Dependencies
#################################################

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base=automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement 

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


#Home Route
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


#Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    """Return the JSON representation of your dictionary."""

    twelve_months_ago=dt.date(2017,8,23)-dt.timedelta(days=365)

    results=session.query(measurement.date, measurement.prcp).filter(measurement.date >= twelve_months_ago).all()

    session.close()
    
    data_precipitation = {dte: precip for dte, precip in results}

    return jsonify(data_precipitation)


#Stations Route
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)

    """Return a JSON list of stations from the dataset."""
    results=session.query(measurement.station).group_by(measurement.station).all()

    session.close()

    stations_list=list(np.ravel(results))

    return jsonify(stations_list)

#Temperature Route
@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data."""
    """Return a JSON list of temperature observations (TOBS) for the previous year."""

    twelve_months_ago=dt.date(2017,8,23)-dt.timedelta(days=365)
    active_station=session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station=active_station[0][0]
    results=session.query(measurement.tobs).filter(measurement.station==most_active_station).filter(measurement.date >= twelve_months_ago).all()

    session.close()

    temperatures=list(np.ravel(results))

    return jsonify(temperatures)

#Start Route

@app.route("/api/v1.0/<start>")
def start(start):
    session=Session(engine)


    temps=[func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)]
    active_station=session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station=active_station[0][0]
    results=session.query(*temps).filter(measurement.station==most_active_station).filter(measurement.date>=start).all()

    session.close()

    temperatures=[]

    for TMIN, TMAX, TAVG in results:
        temperatures_dict = {}
        temperatures_dict["TMIN"] = TMIN
        temperatures_dict["TMAX"] = TMAX
        temperatures_dict["TAVG"] = TAVG
        temperatures.append(temperatures_dict)

    

    return jsonify(temperatures)

#Start-End Route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session=Session(engine)


    temps=[func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)]
    active_station=session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station=active_station[0][0]
    results=session.query(*temps).filter(measurement.station==most_active_station).filter(measurement.date>=start).filter(measurement.date<=end).all()

    session.close()

    temperatures=[]

    for TMIN, TMAX, TAVG in results:
        temperatures_dict = {}
        temperatures_dict["TMIN"] = TMIN
        temperatures_dict["TMAX"] = TMAX
        temperatures_dict["TAVG"] = TAVG
        temperatures.append(temperatures_dict)

    

    return jsonify(temperatures)





if __name__ == '__main__':
    app.run(debug=True)