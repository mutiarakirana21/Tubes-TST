from flask import Flask, jsonify, request, make_response, render_template, url_for, redirect, session
from flask_mysqldb import MySQL
import jwt #Json Web Token
import datetime #buat make sure token expires dlm bbrp waktu
from functools import wraps
import bcrypt



app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'untuktst'
app.config['MYSQL_PORT'] = 4306
app.config['MYSQL_PASSWORD'] = 'tst2022'
app.config['MYSQL_DB'] = 'data harga properti'
 
mysql = MySQL(app)

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
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO user (name, username, password) VALUES (%s, %s, %s)", (request.form['name'], request.form['username'], hash_password))
    mysql.connection.commit()
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

        cursor = mysql.connection.cursor()
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
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO rumah123_housing_data (property_title, property_agent, location, latitude, longitude, phone_number, property_type, land_area, building_area, price_idr, num_bathroom, num_bedroom, garage_capacity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",  (str(data['title']), data['agent'], data['location'], str(data['lat']), str(data['long']), str(data['num']), data['type'], str(data['land_area']), str(data['build_area']), str(data['price']), str(data['bathroom']), str(data['bedroom']), str(data['garage']))) #post alias insert into
        mysql.connection.commit()
        cursor.close()
        return "200 OK"
    return render_template("create.html")

#read
@app.route("/read", methods = ['GET'])
def read():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM rumah123_housing_data") #get alias select
    result = cursor.fetchall()
    return jsonify(result)

#update
@app.route("/update", methods = ['GET', 'POST', 'PUT'])
def update():
    if request.method == 'POST':
        data = request.form
        cursor = mysql.connection.cursor()
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
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM rumah123_housing_data WHERE property_title = %s", (data['title'],)) #delete alias delete from lalaala where
        mysql.connection.commit()
        cursor.close()
        return "Data Deleted!!"
    return render_template("delete.html")

if __name__ == '__main__':
    app.run(debug=True)
