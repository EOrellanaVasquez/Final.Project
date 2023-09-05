from flask import Flask, jsonify, request
from models import User
import requests
from models import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_migrate import Migrate
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
app.config["SECRET_KEY"] = "123456"  # Mi propia clave secreta
db.init_app(app)


# Configura migraciones
migrate = Migrate(app, db)  # Configura las migraciones

# Configuracion Flask-Admin
admin = Admin(app, name="Admin", template_mode="bootstrap3")
admin.add_view(ModelView(User, db.session))


# validacion de Inicio de Sesion con metodo POST.
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user:
        if check_password_hash(user.password_hash, password):
            # Autenticación exitosa
            logging.info(f"Autenticación exitosa para el usuario: {username}")
            return jsonify({"message": "Autenticación exitosa"})
        else:
            # Autenticación fallida, contraseña incorrecta
            logging.warning(f"Autenticación fallida para el usuario: {username} (contraseña incorrecta)")
    else:
        # Autenticación fallida, usuario no encontrado
        logging.warning(f"Autenticación fallida para el usuario: {username} (usuario no encontrado)")

    # Devuelve un mensaje de error
    return jsonify({"message": "Credenciales incorrectas"}), 401


# Ruta para obtener la lista de usuarios en formato JSON
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()  # Obtén todos los usuarios de la base de datos
    user_list = []  # Crea una lista para almacenar los usuarios en formato JSON

    # Itera sobre los usuarios y crea un diccionario JSON para cada uno
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "mail": user.mail,
            "subscription_date": user.suscription_date.strftime("%Y-%m-%d %H:%M:%S")
            # Asegúrate de formatear la fecha como desees
        }
        user_list.append(user_data)  # Agrega el usuario a la lista

    return jsonify({"users": user_list})  # Devuelve la lista de usuarios en formato JSON




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    with app.app_context():
        db.drop_all()
        db.create_all()
