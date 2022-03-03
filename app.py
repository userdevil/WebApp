from flask import Flask, render_template, request, flash, redirect, url_for
import sqlite3
from hashids import Hashids
import requests
import os
import phonenumbers
from phonenumbers import geocoder


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

app.config['SECRET_KEY'] = 'this should be a secret random string'

hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])


@app.route('/')
def home():
    ip = request.remote_addr
    return render_template('home.html',count = ip)

@app.route('/helpline')
def help():
    ip = request.remote_addr
    return render_template('help.html',count = ip)

@app.route('/sitemap.html')
def sitemap():
    return render_template('sitemap.html')

@app.route('/sitemap.xml')
def site():
    return render_template('sitemap.xml')

@app.route('/phtracker')
def ph():
    ip = request.remote_addr
    return render_template('phtracker.html',count = ip)

@app.route('/track', methods=['POST'])
def track():
    if request.method == 'POST':
        url = request.form['user_url']
        ip = request.remote_addr
        resp = requests.get(url)
        redirect_ulr = resp.history
        return render_template('track.html', endurl = resp, redirect = redirect_ulr,count = ip)
        print(url)
@app.route('/track1', methods=['POST'])
def track1():
    if request.method == 'POST':
        number = request.form['user_url']
        ip = request.remote_addr
        ch_number = phonenumbers.parse(number, "CH")
        service_provider = phonenumbers.parse(number, "RO")
        location = geocoder.description_for_number(ch_number, "en")
        from phonenumbers import carrier  
        crname = carrier.name_for_number(service_provider, "en")
        return render_template('track1.html',location =ch_number , crname = crname,number=number,count = ip)
        print(number)

@app.route('/shorturl', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()

    if request.method == 'POST':
        ip = request.remote_addr
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))

        url_data = conn.execute('INSERT INTO urls (original_url) VALUES (?)',(url,))
        conn.commit()
        conn.close()

        url_id = url_data.lastrowid
        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid

        return render_template('index.html', short_url=short_url,count = ip)

    return render_template('index.html')
@app.route('/<id>')
def url_redirect(id):
    conn = get_db_connection()

    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = conn.execute('SELECT original_url, clicks FROM urls'
                                ' WHERE id = (?)', (original_id,)
                                ).fetchone()
        original_url = url_data['original_url']
        clicks = url_data['clicks']

        conn.execute('UPDATE urls SET clicks = ? WHERE id = ?',
                     (clicks+1, original_id))

        conn.commit()
        conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))



@app.route('/stats')
def stats():
    conn = get_db_connection()
    db_urls = conn.execute('SELECT id, created, original_url, clicks FROM urls'
                           ).fetchall()
    conn.close()

    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url)

    return render_template('stats.html', urls=urls)

if __name__=='__main__':
    app.run(debug=False,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
