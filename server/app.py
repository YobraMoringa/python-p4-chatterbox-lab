from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=["GET","POST"])
def messages():
    if request.method == "GET":
        message_objs_list = Message.query.all()
        message_dict_list = [message_obj.to_dict() for message_obj in message_objs_list]
        response = make_response(message_dict_list,200)
        return response
    elif request.method == "POST":
        # get request from client
        request_dict = request.get_json()
        
        # Check whether fields are empty
        for key in request_dict:
            print(request_dict[key])
            if not request_dict[key]:
                error_dict = {
                    'message': f"{key} is empty"
                }
                response = make_response(error_dict, 400)
                return response
        
        new_message_obj = Message(username = request_dict.get("username"), body = request_dict.get("body"))
        db.session.add(new_message_obj)
        db.session.commit()

        new_message_dict = new_message_obj.to_dict()
        response = make_response(new_message_dict, 200)
        return response

@app.route('/messages/<int:id>', methods=["PATCH", "DELETE"])
def messages_by_id(id):
    target_message_obj = Message.query.filter(Message.id==id).first()

    if target_message_obj:
        if request.method == "PATCH":
            print("Hello World")
            # Get changes from client request
            client_changes_dict = request.get_json()

            for key in client_changes_dict:
                updated_value = client_changes_dict[key]
                if not updated_value: #Check for empty fields
                    error_dict = {
                        'message': f"{key} field is empty"
                    }
                    response = make_response(error_dict,400)
                    return response
                else:
                    target_message_obj.body = updated_value
                    db.session.add(target_message_obj)
                    db.session.commit()

                    response_dict = target_message_obj.to_dict()
                    response = make_response(response_dict,200)
                    return response

        elif request.method == "DELETE":
            db.session.delete(target_message_obj)
            db.session.commit()

            message_dict = {
                'message': f"message {id} deleted"
            }
            response = make_response(message_dict,200)
            return response
        else:
            error_dict = {
                'message': "http method is neither patch nor delete"
            }
            response = make_response(error_dict,400)
            return response
    else:
        error_dict = {
            'message': f"id {id} doesn't exist"
        }
        response = make_response(error_dict,400)
        return response

if __name__ == '__main__':
    app.run(port=5555)
