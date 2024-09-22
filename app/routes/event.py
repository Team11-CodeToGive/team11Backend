from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client
from geopy import distance
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="5b3ce3597851110001cf62481ce24ea21f7847f7a5ffedc7f1eac56c")
bp = Blueprint('event_routes', __name__)
supabase = get_supabase_client()

@bp.route('/', methods=['GET'])
def get_events():
    response = supabase.table('Events').select('*').execute()
    if response.data:
        for i in range(len(response.data)):
            location_response = supabase.table('Location').select('*').eq('id', response.data[i]['address_id']).execute()
            if location_response.data:
                response.data[i]['location'] = location_response.data[0]
                del response.data[i]['address_id']
            attendee_response = supabase.table('EventRegistration').select('*').eq('event_id', response.data[i]['event_id']).execute()
        
            # Add the attendees (with user info) to the event data
            response.data[i]['attendees'] = get_attendees_info(attendee_response)

        return jsonify(response.data), 200
    else:
        return jsonify([]), 200

@bp.route('/create', methods=['POST'])
def create_event():
    event_data = request.get_json()
    try:
        location_response = supabase.table('Location').insert(event_data['location']).execute()
        if len(location_response.data) > 0:
            del event_data['location']
            event_data['address_id'] = location_response.data[0]['id']
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
        location_response = supabase.table('Location').select('*').eq('id', response.data[0]['address_id']).execute()
        if location_response.data:
            response.data[0]['location'] = location_response.data[0]
            del response.data[0]['address_id']
        attendee_response = supabase.table('EventRegistration').select('*').eq('event_id', event_id).execute()
        
         # Add the attendees (with user info) to the event data
        response.data[0]['attendees'] = get_attendees_info(attendee_response)


        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "Event not found"}), 404

@bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    new_data = request.get_json()

    if not new_data:
        return jsonify({"error": "No data provided to update"}), 400

    try:
        location_response = supabase.table('Location').insert(new_data['location']).execute()
        if len(location_response.data) > 0:
            del new_data['location']
            new_data['address_id'] = location_response.data[0]['id']
            response = supabase.table('Events').update(new_data).eq('event_id', event_id).execute()

            if response.data:
                return jsonify(response.data[0]), 200
            else:
                return jsonify({"error": "Event not found or no fields updated"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    

@bp.route('/<int:event_id>', methods=['DELETE'])
def cancel_event(event_id):

    response = supabase.table('Events').delete().eq('event_id', event_id).execute()
    try:
        if response.data:
            location_response = supabase.table('Location').delete().eq('id', response.data[0]['address_id']).execute()
            if location_response:
                return jsonify({"message": "Event deleted successfully!"}), 201
            else:
                return jsonify({"error": "Event not found or could not be deleted"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@bp.route('/nearby', methods=['GET'])
def get_nearby_events():
    loc = request.get_json()
    try:
        response = supabase.table('Events').select("address_id", "Location(id,address)").execute()
        result = {}
        for val in response.data:
            event_id = val["Location"]["id"]
            event_address = val["Location"]["address"]
            try:
                dist = round(calc_distance(loc['address'], event_address),2)
                result[event_id] = dist
            except Exception as e:
                print(f"Error calculating distance for event ID {event_id}: {e}")
                continue    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}),400
    sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    return jsonify(result)

# Utility Functions

def get_attendees_info(attendee_response):
    '''
    returns list of attending users
    '''
    attendees_user_info = []

    if attendee_response.data:
        for attendee in attendee_response.data:
            user_id = attendee['user_id']
            print(user_id)
            user_response = supabase.table('users').select('*').eq('user_id', user_id).execute()
            
            if user_response.data:
                # Combine user info with attendee data
                attendee['user_info'] = user_response.data[0]

                # Add to the list of attendees
            attendees_user_info.append(attendee)
    
    return attendees_user_info

## calculates the distance between two locations
def calc_distance(loc1,loc2):
    loc1 = geolocator.geocode(loc1)
    loc2 = geolocator.geocode(loc2)
    loc1 = (loc1.latitude, loc1.longitude)
    loc2 = (loc2.latitude, loc2.longitude)
    dist = distance.distance(loc1,loc2).miles
    return dist