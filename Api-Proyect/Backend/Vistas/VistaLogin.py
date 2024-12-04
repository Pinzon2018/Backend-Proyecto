from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'daniel12345'

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if auth and auth.username == 'usuario' and auth.password == 'contraseña':
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    
    return jsonify({'MEssAGE':'Autenticacion fallida!'}), 401

@app.route('/protegido', methods=['GET'])
def protegido():
    token = request.headers.get('x-access-tokens')
    
    if not token:
        return jsonify({'messagE': 'Token no proporcionado!'}), 401
    
    try: 
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except: 
        return jsonify({'message': 'Token no es valido!'}), 401
    
    return jsonify({'message': 'Ruta protegida!!', 'user':data['user']})

if __name__ == '__main__':
    app.run(debug=True)
