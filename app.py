import os
import re
import json
import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for

load_dotenv()
por_api_key = os.getenv("POR_API_KEY")

app = Flask(__name__)

def format_date(date_str):
    try:
        # Trim unexpected characters
        clean_date = date_str[:8]  # Only take the first 6 characters
        return datetime.strptime(clean_date, "%m%d%Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str 
    
def create_contact(data):
    contact = {
        'Name': f"{data['first_name']} {data['last_name']}",
        'Identifiers': {
            'DriversLicense': data['license_number'],
            'ParentId': data['parent_id']
        },
        'Title': 'Driver',
    }
    
    return contact

# Mock barcode decoding function
def decode_barcode(barcode_data):
    # Relevant data re patterns
    re_patterns = {
        'first_name': r'DAC(.*?)DDFN',
        'last_name': r'DCS(.*?)DDEN',
        'dob': r'DBB(\d{8})',
        'license_number': r'DAQ(.*?)DCS',
        'date_issued': r'DBD(\d{8})',
        'expiration_date': r'DBA(\d{8})',
        'address': r'DAG(.*?)DAI',
        'city': r'DAI(.*?)DAJ',
        'state': r'DAJ(.*?)DAK',
        'zip': r'DAK(\d{5})',
        'sex': r'DBC(\d)',
    }

    # Decode string
    data = {}

    for key, pattern in re_patterns.items():
        match = re.search(pattern, barcode_data)
        if match:
            data[key] = match.group(1)
            
            if key == 'address':
                # Remove trailing whitespace
                data[key] = data[key].strip()
                data['address'] = str(data['address']+'\n')    
            
            # Format dates to YYYY-MM-DD
            if key in ['dob', 'date_issued', 'expiration_date']:
                value = match.group(1)
                # Convert YYMMDD to YYYY-MM-DD
                value = format_date(value)
                
                data[key] = value
            
    return data

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    barcode_data = request.json.get('barcode')
    if not barcode_data:
        return jsonify({"error": "No barcode data provided"}), 400
    decoded_data = decode_barcode(barcode_data)
    return jsonify(decoded_data)

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # form_data = request.form
        form_data_json = request.json
        
        # Create contact api post data
        contact = {
            'Name': f"{form_data_json['first_name']} {form_data_json['last_name']}",
            'Title': 'Driver',
            'Identifiers': {
                'DriversLicense': form_data_json['license_number'],
                'ParentId': form_data_json['customer_number']
            },
        }
        
        # Headers dict required for api post
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': por_api_key,
        }
        
        # Url for api post
        url ='https://api.pointofrental.com/v1/apikey/contacts'
        
        # Save data to sqlite db
        conn = sqlite3.connect('Contacts.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS Contacts (first_name TEXT, last_name TEXT, license_number TEXT, parent_id TEXT, date_issued TEXT, expiration_date TEXT, address TEXT, city TEXT, state TEXT, zip TEXT)')
        
        c.execute('INSERT INTO Contacts (first_name, last_name, license_number, parent_id, date_issued, expiration_date, address, city, state, zip) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (form_data_json['first_name'], form_data_json['last_name'], form_data_json['license_number'], form_data_json['customer_number'], form_data_json['date_issued'], form_data_json['expiration_date'], form_data_json['address'], form_data_json['city'], form_data_json['state'], form_data_json['zip']))
        
        conn.commit()
        
        conn.close()
        
        # return jsonify({"status": "success", "response": contact})
        
        # Post data to api
        response = requests.post(url, headers=headers, json=contact)
        if response.status_code == 201:
            return jsonify({"status": "success", "response": contact})
        else:
            return f'Error:, {response.status_code}, {response.text}'


if __name__ == "__main__":
    app.run(debug=False)
