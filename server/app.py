from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import desc

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = []

        for message in Message.query.order_by(desc('created_at')):
            message_dict = message.to_dict()
            messages.append(message_dict)
        
        response = make_response(jsonify(messages), 200)

        return response
    elif request.method == 'POST':
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        if not all([body, username]):
            return jsonify({"message": "Failed to create message"}), 404
        
        new_message=Message(body=body, username=username)
        
        db.session.add(new_message)
        db.session.commit()

        

        response = make_response(jsonify(data), 201)

        return response


@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    if request.method == 'PATCH':
        message = Message.query.filter_by(id = id).first()

        for attr in request.form:
            setattr(message, attr, request.form.get(attr))
        
        message_dict = message.to_dict()

        response = make_response(message_dict, 200)

        return response
    
    elif request.method == "DELETE":
        message = Message.query.filter_by(id = id).first()

        if message is None:
            return jsonify({"message": "Product cant be found"})

        db.session.delete(message)
        db.session.commit()

        response_body = jsonify({"message": "Succesfully deleted item"})

        return make_response(response_body, 200)






if __name__ == '__main__':
    app.run(debug=True, port=5555)
