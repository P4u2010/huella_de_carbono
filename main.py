from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para almacenar tarjetas (cards)
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    waste_kg = db.Column(db.Float, nullable=False)  # Campo para kilos de basura
    co2_emission = db.Column(db.Float, nullable=False)  # Campo para las emisiones de CO2 calculadas

    def __repr__(self):
        return f'<Card {self.id}>'

# Modelo para almacenar usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Ruta para la página principal
@app.route('/', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
        users_db = User.query.all()
        for user in users_db:
            if form_login == user.login and form_password == user.password:
                return redirect('/index')
        else:
            error = 'Nombre de usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

# Ruta para el registro de usuarios
@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        login = request.form['email']
        password = request.form['password']
        user = User(login=login, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    else:    
        return render_template('registration.html')

# Ruta para la página principal
@app.route('/index')
def index():
    cards = Card.query.order_by(Card.id).all()
    return render_template('index.html', cards=cards)

# Ruta para mostrar una tarjeta
@app.route('/card/<int:id>')
def card(id):
    card = Card.query.get(id)
    return render_template('card.html', card=card)

# Ruta para crear una tarjeta
@app.route('/create')
def create():
    return render_template('create_card.html')

# Función para calcular el CO2 a partir de los kilos de basura
def calculate_co2(waste_kg):
    co2_per_kg = 0.7  # 700 gramos de CO2 por cada kilo de basura
    return waste_kg * co2_per_kg

# Formulario para crear una tarjeta con kilos de basura y calcular el CO2
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    if request.method == 'POST':
        title =  request.form['title']
        subtitle =  request.form['subtitle']
        waste_kg = float(request.form['waste_kg'])  # Convertir a float los kilos de basura

        # Calcular el CO2
        co2_emission = calculate_co2(waste_kg)

        # Creación de un objeto que se enviará a la base de datos
        card = Card(title=title, subtitle=subtitle, waste_kg=waste_kg, co2_emission=co2_emission)

        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create_card.html')

# Ruta para eliminar una tarjeta
@app.route('/delete_card/<int:id>', methods=['POST'])
def delete_card(id):
    card_to_delete = Card.query.get_or_404(id)
    
    try:
        db.session.delete(card_to_delete)
        db.session.commit()
        return redirect('/index')
    except:
        return "Hubo un problema al eliminar la tarjeta"

if __name__ == "__main__":
    app.run(debug=True)
