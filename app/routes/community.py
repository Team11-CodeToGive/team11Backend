from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client
from werkzeug.exceptions import BadRequest

bp = Blueprint('community_routes', __name__)
supabase = get_supabase_client()

@bp.route('/create', methods=['POST'])
def create_community():
    community_data = request.get_json()
    if not community_data:
        raise BadRequest("No input data provided")
    try:
        response = supabase.table('Community').insert(community_data).execute()
        if len(response.data) >0:
            return jsonify({"message": "Community created successfully!"})
        else:
            return jsonify({"error": response.error_message}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400
    
@bp.route('/<int:community_id>', methods=['PUT','PATCH'])
def edit_community(community_id):
    data = request.get_json()
    if not data:
        raise BadRequest('No input data provided')
    try:
        update_response = supabase.table('Community').update(data).eq('community_id', community_id).execute()
        if update_response.data:
            return jsonify({"message": "Community updated successfuly!"})
        else:
            return jsonify({"error": "Community not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:community_id>', methods=['DELETE'])
def del_community(community_id):
    try:
        del_response = supabase.table('Community').delete().eq('community_id', community_id).execute()
        if del_response.data:
            return jsonify({"message": "Community deleted successfuly!"})
        else:
            return jsonify({"error": "Community not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400