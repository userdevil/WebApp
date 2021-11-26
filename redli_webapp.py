from flask import Flask, render_template, request
import requests
import os
import phonenumbers
from phonenumbers import geocoder
app = Flask(__name__)

@app.route('/')
def home():
    ip = request.remote_addr
    return render_template('home.html',count = ip)

@app.route('/helpline')
def help():
    return render_template('help.html')

@app.route('/phtracker')
def ph():
    return render_template('phtracker.html')

@app.route('/track', methods=['POST'])
def track():
    if request.method == 'POST':
        url = request.form['user_url']
        resp = requests.get(url)
        redirect_ulr = resp.history
        return render_template('track.html', endurl = resp, redirect = redirect_ulr)

@app.route('/track1', methods=['POST'])
def track1():
    if request.method == 'POST':
        number = request.form['user_url']
        ch_number = phonenumbers.parse(number, "CH")
        service_provider = phonenumbers.parse(number, "RO")
        location = geocoder.description_for_number(ch_number, "en")
        from phonenumbers import carrier  
        crname = carrier.name_for_number(service_provider, "en")
        return render_template('track1.html',location =ch_number , crname = crname,number=number)


if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
