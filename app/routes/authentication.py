from flask import Blueprint, request, jsonify, session
from ..supabase_service import get_supabase_client
from werkzeug.security import generate_password_hash, check_password_hash
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="5b3ce3597851110001cf62481ce24ea21f7847f7a5ffedc7f1eac56c")
bp = Blueprint('user_routes', __name__)
supabase = get_supabase_client()

@bp.route('/create', methods=['POST'])
def create_user():
    user_data = request.get_json()
    try:
        location_geocode = geolocator.geocode(user_data["location"]["address"])
    except Exception as e:
        print(e)
        return jsonify({"error" : "Invalid location addresss"}), 400
    if location_geocode is None:
        return jsonify({"error" : "Invalid location address"}), 400
    user_data['location']['latitude'] = location_geocode.latitude
    user_data['location']['longitude'] = location_geocode.longitude
    try:
        location_response = supabase.table('Location').insert(user_data['location']).execute()
        if len(location_response.data) > 0:
            del user_data['location']
            user_data['address_id'] = location_response.data[0]['id']
            user_data['password'] = generate_password_hash(user_data['password'])
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
    response = supabase.table('users').select('*').eq('email', user_data['email']).execute()
    if response.data:
        user = response.data[0]
        if check_password_hash(user['password'],user_data['password']):
            session['user_id'] = response.data[0]['user_id']
            session['user_email'] = response.data[0]['email']
            location_response = supabase.table('Location').select('*').eq('id', response.data[0]['address_id']).execute()
            if location_response.data:
                response.data[0]['location'] = location_response.data[0]
                del response.data[0]['address_id']
            return jsonify(response.data[0]), 200
        else:
            return jsonify({"error": "User not found"}), 404
    else:
        return jsonify({"error": "User not found"}), 404
    
@bp.route('/logout', methods=['POST'])
def logout_user():
    try:
        if 'user_id' in session:
            session.clear()  # Clear all session data
            return jsonify({"message": "Logged out successfully!"}), 200
        else:
            return jsonify({"Error": "Not logged in!"}), 200
    except:
        return jsonify({"Error": "Unable to logout. Please try again!"})
