import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references
Measurement = Base.classes.measurement
Stations = Base.classes.station



# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    return (
    f"<h2>Hawaii Climate App</h2><br/>"
    f"Routes:<br/>"
    f"<ul><li>Precipitation - <code>/api/v1.0/precipitation</code></li></ul>"
    f"<ul><li>Stations - <code>/api/v1.0/stations</code></li></ul>"
    f"<ul><li>Temperature Observations - <code>/api/v1.0/tobs</code></li></ul>"
    f"<ul><li>Calculated Temperatures (Single Date) - <code>/api/v1.0/start</code></li></ul>"
    f"<ul><li>Calculated Temperatures (Dual Dates) - <code>/api/v1.0/start/end</code></li></ul>"
    f""
    f"The <b>Calculated Temperatures</b> route will return the minimum, maximum, and average temperatures of the date range given. "
    f"<br>If a single date is given, temperatures will be calculated for all dates equal to or greater than the date given. "
    f"<br>If two dates are given, temperatures will be calculated for all dates between the two given (inclusive). "
    f"<br>To use these routes, replace <code>start</code> and <code>end</code> with dates in YYYY-MM-DD format.")


# 1) Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query dates and precipitation
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary using 'date' as the key and 'prcp' as the value
    precip_list = []

    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        precip_list.append(precip_dict) 

    session.close()

    # Return the list of dates and precipitation
    return jsonify(precip_list)
    


# 2) Stations Route
@app.route("/api/v1.0/stations")
def stations():
    
    # Query all distinct stations
    session = Session(engine)
    results = session.query(Measurement.station).distinct().all()
    
    # Store results as a list
    station_list = list(np.ravel(results))

    session.close()

    # Return a list of all distinct stations
    return jsonify(station_list)



# 3) Temperature Observation Routes
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Query all dates
    session = Session(engine)
    dates = session.query(Measurement.date).all()
    
    # Extract and store the start and end dates of one year's data
    last_date = dates[-1][0]
    end_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    end_date = end_date.date()
    start_date = end_date - dt.timedelta(days=365)
    
    # Query one year's worth of temperature observations
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=start_date).filter(Measurement.date<=end_date).all()
    
    # Create a dictionary using 'date' as the key and 'tobs' as the value
    tobs_list = []

    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict) 

    session.close()

    # Return the list of dates and temperature observations
    return jsonify(tobs_list)



# 4) temp min, max, and avg with only start date
@app.route("/api/v1.0/<start>")
def start(start):
    
    # Query dates and temperature observations
    session = Session(engine)

     # Select first and last dates of the data set
    date_start = session.query(func.min(Measurement.date)).first()[0]
    date_end = session.query(func.max(Measurement.date)).first()[0]

    # Calculate temperatures if the input date is in the data set
    if start >= date_start and start <= date_end:
        calc_temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= date_end).all()[0]
    
        return (
            f"Min temp: {calc_temps[0]}</br>"
            f"Max temp: {calc_temps[1]}</br>"
            f"Avg temp: {calc_temps[2]}")
    
    else:
        return jsonify({"error": f"The date {start} was not found. Please select a date between 2010-01-01 and 2017-08-23."}), 404



# 5) temp min, max, and avg with start and end dates
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    # Query dates and temperature observations
    session = Session(engine)

    # Select first and last dates of the data set
    date_start = session.query(func.min(Measurement.date)).first()[0]
    date_end = session.query(func.max(Measurement.date)).first()[0]

    # Calculate temperatures if the input dates are in the data set
    if start >= date_start and end <= date_end:
        calc_temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()[0]
    
        return (
            f"Min temp: {calc_temps[0]}</br>"
            f"Max temp: {calc_temps[1]}</br>"
            f"Avg temp: {calc_temps[2]}")
    
    else:
        return jsonify({"error": f"The dates {start} or {end} were not found. Please select dates between 2010-01-01 and 2017-08-23."}), 404
            

if __name__ == "__main__":
    app.run(debug=True)
