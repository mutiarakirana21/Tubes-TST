from flask import Flask, request, jsonify, render_template, redirect
from flask_mail import Mail,Message
from random import randint
from flask_mysqldb import MySQL

app=Flask(__name__)
mail=Mail(app)

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'untuktst'
app.config['MYSQL_PORT'] = 4306
app.config['MYSQL_PASSWORD'] = 'tst2022'
app.config['MYSQL_DB'] = 'data harga properti'
 
mysql = MySQL(app)

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]='mutiarakiranapd@gmail.com'
app.config['MAIL_PASSWORD']='kjifjnosrarnluwp'                    
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)
otp=randint(000000,999999)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/verify',methods=["POST"])
def verify():
    email=request.form['email']
    msg=Message(subject='OTP', sender='mutiarakiranapd@gmail.com', recipients=[email])
    msg.body=str(otp)
    mail.send(msg)
    return render_template('verify.html')

@app.route('/validate',methods=['POST'])
def validate():
    user_otp=request.form['otp']
    if otp==int(user_otp):
        return render_template("dashboard.html")
    return "<h3>Please Try Again</h3>"

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