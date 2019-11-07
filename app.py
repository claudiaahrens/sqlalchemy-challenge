import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy

from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# setup datebase
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# setup flask
app = Flask(__name__)

# ORM setup
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# ROUTES
@app.route('/')
def home():
    return """ <h1>Hawaii Climate API</h1>
        <h3>Routes to Use</h3>
        <ul>
            <li>/api/v1.0/precipitation</li>
            <li>/api/v1.0/stations</li>
            <li>/api/v1.0/tobs</li>
            <li>/api/v1.0/temp/{start}</li>
            <li>/api/v1.0/temp/{start}/{end}</li>
        </ul>"""

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Returns precipitation data for the past year"""
    # Create our session (link) from Python to the DB
    # Fix issue with accessing SQLite3 on different threads
    # https://www.reddit.com/r/learnpython/comments/5cwx34/flask_sqlite_error/
    session = Session(engine)

    # Find most recent date in the dataset
    result = session.query(func.max(Measurement.date))[0]
    max_date = result[0]
    last_date = dt.datetime.strptime(max_date, '%Y-%m-%d')

    # Calculate one year ago from the most recent date
    last_year = last_date - dt.timedelta(days=365)

    # Query for results
    results = session.query(Measurement.date, Measurement.prcp).filter(
                        Measurement.date >= last_year).filter(
                        Measurement.date <= last_date).all()

    # Convert results to dictionary
    precipitation = {}
    for result in results:
        (date, prcp) = result
        precipitation[date] = prcp

    # Close the session
    session.close()

    return jsonify({'precipitation': precipitation})

@app.route('/api/v1.0/stations')
def stations():
    """Returns all the station names"""
    # Create our session (link) from Python to the DB
    # Fix issue with accessing SQLite3 on different threads
    # https://www.reddit.com/r/learnpython/comments/5cwx34/flask_sqlite_error/
    session = Session(engine)

    # Query for the result
    results = session.query(Station.name,).group_by(Station.name).all()
    stations = []
    for result in results:
        name = result[0]
        stations.append(name)
    
     # Close the session
    session.close()
    
    return jsonify({'stations': stations})

@app.route('/api/v1.0/tobs')
def tobs():
    """Returns temperature data for the past year"""
    # Create our session (link) from Python to the DB
    # Fix issue with accessing SQLite3 on different threads
    # https://www.reddit.com/r/learnpython/comments/5cwx34/flask_sqlite_error/
    session = Session(engine)

    # Find most recent date in the dataset
    result = session.query(func.max(Measurement.date))[0]
    max_date = result[0]
    max_date = dt.datetime.strptime(max_date, '%Y-%m-%d')

    # Calculate one year ago from the most recent date
    last_year = max_date - dt.timedelta(days=365)

    # Query for results
    results = session.query(Measurement.date, Measurement.tobs).filter(
                        Measurement.date >= last_year).filter(
                        Measurement.date <= max_date).filter(
                        Measurement.station == 'USC00519281').all()

    # Convert results to dictionary
    tobs = {}
    for result in results:
        (date, tob) = result
        tobs[date] = tob

    # Close the session
    session.close()

    return jsonify({'USC00519281' : tobs})

@app.route('/api/v1.0/temp/<start>', defaults={'end': None})
@app.route('/api/v1.0/temp/<start>/<end>')
def temperatures(start, end):
    """Return TMIN, TAVG, TMAX from a starting date, or between two dates"""
    # Create our session (link) from Python to the DB
    # Fix issue with accessing SQLite3 on different threads
    # https://www.reddit.com/r/learnpython/comments/5cwx34/flask_sqlite_error/
    session = Session(engine)

    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    query = query.filter(Measurement.date >= start)

    if end is not None:
        query = query.filter(Measurement.date <= end)
    
    # Execute the query
    results = query.all()
    (tmin, tavg, tmax) = results[0]
    session.close()

    return jsonify({'temperature_min' : tmin, 'temperature_avg' : tavg, 'temperature_max' : tmax})

# run app
if __name__ == '__main__':
    app.run()