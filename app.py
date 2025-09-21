
from flask import Flask, render_template, request
import openai

# Set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"  # <-- Replace with your API key

app = Flask(__name__)

# Sample artisan products (you can expand this later)
products = [
    {"id": 1, "name": "Handmade Clay Pot", "price": 250, "description": "Eco-friendly clay pot by local artisans."},
    {"id": 2, "name": "Woven Basket", "price": 500, "description": "Beautiful handwoven basket made from natural fibers."},
    {"id": 3, "name": "Hand-painted Scarf", "price": 750, "description": "Unique scarf painted by local artists."},
]

# Home page
@app.route("/")
def index():
    return render_template("index.html", products=products)

# Product details page
@app.route("/product/<int:product_id>")
def product(product_id):
    product_item = next((p for p in products if p["id"] == product_id), None)
    return render_template("product.html", product=product_item)

# AI assistant endpoint
@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.form["question"]

    # Use OpenAI to generate response
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"You are an AI assistant for a local artisan marketplace. Answer this question: {user_question}",
        max_tokens=150,
        temperature=0.7
    )

    answer = response.choices[0].text.strip()
    return render_template("response.html", question=user_question, answer=answer)

if __name__ == "__main__":
   app.run(debug=True)



# AI assistant endpoint with product recommendation
@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.form["question"]

    # AI prompt includes product data for personalized recommendations
    products_text = "\n".join([f"{p['name']} - {p['description']} (Price: ₹{p['price']})" for p in products])

    prompt = f"""
    You are an AI assistant for a local artisan marketplace. 
    Here are the available products:
    {products_text}

    User question: {user_question}

    1. Give a helpful answer to the user's question.
    2. Suggest 1-3 relevant products from the list if applicable.
    """

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=250,
        temperature=0.7
    )

    answer = response.choices[0].text.strip()
    return render_template("response.html", question=user_question, answer=answer)



# Product search endpoint
@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    matched_products = [p for p in products if query in p["name"].lower() or query in p["description"].lower()]
    return render_template("index.html", products=matched_products)




@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    
    # Filter matching products
    matched_products = [p for p in products if query in p["name"].lower() or query in p["description"].lower()]
    
    # Generate AI recommendations for the search query
    prompt_text = f"""
    You are an AI assistant for a local artisan marketplace.
    Suggest 3 relevant products based on this user search query: "{query}".
    Consider the available products: {products}.
    """
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_text,
        max_tokens=200,
        temperature=0.7
    )
    
    recommendations = response.choices[0].text.strip()
    
    return render_template("index.html", products=matched_products, recommendations=recommendations, search_query=query)




from flask import jsonify

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").lower()
    
    # Filter matching products
    matched_products = [p for p in products if query in p["name"].lower() or query in p["description"].lower()]
    
    # Generate AI recommendations
    prompt_text = f"""
    You are an AI assistant for a local artisan marketplace.
    Suggest 3 relevant products based on this user search query: "{query}".
    Consider the available products: {products}.
    """
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_text,
        max_tokens=200,
        temperature=0.7
    )
    
    recommendations = response.choices[0].text.strip()
    
    return jsonify({
        "matched_products": matched_products,
        "recommendations": recommendations
    })





from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Artisan (User) Model
class Artisan(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Artisan.query.get(int(user_id))




from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"], method="sha256")

        new_user = Artisan(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return "Signup successful! <a href='/login'>Login here</a>"

    return """
    <h2>Signup</h2>
    <form method="POST">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <button type="submit">Signup</button>
    </form>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = Artisan.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return "Login successful! <a href='/add'>Go Add Product</a>"
        else:
            return "Invalid credentials! <a href='/login'>Try again</a>"

    return """
    <h2>Login</h2>
    <form method="POST">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <button type="submit">Login</button>
    </form>
    """

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return "Logged out successfully! <a href='/'>Home</a>"







@app.route("/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]

        new_product = Product(name=name, price=price, description=description)
        db.session.add(new_product)
        db.session.commit()

        return "Product added successfully! <a href='/'>Go Home</a>"

    return """
    <h2>Add New Product</h2>
    <form method="POST">
        Name: <input type="text" name="name"><br>
        Price: <input type="number" name="price"><br>
        Description: <textarea name="description"></textarea><br>
        <button type="submit">Add</button>
    </form>
    """






import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS






class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(300), nullable=False)
    image = db.Column(db.String(200), nullable=True)  # Store image filename




class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(300), nullable=False)
    image = db.Column(db.String(200), nullable=True)
    artisan_id = db.Column(db.Integer, db.ForeignKey("artisan.id"))  # Link to artisan




class Artisan(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    products = db.relationship("Product", backref="artisan", lazy=True)




@app.route("/dashboard")
@login_required
def dashboard():
    artisan_products = Product.query.filter_by(artisan_id=current_user.id).all()
    return render_template("dashboard.html", products=artisan_products)







@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)

    if product.artisan_id != current_user.id:
        return "Unauthorized access!"

    if request.method == "POST":
        product.name = request.form["name"]
        product.price = request.form["price"]
        product.description = request.form["description"]

        # Handle image update
        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            product.image = filename

        db.session.commit()
        return "Product updated successfully! <a href='/dashboard'>Go Back</a>"

    return f"""
    <h2>Edit Product</h2>
    <form method="POST" enctype="multipart/form-data">
        Name: <input type="text" name="name" value="{product.name}"><br>
        Price: <input type="number" name="price" value="{product.price}"><br>
        Description: <textarea name="description">{product.description}</textarea><br>
        Image: <input type="file" name="image"><br>
        <button type="submit">Update</button>
    </form>
    """





@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)

    if product.artisan_id != current_user.id:
        return "Unauthorized access!"

    db.session.delete(product)
    db.session.commit()
    return "Product deleted successfully! <a href='/dashboard'>Go Back</a>"





from flask import session

app.secret_key = "supersecretkey"  # Needed for sessions



@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    product = Product.query.get_or_404(id)

    # Initialize cart if not exists
    if "cart" not in session:
        session["cart"] = []

    # Add product ID to cart
    cart = session["cart"]
    cart.append(product.id)
    session["cart"] = cart

    return f"Added {product.name} to cart! <a href='/cart'>View Cart</a>"




@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    products_in_cart = Product.query.filter(Product.id.in_(cart)).all()
    total = sum([p.price for p in products_in_cart])
    return render_template("cart.html", products=products_in_cart, total=total)




@app.route("/remove_from_cart/<int:id>")
def remove_from_cart(id):
    if "cart" in session:
        cart = session["cart"]
        if id in cart:
            cart.remove(id)
            session["cart"] = cart
    return "Item removed! <a href='/cart'>Go back to Cart</a>"




@app.route("/checkout")
def checkout():
    session.pop("cart", None)  # Clear cart after checkout
    return "Thank you for your purchase! 🎉 <a href='/'>Go Home</a>"




class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    total = db.Column(db.Float, nullable=False)

    # Relationship
    items = db.relationship("OrderItem", backref="order", lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    product = db.relationship("Product")



@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get("cart", [])
    products_in_cart = Product.query.filter(Product.id.in_(cart)).all()
    total = sum([p.price for p in products_in_cart])

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        new_order = Order(customer_name=name, customer_email=email, total=total)
        db.session.add(new_order)
        db.session.commit()

        # Save order items
        for product in products_in_cart:
            order_item = OrderItem(order_id=new_order.id, product_id=product.id, quantity=1)
            db.session.add(order_item)

        db.session.commit()
        session.pop("cart", None)  # Clear cart

        return f"✅ Order placed successfully! Your order ID is {new_order.id}. <a href='/orders'>View Orders</a>"

    return render_template("checkout.html", products=products_in_cart, total=total)




@app.route("/orders")
def orders():
    all_orders = Order.query.all()
    return render_template("orders.html", orders=all_orders)




@app.route("/artisan_orders")
@login_required
def artisan_orders():
    # Get all items where the product belongs to the current artisan
    items = OrderItem.query.join(Product).filter(Product.artisan_id == current_user.id).all()
    return render_template("artisan_orders.html", items=items)




import stripe

# Stripe configuration (replace with your own keys from dashboard)
stripe.api_key = "sk_test_your_secret_key"
PUBLISHABLE_KEY = "pk_test_your_publishable_key"



@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get("cart", [])
    products_in_cart = Product.query.filter(Product.id.in_(cart)).all()
    total = sum([p.price for p in products_in_cart])

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        # Create Stripe Checkout Session
        session_stripe = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": product.name,
                        },
                        "unit_amount": int(product.price * 100),  # in cents
                    },
                    "quantity": 1,
                }
                for product in products_in_cart
            ],
            mode="payment",
            success_url="http://127.0.0.1:5000/payment_success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:5000/cart",
            customer_email=email,
        )

        return redirect(session_stripe.url, code=303)

    return render_template("checkout.html", products=products_in_cart, total=total, key=PUBLISHABLE_KEY)




@app.route("/payment_success")
def payment_success():
    session_id = request.args.get("session_id")
    checkout_session = stripe.checkout.Session.retrieve(session_id)

    # Create Order in Database
    new_order = Order(
        customer_name=checkout_session.customer_details.name or "Guest",
        customer_email=checkout_session.customer_details.email,
        total=checkout_session.amount_total / 100,
    )
    db.session.add(new_order)
    db.session.commit()

    # Link order items
    cart = session.get("cart", [])
    products_in_cart = Product.query.filter(Product.id.in_(cart)).all()
    for product in products_in_cart:
        order_item = OrderItem(order_id=new_order.id, product_id=product.id, quantity=1)
        db.session.add(order_item)

    db.session.commit()
    session.pop("cart", None)

    return f"✅ Payment Successful! Your order ID is {new_order.id}. <a href='/orders'>View Orders</a>"




from flask_mail import Mail, Message

# Email configuration (use your SMTP server or Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Use app password for Gmail

mail = Mail(app)




@app.route("/payment_success")
def payment_success():
    session_id = request.args.get("session_id")
    checkout_session = stripe.checkout.Session.retrieve(session_id)

    # Create Order in DB
    new_order = Order(
        customer_name=checkout_session.customer_details.name or "Guest",
        customer_email=checkout_session.customer_details.email,
        total=checkout_session.amount_total / 100,
    )
    db.session.add(new_order)
    db.session.commit()

    # Link order items
    cart = session.get("cart", [])
    products_in_cart = Product.query.filter(Product.id.in_(cart)).all()
    for product in products_in_cart:
        order_item = OrderItem(order_id=new_order.id, product_id=product.id, quantity=1)
        db.session.add(order_item)
    db.session.commit()

    session.pop("cart", None)

    # ---- Send email to customer ----
    msg_customer = Message(
        subject=f"Order Confirmation #{new_order.id}",
        sender=app.config['MAIL_USERNAME'],
        recipients=[new_order.customer_email],
        body=f"Thank you {new_order.customer_name}!\nYour order #{new_order.id} totaling ${new_order.total} has been placed successfully."
    )
    mail.send(msg_customer)

    # ---- Notify artisans ----
    for product in products_in_cart:
        artisan_email = product.artisan.username + "@example.com"  # Replace with real artisan email
        msg_artisan = Message(
            subject=f"Your product '{product.name}' was sold!",
            sender=app.config['MAIL_USERNAME'],
            recipients=[artisan_email],
            body=f"Your product '{product.name}' has been purchased by {new_order.customer_name}.\nOrder ID: {new_order.id}"
        )
        mail.send(msg_artisan)

    return f"✅ Payment Successful! Your order ID is {new_order.id}. <a href='/orders'>View Orders</a>"




class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)



@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not hasattr(current_user, "is_admin") or not current_user.is_admin:
        return "Access denied!"

    total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
    total_orders = Order.query.count()
    top_products = db.session.query(
        Product.name, db.func.count(OrderItem.id).label("sold")
    ).join(OrderItem).group_by(Product.id).order_by(db.desc("sold")).all()

    return render_template(
        "admin_dashboard.html",
        total_revenue=total_revenue,
        total_orders=total_orders,
        top_products=top_products
    )



