import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)


measurements = Base.classes.measurement

station = Base.classes.station


app = Flask(__name__)



@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)


    first_date = session.query(measurements.date).order_by(measurements.date.desc()).first()
    first_date = first_date[0]
    first_date = dt.datetime.strptime(first_date,'%Y-%m-%d')
    

# Calculate the date one year from the last date in data set.

    year_ago = first_date- dt.timedelta(days=366)
    

# Perform a query to retrieve the data and precipitation scores
    prcp_query = session.query(measurements.date,measurements.prcp).\
    filter(func.date(measurements.date) >= year_ago).\
    order_by(measurements.date.desc()).all()


    session.close()

    # Convert list of tuples into normal list
    prcp_results = list(np.ravel(prcp_query))

    return jsonify(prcp_results)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)


    station_query = session.query(station.station).all()

    session.close()

    station_results = list(np.ravel(station_query))

    return jsonify(station_results)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    
    first_date = session.query(measurements.date).order_by(measurements.date.desc()).first()
    first_date = first_date[0]
    first_date = dt.datetime.strptime(first_date,'%Y-%m-%d')
    

# Calculate the date one year from the last date in data set.

    year_ago = first_date- dt.timedelta(days=366)
    

# Perform a query to retrieve 
    active_station = session.query(measurements.station,func.count(measurements.station)).group_by(measurements.station).\
        order_by(func.count(measurements.station).desc()).all()

    most_active_station = active_station[0][0]

    tobs_query = session.query(measurements.date, measurements.tobs).filter(measurements.date >= year_ago).\
        filter(measurements.station == most_active_station).all()

    session.close()

    tobs_results = list(np.ravel(tobs_query))

    return jsonify(tobs_results)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start=None,end=None):
    
    session = Session(engine)
    

    if not end:

        data = session.query(measurements.date, func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
            filter(measurements.date >= start).all()
        stats = list(np.ravel(data))
        return jsonify(stats)

    

    data = session.query(measurements.date, func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
        filter(measurements.date >= start).filter(measurements.date <= end).all()

    stats = list(np.ravel(data))
    return jsonify(stats=stats)


    session.close()



if __name__ == '__main__':
    app.run(debug=True)