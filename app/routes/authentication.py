from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="5b3ce3597851110001cf62481ce24ea21f7847f7a5ffedc7f1eac56c")
bp = Blueprint('user_routes', __name__)
supabase = get_supabase_client()

@bp.route('/create', methods=['POST'])
def create_user():
    user_data = request.get_json()
    location_geocode = geolocator.geocode(user_data["location"]["address"])
    if location_geocode is None:
        return jsonify({"error" : "Invalid location address"})
    user_data['location']['latitude'] = location_geocode.latitude
    user_data['location']['longitude'] = location_geocode.longitude
    try:
        location_response = supabase.table('Location').insert(user_data['location']).execute()
        if len(location_response.data) > 0:
            del user_data['location']
            user_data['address_id'] = location_response.data[0]['id']
            response = supabase.table('users').insert(user_data).execute()
            if len(response.data) > 0:
                return jsonify({"message": "User created successfully!"}), 201
            else:
                return jsonify({"error": response.error_message}), 400
        else:
            return jsonify({"error": location_response.error_message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
@bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    response = supabase.table('users').select('*').eq('id', user_id).execute()
    
    if response.data:
        location_response = supabase.table('Location').select('*').eq('id', response.data[0]['address_id']).execute()
        if location_response.data:
            response.data[0]['location'] = location_response.data[0]
            del response.data[0]['address_id']
            return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "User not found"}), 404
@bp.route('/login', methods=['POST'])
def login_user():
    user_data = request.get_json()
    response = supabase.table('users').select('*').eq('email', user_data['email']).eq('password',user_data['password']).execute()
    if response.data:
        location_response = supabase.table('Location').select('*').eq('id', response.data[0]['address_id']).execute()
        if location_response.data:
            response.data[0]['location'] = location_response.data[0]
            del response.data[0]['address_id']
            return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "User not found"}), 404

