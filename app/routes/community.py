from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client

bp = Blueprint('community_routes', __name__)
supabase = get_supabase_client()

@bp.route('/create', methods=['POST'])
def create_community():
    community_data = request.get_json()
    try:
        response = supabase.table('Community').insert(community_data).execute()
        if len(response.data) >0:
            return jsonify({"message": "Community created successfully!"})
        else:
            return jsonify({"error": response.error_message}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

