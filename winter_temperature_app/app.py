from flask import Flask, render_template
from datetime import datetime
import pandas as pd
from meteostat import Point, Daily
import calendar
from scipy import stats
import matplotlib.pyplot as plt

app = Flask(__name__)

# Create Point for Toronto, ON
location = Point(43.6532, -79.3832, 76)

# Function to get meteorological winter data
def get_meteorological_winter_data(year):
    # Winter starts December of previous year
    start = datetime(year - 1, 12, 1)
    # Get last day of February (handles leap years)
    _, last_day = calendar.monthrange(year, 2)
    # Winter ends last day of February of current year
    end = datetime(year, 2, last_day)

    data = Daily(location, start, end)
    return data.fetch()

# Function to get astronomical winter data
def get_astronomical_winter_data(year):
    # Dictionary of winter dates (year: (start_date, end_date))
    winter_dates = {
    2001: ("2000-12-21 08:37", "2001-03-20 02:35"),
    2002: ("2001-12-21 14:21", "2002-03-20 08:31"),
    2003: ("2002-12-21 20:14", "2003-03-20 14:16"),
    2004: ("2003-12-22 02:04", "2004-03-20 20:00"),
    2005: ("2004-12-21 07:42", "2005-03-20 01:49"),
    2006: ("2005-12-21 13:35", "2006-03-20 07:34"),
    2007: ("2006-12-21 19:22", "2007-03-20 13:26"),
    2008: ("2007-12-22 01:08", "2008-03-20 19:07"),
    2009: ("2008-12-21 07:04", "2009-03-20 01:48"),
    2010: ("2009-12-21 12:47", "2010-03-20 07:44"),
    2011: ("2010-12-21 18:38", "2011-03-20 13:32"),
    2012: ("2011-12-22 00:30", "2012-03-20 19:21"),
    2013: ("2012-12-21 06:12", "2013-03-20 01:14"),
    2014: ("2013-12-21 12:11", "2014-03-20 07:02"),
    2015: ("2014-12-21 18:03", "2015-03-20 12:57"),
    2016: ("2015-12-22 00:48", "2016-03-20 18:45"),
    2017: ("2016-12-21 05:44", "2017-03-20 00:30"),
    2018: ("2017-12-21 11:28", "2018-03-20 06:28"),
    2019: ("2018-12-21 17:23", "2019-03-20 12:15"),
    2020: ("2019-12-21 23:19", "2020-03-20 18:58"),
    2021: ("2020-12-21 05:02", "2021-03-19 23:50"),
    2022: ("2021-12-21 10:59", "2022-03-20 05:37"),
    2023: ("2022-12-21 16:48", "2023-03-20 11:33"),
    2024: ("2023-12-21 22:27", "2024-03-20 17:24"),
    2025: ("2024-12-21 04:12", "2025-03-20 13:16")  
}
    
    # Get the winter dates for this year
    start_str, end_str = winter_dates[year]
    start = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
    end = datetime.strptime(end_str, "%Y-%m-%d %H:%M")

    data = Daily(location, start, end)
    return data.fetch()

@app.route('/')
def index():
    # Fetch historical data for both meteorological and astronomical winters
    meteorological_data = {}
    astronomical_data = {}
    
    # Get data for winters from 2001 to 2024 for meteorological
    for year in range(2000, 2024):  # Adjusted to 2023 to match the end year
        data = get_meteorological_winter_data(year)
        if not data.empty:  # Check if data is not empty
            data['winter_year'] = year  # Add year identifier
            meteorological_data[year + 1] = data['tavg'].mean()  # Store average temperature for the following year

    # Get data for winters from 2001 to 2024 for astronomical
    for year in range(2001, 2025):
        data = get_astronomical_winter_data(year)
        if not data.empty:  # Check if data is not empty
            data['winter_year'] = year  # Add year identifier
            astronomical_data[year] = data['tavg'].mean()  # Store average temperature

    # Convert to lists for JSON serialization
    meteorological_labels = list(meteorological_data.keys())
    meteorological_values = list(meteorological_data.values())
    astronomical_labels = list(astronomical_data.keys())
    astronomical_values = list(astronomical_data.values())

    # Define the winter ranges for 2024-2025
    meteorological_winter_2024 = "December 1, 2024 - February 29, 2025"
    astronomical_winter_2024 = "December 21, 2024 - March 20, 2025"

    # Track average temperature for the ongoing winter of 2025
    current_date = datetime.now()
    meteorological_winter_start = datetime(2024, 12, 1)
    astronomical_winter_start = datetime(2024, 12, 21)
    meteorological_winter_end = datetime(2025, 2, 28)
    astronomical_winter_end = datetime(2025, 3, 20)

    # Initialize variables for tracking temperatures
    meteorological_avg_temp_2025 = None
    astronomical_avg_temp_2025 = None
    remaining_days_meteorological = None
    remaining_days_astronomical = None

    # Initialize variables for last year's temperatures
    last_year_meteorological_avg_temp = None
    last_year_astronomical_avg_temp = None
    last_year_meteorological_avg_temp_so_far = None
    last_year_astronomical_avg_temp_so_far = None

    # Check if we are within the meteorological winter range
    if meteorological_winter_start <= current_date <= meteorological_winter_end:
        # Fetch data for the ongoing meteorological winter
        data = get_meteorological_winter_data(2025)
        if not data.empty:
            # Calculate average temperature so far
            days_passed = (current_date - meteorological_winter_start).days + 1
            meteorological_avg_temp_2025 = data['tavg'].mean()
            # Calculate remaining days
            total_days = (meteorological_winter_end - meteorological_winter_start).days + 1
            remaining_days_meteorological = total_days - days_passed

        # Fetch last year's meteorological data for comparison
        last_year_data = get_meteorological_winter_data(2024)
        if not last_year_data.empty:
            last_year_meteorological_avg_temp = last_year_data['tavg'].mean()

            # Calculate last year's average temperature so far
            last_year_days_passed = (current_date - datetime(2023, 12, 1)).days + 1
            if last_year_days_passed > 0:
                last_year_meteorological_avg_temp_so_far = last_year_data['tavg'][:last_year_days_passed].mean()

    # Check if we are within the astronomical winter range
    if astronomical_winter_start <= current_date <= astronomical_winter_end:
        # Fetch data for the ongoing astronomical winter
        data = get_astronomical_winter_data(2025)
        if not data.empty:
            # Calculate average temperature so far
            days_passed = (current_date - astronomical_winter_start).days + 1
            astronomical_avg_temp_2025 = data['tavg'].mean()
            # Calculate remaining days
            total_days = (astronomical_winter_end - astronomical_winter_start).days + 1
            remaining_days_astronomical = total_days - days_passed

        # Fetch last year's astronomical data for comparison
        last_year_data = get_astronomical_winter_data(2024)
        if not last_year_data.empty:
            last_year_astronomical_avg_temp = last_year_data['tavg'].mean()

            # Calculate last year's average temperature so far
            last_year_days_passed = (current_date - datetime(2023, 12, 21)).days + 1
            if last_year_days_passed > 0:
                last_year_astronomical_avg_temp_so_far = last_year_data['tavg'][:last_year_days_passed].mean()

    # Get the average temperature for the previous winter (2024)
    avg_temp_last_year_meteorological = meteorological_data[2024] if 2024 in meteorological_data else None
    avg_temp_last_year_astronomical = astronomical_data[2024] if 2024 in astronomical_data else None

    # Calculate the average temperature needed for the remaining days
    needed_temp_meteorological = None
    needed_temp_astronomical = None

    if meteorological_avg_temp_2025 is not None and avg_temp_last_year_meteorological is not None:
        needed_temp_meteorological = (avg_temp_last_year_meteorological * 90 - meteorological_avg_temp_2025 * (days_passed)) / remaining_days_meteorological if remaining_days_meteorological > 0 else None

    if astronomical_avg_temp_2025 is not None and avg_temp_last_year_astronomical is not None:
        needed_temp_astronomical = (avg_temp_last_year_astronomical * 90 - astronomical_avg_temp_2025 * (days_passed)) / remaining_days_astronomical if remaining_days_astronomical > 0 else None

    return render_template('index.html', 
                           meteorological_labels=meteorological_labels,
                           meteorological_values=meteorological_values,
                           astronomical_labels=astronomical_labels,
                           astronomical_values=astronomical_values,
                           meteorological_winter_2024=meteorological_winter_2024,
                           astronomical_winter_2024=astronomical_winter_2024,
                           meteorological_avg_temp_2025=meteorological_avg_temp_2025,
                           astronomical_avg_temp_2025=astronomical_avg_temp_2025,
                           needed_temp_meteorological=needed_temp_meteorological,
                           needed_temp_astronomical=needed_temp_astronomical,
                           last_year_meteorological_avg_temp=last_year_meteorological_avg_temp,
                           last_year_astronomical_avg_temp=last_year_astronomical_avg_temp,
                           last_year_meteorological_avg_temp_so_far=last_year_meteorological_avg_temp_so_far,
                           last_year_astronomical_avg_temp_so_far=last_year_astronomical_avg_temp_so_far)

if __name__ == '__main__':
    app.run(debug=True)