# app/routes/debug.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/echo', methods=['POST', 'GET'])
def echo_headers():
    # Return selected info so it prints to browser and server log
    headers = {k: v for k, v in request.headers.items()}
    print("---- DEBUG echo_headers request.headers ----")
    for k,v in headers.items():
        print(k + ":", v)
    print("---- END ----")
    return jsonify({"received_headers": headers}), 200

@debug_bp.route('/protected', methods=['POST'])
@jwt_required()
def debug_protected():
    identity = get_jwt_identity()
    print("---- DEBUG protected get_jwt_identity ----")
    print("identity:", identity)
    print("---- END ----")
    return jsonify({"identity": identity}), 200
