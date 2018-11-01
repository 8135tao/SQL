
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Setting up database
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
print(Base.classes.keys())
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################



@app.route("/")
def welcome():
    return (
        f"Welcome to the weather API!<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Returns total rainfalls from previous years by station.<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"Returns station name and id.<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Returns temperature observed in stations from previous years<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"Returns the MIN, AVG, and MAX temperatures for dates greater than and equal to the start date.<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Returns the MIN, AVG, and MAX temperatures for dates between the start and end date inclusive.<br/>"
    )
####################################################
#/api/v1.0/precipitation
#Convert the query results to a Dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
####################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for last year"""
# Create our session (link) from Python to the DB
    session = Session(engine)


# Query for the dates and precipitation observations from the last year.
    query_latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(query_latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(365)

    query_date_prcp = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date>=one_year_ago).\
                    order_by(Measurement.date).all()
                                                                    

# convert query result to a dictionary with `date` and `prcp` as the keys and values
    date_prcp = []
    for query_result in query_date_prcp:
        prcp_row = {}
        prcp_row["date"] = query_result[0]
        prcp_row["prcp"] = query_result[1]
        date_prcp.append(prcp_row)
    return jsonify(date_prcp)

####################################################
#/api/v1.0/stations
#Return a JSON list of stations from the dataset.
####################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    query_station_name = session.query(Station.station,Station.name).\
                        group_by(Station.name).all()
    
    #directly covert query result to dictionary and jsonify to return
    return  jsonify( dict(query_station_name) )

    #or do it the same way as above
    # station_name= []
    # for query_result in query_station_name:
    #     sta_name_row={}
    #     sta_name_row["station id"] = query_result[0]
    #     sta_name_row["station name"] = query_result[1]
    #     station_name.append(sta_name_row)
    # return jsonify(station_name)

####################################################
#/api/v1.0/tobs

#query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year.
####################################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    query_date_temp = session.query(Measurement.tobs,Measurement.date).\
                        order_by(Measurement.date).\
                        filter(Measurement.date>=one_year_ago).all()
    
    date_temp_df = pd.DataFrame(query_date_temp,columns=['temp observed','date'])
    date_temp_df.set_index('date',inplace=True)

    return jsonify(date_temp_df.to_dict())


####################################################
#/api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
####################################################
@app.route("/api/v1.0/<start>")
def tempstart(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    try:
        start_date= dt.datetime.strptime(start, '%Y-%m-%d')
        query_normals = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                                filter(Measurement.date >= start_date)
        normals={}
        normals['date start'] = start_date
        normals['temp min'] = list(query_normals)[0][0]
        normals['temp avg'] = list(query_normals)[0][1]
        normals['temp max'] = list(query_normals)[0][2]
        return jsonify( normals )
    except:
        return f"please enter the date in the form Y-m-d, example (2017-01-01)"

####################################################
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
####################################################
@app.route("/api/v1.0/<start>/<end>")
def tempstartend(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    try:
        start_date= dt.datetime.strptime(start, '%Y-%m-%d')
        end_date= dt.datetime.strptime(end, '%Y-%m-%d')

        query_normals = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
        normals={}
        normals['date start'] = start_date
        normals['date end'] = end_date
        normals['temp min'] = list(query_normals)[0][0]
        normals['temp avg'] = list(query_normals)[0][1]
        normals['temp max'] = list(query_normals)[0][2]
        return jsonify( normals )
    except:
        return f"please enter the date in the form Y-m-d, example (2017-01-01)"



if __name__ == "__main__":
    app.run(debug=True)
