from flask import Flask, jsonify, request, make_response, render_template, url_for, redirect, session
from flask_mysqldb import MySQL
import jwt #Json Web Token
import datetime #buat make sure token expires dlm bbrp waktu
from functools import wraps
import bcrypt
import json
from mysql.connector import connect
import os
import time


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'untuktst'
app.config['MYSQL_PORT'] = 3301
app.config['MYSQL_PASSWORD'] = 'tst2022'
app.config['MYSQL_DB'] = 'datahargaproperti'
 
if os.getenv('IS_DEPLOYED') is not None:
    config = {
        'user': 'untuktst',
        'password': 'tst2022',
        'host': 'mysqldb',
        'port': '3306',
        'database': 'datahargaproperti'
    }
else:
    config = {
        'user' : 'untuktst',
        'password': 'tst2022',
        'host': 'localhost',
        'port': '3301',
        'database': 'datahargaproperti'
    }

print(config)
mysql = MySQL(app)
mydb = connect(**config)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
    # cursor = mysql.connection.cursor()
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO user (name, username, password) VALUES (%s, %s, %s)", (request.form['name'], request.form['username'], hash_password))
    # mysql.connection.commit()
    mydb.commit()
    session['name'] = name
    return redirect(url_for("home"))

app.config['SECRET_KEY'] ='bisatst'
storage = []
# Token Required
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if len(storage) == 0:
            return jsonify({'message':'Token is missing'}),403
        try:
            data = jwt.decode(storage[0],app.config['SECRET_KEY'],algorithms=['HS256'])
        except:
            return jsonify({'message':'Invalid Token'}),403
        return f(*args,**kwargs)
    return decorated
    
#Login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        # cursor = mysql.connection.cursor()
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user!= None :
            if bcrypt.hashpw(password, user[2].encode('utf=8')) == user [2].encode('utf-8'):
                token = jwt.encode({'user':username, 'exp':datetime.datetime.utcnow()+datetime.timedelta(hours=24)},app.config['SECRET_KEY'])
                storage.append(token)
                name = user[1]
                session['name'] = name
                print(f'storage: {storage}')
                return redirect(url_for(".dashboard", token=token))
        else:
            return('Password atau username salah')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html')

@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/create", methods = ['GET','POST'])
def create():
    if request.method == 'POST':
        data = request.form
        # cursor = mysql.connection.cursor()
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO rumah123_housing_data (property_title, property_agent, location, latitude, longitude, phone_number, property_type, land_area, building_area, price_idr, num_bathroom, num_bedroom, garage_capacity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",  (str(data['title']), data['agent'], data['location'], str(data['lat']), str(data['long']), str(data['num']), data['type'], str(data['land_area']), str(data['build_area']), str(data['price']), str(data['bathroom']), str(data['bedroom']), str(data['garage']))) #post alias insert into
        mysql.connection.commit()
        cursor.close()
        return "200 OK"
    return render_template("create.html")

#read
@app.route("/read", methods = ['GET'])
def read():
    # cursor = mysql.connection.cursor()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM rumah123_housing_data") #get alias select
    result = cursor.fetchall()
    return jsonify(result)

#update
@app.route("/update", methods = ['GET', 'POST', 'PUT'])
def update():
    if request.method == 'POST':
        data = request.form
        # cursor = mysql.connection.cursor()
        cursor = mydb.cursor()
        cursor.execute("UPDATE rumah123_housing_data SET property_agent=%s WHERE property_title=%s", (data['agent'], data['title_selected'])) #put alias update, set lalaala
        mysql.connection.commit()
        cursor.close()
        return "200 OK"
    return render_template("update.html")

#delete
@app.route("/delete", methods = ['GET', 'POST', 'DELETE'])
def delete():
    if request.method == 'POST':
        data = request.form
        # cursor = mysql.connection.cursor()
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM rumah123_housing_data WHERE property_title = %s", (data['title'],)) #delete alias delete from lalaala where
        mysql.connection.commit()
        cursor.close()
        return "Data Deleted!!"
    return render_template("delete.html")

@app.route("/api/recommend", methods=["GET", "POST"])
def calc():
    if request.method == "POST":
        budget = int(request.form['budget']) #inget di html nya nama kolom inputnya budget dan ini budget per bulan
        daerah = request.form['daerah']
        lama_tinggal =int(request.form['lama_tinggal']) #dalam tahun

        total_kost = int(request.form['total_kost']) #anggep dari inputan dulu
        kost = [
            {
                "nama_kost": "a"
            },
            {
                "nama_kost": "b"
            },
            {
                "nama_kost": "b"
            }
        ] #dummy
        

        harga = int(budget) * 12 * int(lama_tinggal)
        daerah = "%" + daerah + "%"
        # cursor = mysql.connection.cursor()
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM rumah123_housing_data WHERE price_idr <= %s AND location LIKE %s LIMIT 10", (harga,daerah,))
        row_headers1 = [x[0] for x in cursor.description]
        records = cursor.fetchall()
        total_rumah = len(records)
        cursor.close()

        # cursor = mysql.connection.cursor()
        cursor = mydb.cursor()
        cursor.execute("SELECT price_idr FROM rumah123_housing_data WHERE price_idr >= %s AND location LIKE %s order by price_idr asc LIMIT 1", (harga,daerah,))
        row_headers2 = [x[0] for x in cursor.description]
        rumah_min = cursor.fetchall()[0]
        harga_min_rumah = float(rumah_min[0])
        cursor.close()

        text = ""

        if total_rumah > 0:
            text += "Kamu lebih baik membeli RUMAH."
            text += " Berikut list rumah yang cocok untukmu"
            result = []
            for r in records:
                result.append(dict(zip(row_headers1, r)))
            return render_template("after_recommend.html", text=text, result=json.dumps(result, indent=4))
        elif ((total_rumah <= 0) and (total_kost > 0)):
            text += "Kamu lebih baik menyewa KOS-KOSAN"
            harga_tambah = harga_min_rumah - (budget*12*lama_tinggal)
            harga_tambah_perbulan = harga_tambah / (12*lama_tinggal)
            text += "Jika ingin membeli rumah, kamu perlu menambahkan budget sebesar Rp" + str(harga_tambah_perbulan) + " per bulan."
            text += "\nBerikut list kost yang cocok untukmu : \n"
            return render_template("after_recommend.html", text=text, result=json.dumps(kost, indent=4))
        elif ((total_rumah <= 0) and (total_kost <= 0)):
            text = "Tidak ada yang cocok untuk budget yang diinput"
            return render_template("after_recommend.html", text=text, result=[], header=[])
    return render_template("recomend.html")

@app.route("/mean", methods=["GET"])
def mean():
    # cursor = mysql.connection.cursor()
    cursor = mydb.cursor()
    cursor.execute("SELECT location, avg(price_idr) FROM rumah123_housing_data GROUP BY location")
    result = cursor.fetchall()
    cursor.close()
    return jsonify(result)



@app.route("/api/provider/mean", methods=["GET", "POST"])
def api_mean():
    if request.method == "POST":
        daerah = "%" + request.form['daerah'] + "%"
        # cursor = mysql.connection.cursor()
        cursor = mydb.cursor()
        cursor.execute("SELECT avg(price_idr) FROM rumah123_housing_data WHERE location LIKE %s", (daerah,))
        result = cursor.fetchall()
        return jsonify(result)
    return render_template("provider_mean.html")

@app.route("/api/provider/list", methods = ["GET", "POST"])
def list():
    if request.method == "POST":
        lama_cicil = request.form['lama_cicil']
        daerah = "%" + request.form['daerah'] + "%"
        cicil_pertahun = request.form['cicil_pertahun']
        budget = int(lama_cicil) * int(cicil_pertahun)
        # cursor = mysql.connection.cursor()
        cursor = mydb.cursor()
        cursor.execute("SELECT property_title, property_agent, location, num_bedroom, price_idr FROM rumah123_housing_data WHERE price_idr <= %s AND location LIKE %s", (budget,daerah,)) #get alias select
        result = cursor.fetchall()
        return jsonify(result)
    return render_template("provider_list.html")


if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0", port=5000)
