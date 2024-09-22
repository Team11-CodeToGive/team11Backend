from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client
from datetime import datetime, timedelta
from geopy import distance
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="5b3ce3597851110001cf62481ce24ea21f7847f7a5ffedc7f1eac56c")
bp = Blueprint('event_routes', __name__)
supabase = get_supabase_client()

@bp.route('/', methods=['GET'])
def get_events():
    # Get pagination parameters from request (limit and offset)
    limit = request.args.get('limit', default=10, type=int)  # Default to 10 events per request
    offset = request.args.get('offset', default=0, type=int)  # Offset for paginated results

    response = supabase.table('Events').select('*').gt('start_datetime', get_current_datetime())\
        .order('start_datetime').range(offset, offset + limit - 1).execute()
    grouped_events = []
    if response.data:
        events_by_date = {}

        for i in range(len(response.data)):
            location_response = supabase.table('Location').select('*').eq('id', response.data[i]['address_id']).execute()
            if location_response.data:
                response.data[i]['location'] = location_response.data[0]
                del response.data[i]['address_id']
            attendee_response = supabase.table('EventRegistration').select('*').eq('event_id', response.data[i]['event_id']).execute()
            response.data[i]['attendees'] = get_attendees_info(attendee_response)

             # Extract the date from the event's start_datetime and convert it to a string
            event_date = datetime.strptime(response.data[i]['start_datetime'], "%Y-%m-%dT%H:%M:%S").date().isoformat()

            # Group events by the date; initialize the list if it doesn't exist
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            
            # Append the event to the list for that date
            events_by_date[event_date].append(response.data[i])

            # Format the output as a list of dictionaries with 'date' and 'events' keys
            for date, events in events_by_date.items():
                grouped_events.append({
                    "date": date,
                    "events": events
                })
        
            # Add the attendees (with user info) to the event data

        return jsonify(grouped_events), 200
    else:
        return jsonify([]), 200

@bp.route('/create', methods=['POST'])
def create_event():
    event_data = request.get_json()
    location_geocode = geolocator.geocode(event_data["location"]["address"])
    if location_geocode is None:
        return jsonify({"error" : "Invalid location address"})
    event_data['location']['latitude'] = location_geocode.latitude
    event_data['location']['longitude'] = location_geocode.longitude
    try:
        
        location_response = supabase.table('Location').insert(event_data['location']).execute()
        if len(location_response.data) > 0:
            del event_data['location']
            event_data['address_id'] = location_response.data[0]['id']
            # Handle recurring events if recurrence data is provided
            recurrence_type = event_data.get('recurrence_type')  # daily, weekly, monthly, yearly
            recurrence_interval = event_data.get('recurrence_interval', 1)  # default to 1
            recurrence_end_datetime = event_data.get('recurrence_end_datetime')  # End of recurrence
            
            # Create the first event occurrence
            first_event_occurrence = event_data.copy()

            if event_data.get('recurring'):
                del first_event_occurrence['recurrence_type']
                del first_event_occurrence['recurrence_interval']
                del first_event_occurrence['recurrence_end_datetime']
            response = supabase.table('Events').insert(first_event_occurrence).execute()
            if len(response.data) == 0:
                return jsonify({"error": "Error creating first event occurrence"}), 400
             # If recurrence details are provided, calculate and create future occurrences
            if recurrence_type and recurrence_end_datetime:
                # Create occurrences based on recurrence rules
                start_datetime = event_data['start_datetime']
                create_recurring_events(event_data, start_datetime, recurrence_type, recurrence_interval, recurrence_end_datetime)

                return jsonify({"message": "Event created successfully with recurrences!"}), 201
            else:
                return jsonify({"message": "Event created successfully!"}), 201

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

        if response.data[0]['recurring']:
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            recurring_response = supabase.table('Events').select('*').eq('title', response.data[0]['title'])\
                .gt('start_datetime', current_datetime).execute()
            
            if recurring_response.data:
                occurences = []
                for i in recurring_response.data:
                    occurences.append(i['start_datetime'])
                
                response.data[0]['occurences'] = occurences


        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "Event not found"}), 404

@bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    new_data = request.get_json()
    if not new_data:
        return jsonify({"error": "No data provided to update"}), 400
    if "location" in new_data:
        location_geocode = geolocator.geocode(new_data["location"]["address"])
        if location_geocode is None:
            return jsonify({"error" : "Invalid location address"})
        new_data['location']['latitude'] = location_geocode.latitude
        new_data['location']['longitude'] = location_geocode.longitude
        location_response = supabase.table('Location').insert(new_data['location']).execute()
        del new_data['location']
    try:
        if len(location_response.data) > 0:
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
        response = supabase.table('Location').select("latitude, longitude").eq("address", loc['address']).limit(1).execute()
        user_coor = (response.data[0]['latitude'], response.data[0]["longitude"])
    except Exception as e:
        print(e)
        location_geocode = geolocator.geocode(loc["address"])
        if location_geocode is None:
            return jsonify({"error" : "Invalid location address"})
        user_coor = (location_geocode.latitude,location_geocode.longitude)

    try:
        response = supabase.table('Events').select("event_id", "Location(id,latitude,longitude)").execute()
        result = {}
        for val in response.data:
            event_id = val["event_id"]
            if val["Location"]["latitude"] == None or val["Location"]["longitude"] == None:
                continue
            event_coor= (val["Location"]["latitude"], val["Location"]['longitude'])
            try:
                dist = round(calc_distance(user_coor, event_coor),2)
                result[event_id] = dist
            except Exception as e:
                print(f"Error calculating distance for event ID {event_id}: {e}")
                continue    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}),400
    sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=False)
    return jsonify(sorted_result)

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

def create_recurring_events(event_data, start_datetime, recurrence_type, interval, end_datetime):
    current_start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')  # Assuming ISO format for datetime
    current_start_datetime = calculate_next_occurrence(current_start_datetime, recurrence_type, interval)

    current_end_datetime = datetime.strptime(event_data['end_datetime'], '%Y-%m-%dT%H:%M:%S')
    current_end_datetime = calculate_next_occurrence(current_end_datetime, recurrence_type, interval)

    # Calculate the duration of the event (difference between start and end times)
    event_duration = current_end_datetime - current_start_datetime

    recurrence_end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S')
    


    occurrences = []
    occurrence_count = 1  # Start counting occurrences (first event already created)
    
    while current_start_datetime <= recurrence_end_datetime and occurrence_count < 4:
        next_occurrence_data = event_data.copy()  # Create a copy of the original event data
        del next_occurrence_data['recurrence_type']
        del next_occurrence_data['recurrence_interval']
        del next_occurrence_data['recurrence_end_datetime']
        next_occurrence_data['start_datetime'] = current_start_datetime.strftime('%Y-%m-%dT%H:%M:%S')  # Update start_datetime
        next_occurrence_data['end_datetime'] = (current_start_datetime + event_duration).strftime('%Y-%m-%dT%H:%M:%S')
        
        # Insert each occurrence into the Events table
        try:
            supabase.table('Events').insert(next_occurrence_data).execute()
            occurrence_count += 1  # Increment the occurrence count
        except Exception as e:
            print(f"Error inserting occurrence on {current_start_datetime}: {e}")

        # Calculate the next occurrence based on recurrence type
        current_start_datetime = calculate_next_occurrence(current_start_datetime, recurrence_type, interval)
        current_end_datetime = current_start_datetime + event_duration  # Adjust the end time based on the new start time


# Helper function to calculate the next occurrence date
def calculate_next_occurrence(current_datetime, recurrence_type, interval):
    if recurrence_type == 'daily':
        return current_datetime + timedelta(days=interval)
    elif recurrence_type == 'weekly':
        return current_datetime + timedelta(weeks=interval)
    elif recurrence_type == 'monthly':
        return add_months(current_datetime, interval)
    elif recurrence_type == 'yearly':
        return add_years(current_datetime, interval)
    else:
        raise ValueError(f"Unsupported recurrence type: {recurrence_type}")
    
# Helper function to add months
def add_months(current_datetime, months):
    month = current_datetime.month - 1 + months
    year = current_datetime.year + month // 12
    month = month % 12 + 1
    day = min(current_datetime.day, (datetime(year, month, 1) - timedelta(days=1)).day)
    return current_datetime.replace(year=year, month=month, day=day)

# Helper function to add years
def add_years(current_datetime, years):
    try:
        return current_datetime.replace(year=current_datetime.year + years)
    except ValueError:
        # Handle leap year cases (e.g., Feb 29 on leap year)
        return current_datetime.replace(month=2, day=28, year=current_datetime.year + years)



## calculates the distance between two locations
def calc_distance(loc1,loc2):
    dist = distance.distance(loc1,loc2).miles
    return dist

def get_current_datetime():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
