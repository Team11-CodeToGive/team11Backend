from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client

bp = Blueprint('event_routes', __name__)
supabase = get_supabase_client()

@bp.route('/', methods=['GET'])
def get_events():
    response = supabase.table('Events').select('*').execute()
    if response.data:
        return jsonify(response.data), 200
    else:
        return jsonify([]), 200

@bp.route('/create', methods=['POST'])
def create_event():
    event_data = request.get_json()
    try:
        response = supabase.table('Events').insert(event_data).execute()
        if len(response.data) > 0:
            return jsonify({"message": "Event created successfully!"}), 201
        else:
            return jsonify({"error": response.error_message}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    response = supabase.table('Events').select('*').eq('event_id', event_id).execute()
    
    if response.data:
        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "Event not found"}), 404

@bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided to update"}), 400
    
    response = supabase.table('Events').update(data).eq('event_id', event_id).execute()

    if response.data:
        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "Event not found or no fields updated"}), 404

    

@bp.route('/<int:event_id>', methods=['DELETE'])
def cancel_event(event_id):
    response = supabase.table('Events').delete().eq('event_id', event_id).execute()

    if response.data:
        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "Event not found or could not be deleted"}), 404
    