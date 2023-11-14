# Import the dependencies.
import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# Creating Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value. Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    new_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= new_date).all()
    
    
    precipitation_dict = {str(date): prcp for date, prcp in results}
    
    return jsonify(precipitation_dict)
# 3, /api/v1.0/stations, Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    active_station_data = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    stations_list = [{"Station": station, "Count": count} for station, count in active_station_data]

    return jsonify(stations_list)
    

# 4, /api/v1.0/tobs,Query the dates and temperature observations of the most-active station for the previous year of data. Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = 'USC00519281'
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= '2016-08-23').all()
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in results]
    return jsonify(temperature_list)

# 5, /api/v1.0/<start> and /api/v1.0/<start>/<end>, Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range. For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date. For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")

def get_temps_start(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)


#S Start to end date

@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)



if __name__ == '__main__':
    app.run(debug=True)





    


