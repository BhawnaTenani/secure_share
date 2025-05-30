from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from datastore import USERS, FILES
from helper import reverse_token, allowed_file

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if email in USERS:
        return jsonify({'message': 'User already exists'}), 409

    USERS[email] = {
        'password': password,
        'verified': False,
        'type': 'client'
    }

    token = reverse_token(email)
    return jsonify({'message': 'Signup successful', 'verify_link': f"/verify/{token}"}), 201

@app.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    email = reverse_token(token)
    if email in USERS:
        USERS[email]['verified'] = True
        return jsonify({'message': 'Email verified'})
    return jsonify({'message': 'Invalid token'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = USERS.get(email)
    if user and user['password'] == password:
        return jsonify({'message': 'Login successful', 'type': user['type']})
    return jsonify({'message': 'Login failed'}), 401

@app.route('/upload', methods=['POST'])
def upload_file():
    user_type = request.form.get('user_type')
    if user_type != 'ops':
        return jsonify({'message': 'Unauthorized'}), 403

    file = request.files.get('file')
    if file and allowed_file(file.filename):
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, file_id + "_" + filename)
        file.save(path)
        FILES[file_id] = {'name': filename, 'path': path}
        return jsonify({'message': 'File uploaded', 'file_id': file_id})
    return jsonify({'message': 'Invalid file type'}), 400

@app.route('/download/<file_id>', methods=['GET'])
def generate_download_link(file_id):
    user_type = request.args.get('user_type')
    if user_type != 'client':
        return jsonify({'message': 'Only client users can download'}), 403
    if file_id not in FILES:
        return jsonify({'message': 'File not found'}), 404

    token = reverse_token(file_id)
    return jsonify({'download-link': f'/access/{token}', 'message': 'success'})

@app.route('/access/<token>', methods=['GET'])
def access_file(token):
    file_id = reverse_token(token)
    if file_id in FILES:
        file = FILES[file_id]
        return jsonify({'filename': file['name'], 'filepath': file['path']})
    return jsonify({'message': 'Invalid or expired link'}), 404

@app.route('/files', methods=['GET'])
def list_files():
    return jsonify({'files': [f['name'] for f in FILES.values()]})

if __name__ == '__main__':
    app.run(debug=True)
