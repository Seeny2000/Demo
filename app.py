
from flask import *
from flask_mail import Mail,Message
import random
import sqlite3
from urllib.parse import urlencode
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
# mail
app.config["MAIL_SERVER"]="smtp.gmail.com"
app.config["MAIL_PORT"]=587
app.config["MAIL_USERNAME"]="gouthamanravi2004@gmail.com"
app.config["MAIL_PASSWORD"]="vhlm viik xtff htvx"
app.config["MAIL_USE_TLS"]=True
mail=Mail(app)
app.secret_key="12345678"

conn=sqlite3.connect("tourism.db",check_same_thread=False)
cur = conn.cursor()
conn.execute("CREATE TABLE IF NOT EXISTS Users(username TEXT,email TEXT,password TEXT,phoneno number,age number,gender text)")

# Admin database creation
def get_db_connection():
    conn = sqlite3.connect('tourism.db')
    conn.row_factory = sqlite3.Row  # This will return rows as dictionaries
    return conn

# Create the table (if it doesn't exist)
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute("SELECT * FROM admin WHERE username = ?", ('admin',))
    admin_exists = cursor.fetchone()

    # If the admin does not exist, insert the default admin with a hashed password
    if not admin_exists:
        default_username = 'admin'
        default_password = 'admin123'  # Default password (you can change it)
        hashed_password = generate_password_hash(default_password)
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (default_username, hashed_password))
        print(f"Default admin user created: Username: {default_username}, Password: {default_password}")
    
    conn.commit()
    conn.close()

# creating cart for products
def cart():
    conn=sqlite3.connect("tourism.db",check_same_thread=False)
    cur = conn.cursor()
    conn.execute("CREATE TABLE IF NOT EXISTS cart(country TEXT,place text,duration text,price number)")

# Call the function to create the table when the app starts
create_table()
cart()


# HOME
@app.route("/",methods=["GET","POST"])
def home():
    return render_template("home.html")

# ABOUT
@app.route("/about")
def about():
    return render_template("about.html")

# SIGN-IN
@app.route("/signin",methods=["GET","POST"])
def signin():
    if request.method == "POST":
        username= request.form["username"]

        # password verification criteria....
        password=request.form["password"]
        if len(password)<8:
            return("min 8 character is required ")
        elif not("1" in password or "2" in password or "3" in password or "4" in password or "5" in password or "6" in password or "7" in password or "8" in password or "9" in password or "0" in password):
            return ("min one number is required")
        elif not("!" in password or "@" in password or "$" in password):
            return("min one special character is  required")   
        
        email=request.form["email"]

        # phone no criteria....
        phoneno=request.form["phoneno"]
        if len(phoneno)<10:
            return ("Phone no must contain min 10 numbers")
        
        age=request.form["age"]
        gender=request.form["gender"]
        conn.execute("insert into users values(?,?,?,?,?,?)",(username,email,password,phoneno,age,gender))
        conn.commit()

        return redirect("/")    
    return render_template("signin.html")

# LOGIN
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        cur.execute("select email,password from users where email=? and password=?",(email,password))
        data= cur.fetchall() 
        session["email"]=email   
        print(data)                          
        if data:
            message="Login Successful"
            query_string = urlencode({"Message" : message})
            # otp sending through email for verification
            if "email" in session:
                email=session["email"]
                otp=generateotp()
                msg=Message("OTP VERIFICATION",sender="gouthamanravi2004@gmail.com",recipients=[email])
                msg.body=f"YOUR OTP IS {otp}"
                mail.send(msg)
                session["otp"]=otp
                return render_template("otp.html")
            
            else:
                return "USER NOT IN THE SESSION "
        else:
            message="Login Failed"
            query_string = urlencode({"Message" : message})
            return redirect(url_for("login") + "?" + query_string)
            
    return render_template("login.html")   

def generateotp():
    otp=random.randint(1000,9999)
    return str(otp)

# otp verification
@app.route("/checkotp",methods=["POST"])
def checkotp():
    if "otp" in request.form:
        otp=request.form["otp"]
        if "otp" in session and session["otp"]==otp:
            message="otp verified successfully"
            query_string = urlencode({"message" : message})
            # return redirect(url_for("home") + "?" + query_string)
            return render_template("userpage.html")
        else:
            return "OTP does not match"
        
    else:
        return "No OTP provided"

# Admin login
@app.route("/admin",methods=["GET","POST"])
def adminlogin():  
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return render_template("admindashboard.html")
        else:
            flash('Invalid username or password.', 'error')

        conn.close()

    return render_template('adminlogin.html')

# Admin dashboard
@app.route("/admindashboard",methods=["GET","POST"])
def admindashboard():
    return render_template("admindashboard.html")

# Add Admin
@app.route("/addadmin",methods=["GET","POST"])
def addadmin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert the new user into the database
            cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash('Admin Added Successfully')
            return render_template("admindashboard.html")
        except sqlite3.IntegrityError:
            flash('Admin already exists')
        finally:
            conn.close()

    return render_template('addadmin.html')

# Remove Admin
@app.route("/removeadmin",methods=["GET","POST"])
def removeadmin():
    if 'username' not in session:
        return redirect('/admindashboard')

    logged_in_user = session['username']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all users except the logged-in user
    cursor.execute("SELECT id, username FROM admin WHERE username != ?", (logged_in_user,))
    users = cursor.fetchall()

    if request.method == 'POST':
        user_id = request.form['user_id']
        cursor.execute("DELETE FROM admin WHERE id = ?", (user_id,))
        conn.commit()
        flash('User removed successfully!', 'success')
        return redirect('/removeadmin')

    conn.close()

    return render_template('removeadmin.html', users=users)

# Update admin password using session data
@app.route("/updatepassword", methods=["GET", "POST"])
def updatepass():
    if 'username' not in session:
        return redirect('/admindashboard')

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = ?", (session['username'],))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], old_password):
            hashed_new_password = generate_password_hash(new_password)
            cursor.execute("UPDATE admin SET password = ? WHERE id = ?", (hashed_new_password, user['id']))
            conn.commit()
            flash('Password updated successfully!')
            return redirect('/admindashboard')
        else:
            flash('Old password is incorrect.', 'error')

        conn.close()

    return render_template('updateadminpassword.html')

# Logout admin and clearing session data
@app.route('/logout')
def logout():
    # Remove all session data
    session.pop('username', None)
    flash('Logged out Successfully')
    return redirect(url_for('home'))  # Redirect to Home page
    

# Logout user and clearing session data
@app.route('/userlogout')
def userlogout():
    # Remove all session data
    session.clear()
    print(session)
    flash('Logged out Successfully')
    return redirect(url_for('home'))  # Redirect to Home page

# Route to add an item to the cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Get the item details from the form submission
    item = {
        'country': request.form.get('country'),
        'place': request.form.get('place'),
        'duration': request.form.get('duration'),
        'price': request.form.get('price')
    }
    
    # Initialize the cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    # Add the new item to the cart
    session['cart'].append(item)
    session.modified = True  # Mark session as modified

    return render_template("userpage.html")


# Route to show the cart
@app.route('/cart')
def show_cart():
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart)

# Route to remove an item from the cart
@app.route('/remove_from_cart/<int:cart_item_index>')
def remove_from_cart(cart_item_index):
    cart = session.get('cart', [])
    
    # Ensure the index is valid
    if 0 <= cart_item_index < len(cart):
        cart.pop(cart_item_index)  # Remove the item by index
    
    session['cart'] = cart  # Update the session with the modified cart
    session.modified = True  # Mark session as modified

    return redirect(url_for('show_cart'))

# -----------------------------------------------------------------------------------------------------------------------------


# Route to add an item to the favourites
@app.route('/favourites', methods=['POST'])
def add_to_fav():
    # Get the item details from the form submission
    item = {
        'country': request.form.get('country'),
        'place': request.form.get('place'),
        'duration': request.form.get('duration'),
        'price': request.form.get('price')
    }
    
    # Initialize the cart if it doesn't exist
    if 'fav' not in session:
        session['fav'] = []
    
    # Add the new item to the cart
    session['fav'].append(item)
    session.modified = True  # Mark session as modified

    return render_template("userpage.html")

@app.route('/fav')
def show_fav():
    fav = session.get('fav', [])
    return render_template('fav.html', fav=fav)  # Use 'fav' to match the variable name


# Route to remove an item from the cart
@app.route('/remove_from_fav/<int:fav_item_index>')
def remove_from_fav(fav_item_index):
    fav = session.get('fav', [])
    
    # Ensure the index is valid
    if 0 <= fav_item_index < len(fav):
        cart.pop(fav_item_index)  # Remove the item by index
    
    session['fav'] = fav  # Update the session with the modified cart
    session.modified = True  # Mark session as modified

    return redirect(url_for('show_fav'))





@app.route('/thai')
def thai():
    return "This is the Thai page"



@app.route("/userpage")
def userpage():
    return render_template("userpage.html")



if __name__=="__main__":
    app.run(debug=True)




