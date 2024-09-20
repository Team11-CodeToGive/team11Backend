from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client

bp = Blueprint('user_routes', __name__)
supabase = get_supabase_client()

@bp.route('/create', methods=['POST'])
def create_user():
    user_data = request.get_json()
    try:
        response = supabase.table('users').insert(user_data).execute()
        if len(response.data) > 0:
            return jsonify({"message": "User created successfully!"}), 201
        else:
            return jsonify({"error": response.error_message}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400
@bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    response = supabase.table('users').select('*').eq('id', user_id).execute()
    
    if response.data:
        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "User not found"}), 404
