from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from json import dumps
import os
import logging
from flask import Flask, g, Response, request
from neo4j import GraphDatabase, basic_auth

url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
username = os.getenv("NEO4J_USER", "Daniel_Hurtado")
password = os.getenv("NEO4J_PASSWORD", "123456")
neo4jVersion = os.getenv("NEO4J_VERSION", "4")
database = os.getenv("NEO4J_DATABASE", "taller5")
port = os.getenv("PORT", 8081)

# Create a database driver instance
driver = GraphDatabase.driver(url, auth = basic_auth(username, password))

# Connect to database only once and store session in current context
def get_db():
    if not hasattr(g, "neo4j_db"):
        if neo4jVersion.startswith("4"):
            g.neo4j_db = driver.session(database = database)
        else:
            g.neo4j_db = driver.session()
    return g.neo4j_db

# Close database connection when application context ends

def close_db(error):
    if hasattr(g, "neo4j_db"):
        g.neo4j_db.close()

def serialize_Mascota(mascota):
    return {
        'Nombre': mascota['name'],
        'Mascota': mascota['pet'],
        'Fotografia': mascota['Picture'],
    }
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='Leonardo', password='password'))
users.append(User(id=2, username='Daniel', password='secret'))
users.append(User(id=3, username='David', password='somethingsimple'))


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'somesecretkeythatonlyishouldknow'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))

        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/listarMascotas')
def listar():
    db = get_db()
    results = db.read_transaction(lambda tx: list(tx.run("MATCH (d:Pet) <-[:ACTED_IN]-(i:Picture) "
                                                         "RETURN d.pet as Pet, i.Picture as Fotografia "
                                                         "LIMIT $limit", {
                                                             "limit": request.args.get("limit",
                                                                                       100)})))
    print(results)
    return render_template('listarMascotas.html')

