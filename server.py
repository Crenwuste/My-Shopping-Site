from flask import Flask, request, render_template, redirect, session, url_for

app = Flask(__name__, static_folder="public")
app.secret_key = "supersecretkey!"

# Configuratii utilizatori
ALLOWED_USERS = {
    "test": "test123",
}

DATABASE_FILE = "database.txt"

# Lista de produse
products = [
    {
        "id": "1", 
        "name": "Frigider Samsung", 
        "description": "Frigider cu două uși, clasă energetică A++", 
        "price": 2499, 
        "image": "public/images/produse/frigider.jpg"
    },
    {
        "id": "2", 
        "name": "Mașină de spălat LG", 
        "description": "Capacitate 8kg, 1400 rpm, tehnologie AI Direct Drive", 
        "price": 1899, 
        "image": "public/images/produse/masina_spalat.jpg"
    },
    {
        "id": "3", 
        "name": "Friteuza Tesla AF701BX", 
        "description": "Capacitate 7L, 1700W, Panou digital", 
        "price": 9999, 
        "image": "public/images/produse/friteuza.jpg"
    },
    {
        "id": "4", 
        "name": "Cuptor cu microunde UD", 
        "description": "Capacitate de pana la 20 de litri", 
        "price": 369, 
        "image": "public/images/produse/cuptor.jpg"
    },
    {
        "id": "5", 
        "name": "Espressor Miele CM 7750", 
        "description": "LOV COFFEE", 
        "price": 4677, 
        "image": "public/images/produse/espresor.jpg"
    },
    {
        "id": "6", 
        "name": "Aer condiționat Tesla 12000 BTU", 
        "description": "Clasa A++, Funcție încălzire", 
        "price": 1290, 
        "image": "public/images/produse/aer_conditionat.jpg"
    }
]

# ==============================================
# FUNCTII UTILITARE
# ==============================================

def read_database(filename):
    """Citește detalii cont din fișier"""
    try:
        with open(filename, "rt") as f:
            return {
                "first_name": f.readline().strip(),
                "last_name": f.readline().strip(),
                "phone": f.readline().strip(),
                "address": f.readline().strip()
            }
    except FileNotFoundError:
        return None

def write_database(filename, first_name, last_name, phone, address):
    """Scrie detalii cont în fișier"""
    with open(filename, "wt") as f:
        f.write(f"{first_name}\n{last_name}\n{phone}\n{address}\n")

def save_order_to_file(order_data):
    """Salvează comanda în fișier"""
    # Scriem comanda în fisier
    with open("orders.txt", "a") as f:
        f.write("\n========================================\n")
        f.write("\nDetalii client:\n")
        f.write(f"Nume complet: {order_data['customer']['full_name']}\n")
        f.write(f"Email: {order_data['customer']['email']}\n")
        f.write(f"Telefon: {order_data['customer']['phone']}\n")
        f.write(f"Adresă: {order_data['customer']['address']}\n")
        f.write(f"Metodă de plată: {order_data['customer']['payment_method']}\n")
        
        f.write("\nProduse comandate:\n")
        for product in order_data['products']:
            f.write(f"- {product['name']} x {product['quantity']} = {product['price'] * product['quantity']} RON\n")
        
        f.write(f"\nTotal comandă: {order_data['total']} RON\n")
        f.write("========================================\n")

# ==============================================
# RUTE PRINCIPALE
# ==============================================
@app.route('/')
def index():
    """Pagina principală cu produse"""
    return render_template("index.html", products=products)

@app.route("/second")
def second():
    """Pagina secundară"""
    return render_template("second.html")

# ==============================================
# AUTENTIFICARE
# ==============================================
@app.route("/login", methods=["GET", "POST"])
def login():
    """Gestionare autentificare"""
    if session.get("authenticated"):
        return redirect(url_for("index"))

    error_msg = None
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
            session["authenticated"] = True
            session["username"] = username
            return redirect(url_for("index"))
        else:
            error_msg = "Invalid username or password"
    
    return render_template("login.html", error_msg=error_msg)

@app.route("/logout")
def logout():
    """Deconectare utilizator"""
    session.clear()
    return redirect(url_for("index"))

@app.route("/account-details", methods=["GET", "POST"])
def account_details():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if write_database(DATABASE_FILE, first_name, last_name, phone, address):
            return redirect(url_for("account_details"))
        else:
            return render_template("account-details.html",
                                error_msg="Failed to save data",
                                account_data={"first_name": first_name,
                                            "last_name": last_name,
                                            "phone": phone,
                                            "address": address})

    account_data = read_database(DATABASE_FILE)
    return render_template("account-details.html", account_data=account_data)

# ==============================================
# COS DE CUMPARATURI
# ==============================================
@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Adăugare produs în coș"""
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    session['cart'] = cart
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    """Vizualizare coș"""
    cart_items = session.get('cart', {})
    products_in_cart = []
    subtotal = 0
    shipping_cost = 15
    
    for product_id, quantity in cart_items.items():
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            product_total = product['price'] * quantity
            products_in_cart.append({
                'id': product_id,
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': quantity,
                'total': product_total
            })
            subtotal += product_total
    
    total = subtotal + shipping_cost
    
    return render_template('cart.html',
                         products=products_in_cart,
                         subtotal=subtotal,
                         shipping_cost=shipping_cost,
                         total=total,
                         cart_count=sum(cart_items.values()))

@app.route('/remove_from_cart/<product_id>')
def remove_from_cart(product_id):
    """Ștergere produs din coș"""
    if 'cart' not in session:
        session['cart'] = {}
    
    if product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True
            
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET'])
def checkout():
    # Verificam daca cosul este gol
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('view_cart'))
    
    # Calculam totalurile
    cart_items = session['cart']
    products_in_cart = []
    subtotal = 0
    
    for product_id, quantity in cart_items.items():
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            product_total = product['price'] * quantity
            products_in_cart.append({
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'total': product_total
            })
            subtotal += product_total
    
    shipping_cost = 15
    total = subtotal + shipping_cost
    
    return render_template('checkout.html',
                         products=products_in_cart,
                         subtotal=subtotal,
                         shipping_cost=shipping_cost,
                         total=total)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    # Verificam daca cosul exista
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('view_cart'))
    
    # Procesam datele formularului
    order_data = {
        'customer': {
            'full_name': request.form.get('full_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'payment_method': request.form.get('payment_method')
        },
        'products': [],
        'total': float(request.form.get('total', 0))
    }
    
    # Adaugam produsele
    for product_id, quantity in session['cart'].items():
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            order_data['products'].append({
                'id': product_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity
            })
    
    # Salvam comanda în fișier
    save_order_to_file(order_data)
    
    # Stergem coșul
    session.pop('cart', None)
    
    return redirect(url_for('order_confirmation'))

@app.route('/order-confirmation')
def order_confirmation():
    return render_template('order_confirmation.html')

# ==============================================
# FUNCTII TEMPLATE SI EROARE
# ==============================================
@app.context_processor
def inject_template_vars():
    """Variabile disponibile în toate template-urile"""
    return {
        "authenticated": session.get("authenticated", False),
        "username": session.get("username", ""),
        "cart_count": sum(session.get('cart', {}).values())
    }

@app.errorhandler(404)
def error404(error):
    """Pagina de eroare 404"""
    return render_template("404.html",
                        authenticated=session.get("authenticated", False),
                        username=session.get("username", "")), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)