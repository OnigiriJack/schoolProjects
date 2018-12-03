import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

from datetime import datetime

# Ensure environment variable is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded


app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])[0]['cash']
    grand_total = cash
    if cash == 10000:
        return render_template("index.html", cash=usd(cash), grand_total=usd(grand_total))
    else:
        stocks = db.execute(
            "SELECT symbol, price, SUM(stocks) as Stocks, (price * SUM(stocks)) as total FROM histo WHERE userID=:id GROUP BY symbol",
            id=session["user_id"])
        stock_total = db.execute("SELECT (price * SUM(stocks)) as total FROM histo WHERE userID=:id",
                                 id=session["user_id"])[0]['total']
        grand_total = stock_total + cash
        return render_template("index.html", username=session["user_id"], stocks=stocks, cash=usd(cash), grand_total=usd(grand_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        stock = request.form.get("symbol")
        try:
            num_of_shares = int(request.form.get("shares"))
        except:
            return apology("must be a number")

        stockinfo = lookup(stock)

        cash = db.execute("SELECT cash FROM users WHERE id=:id",
                          id=session["user_id"])[0]['cash']

        if not lookup(stock) or not stock or stock == None:
            return apology("INVALID STOCK", 400)
        elif num_of_shares < 0:
            return apology("stock less than 0", 400)
        elif num_of_shares * stockinfo['price'] > cash:
            return apology("insufficent funnds :(", 400)
        else:
            total = num_of_shares * stockinfo['price']
            db.execute("UPDATE users SET cash = cash - :total WHERE id=:id", id=session["user_id"], total=total)
            db.execute("INSERT INTO histo (userID, symbol, price, stocks) VALUES(:userID, :symbol, :price, :stocks)",
                       userID=session["user_id"], symbol=stock, price=stockinfo['price'], stocks=num_of_shares)
            return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    stocks = db.execute("SELECT * FROM histo WHERE userID=:id", id=session["user_id"])
    return render_template("history.html", username=session["user_id"], stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        stock = request.form.get("symbol")
        if not lookup(stock) or not stock:
            return apology("INVALID STOCK", 400)
        else:
            stockinfo = lookup(stock)
            return render_template("quoted.html", stock=stockinfo['symbol'], price=usd(stockinfo['price']))
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # ensure passwords match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Passwords must match", 400)

        # Add user to data base with insert request
        insert_user_query = "INSERT INTO users (username,hash) VALUES(:username, :hash)"

        result = db.execute(insert_user_query,
                            username=request.form.get("username"),
                            hash=generate_password_hash(request.form.get("password"),
                                                        method='pbkdf2:sha256', salt_length=8))
        if not result:
            return apology("invalid", 400)
        # keep user logged in
        session["user_id"] = result
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        stock = request.form.get("symbol")
        try:
            num_of_shares = int(request.form.get("shares"))
        except:
            return apology("must be a number")

        stocks = db.execute("SELECT symbol, SUM(stocks) as total FROM histo WHERE userID=:id GROUP BY symbol",
                            id=session["user_id"])[0]['total']
        stockinfo = lookup(stock)
        total = num_of_shares * stockinfo['price']
        cash = db.execute("SELECT cash FROM users WHERE id=:id",
                          id=session["user_id"])[0]['cash']

        if not lookup(stock):
            return apology("INVALID STOCK", 400)
        elif num_of_shares < 0:
            return apology("Negative shares", 400)
        elif num_of_shares > stocks:
            return apology("You do not have that many shares", 400)
        else:
            # update users cash
            db.execute("UPDATE users SET cash = cash + :total WHERE id=:id", id=session["user_id"], total=total)
            db.execute("INSERT INTO histo (userID, symbol, price, stocks) VALUES(:userID, :symbol, :price, :stocks)",
                       userID=session["user_id"], symbol=stock, price=stockinfo['price'], stocks=-num_of_shares)
            return redirect("/")
    else:
        stocks = db.execute("SELECT symbol, SUM(stocks) as total FROM histo WHERE userID=:id GROUP BY symbol",
                            id=session["user_id"])
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
