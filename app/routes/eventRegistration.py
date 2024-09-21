from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client
from .event import get_event, update_event

bp = Blueprint('event_registration_routes', __name__)
supabase = get_supabase_client()

@bp.route('/create', methods=['POST'])
def create_registration():
    registration_data = request.get_json()

    try:
        # Retrieve the event using the event_id
        event_response = supabase.table('Events').select('*').eq('event_id', registration_data['event_id']).execute()

        if event_response.data:
            # If event exists, append user_id to the attendees list
            if is_registered(registration_data):
                return jsonify({"message": "User already registered!"}), 400

            response = supabase.table('EventRegistration').insert(registration_data).execute()

            if response.data:
                return jsonify({"message": "User registered successfully!"}), 201
            else:
                return jsonify({"error": response.error_message}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route('/<int:registration_id>', methods=['DELETE'])
def cancel_registrations(registration_id):
        response = supabase.table('EventRegistration').delete().eq('registration_id', registration_id).execute()

        if response.data:
            return jsonify(response.data[0]), 200
        else:
            return jsonify({"error": "Registration not found or could not be deleted"}), 404
             
def is_registered(resgistration_data):
    '''
    Check if user already registered to event'''
    response = supabase.table('EventRegistration').select('*')\
        .eq('event_id', resgistration_data['event_id'])\
            .eq('user_id', resgistration_data['user_id']).execute()
    
    return len(response.data) > 0