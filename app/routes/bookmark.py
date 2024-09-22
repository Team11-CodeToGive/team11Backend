from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client

bp = Blueprint('bookmark_routes', __name__)
supabase = get_supabase_client()

@bp.route('/create', methods=['POST'])
def bookmark_event():
    bookmark_data = request.get_json()
    
    user_id = bookmark_data.get('user_id')
    event_id = bookmark_data.get('event_id')

    # Check if the bookmark already exists to prevent duplicates
    existing_bookmark = supabase.table('Bookmarks').select('*')\
        .eq('user_id', user_id).eq('event_id', event_id).execute()

    if existing_bookmark.data:
        return jsonify({"error": "Event is already bookmarked"}), 400
    
    try:
        # Insert bookmark into Bookmarks table
        response = supabase.table('Bookmarks').insert(bookmark_data).execute()

        if response.data:
            return jsonify({"message": "Event bookmarked successfully!"}), 201
        else:
            return jsonify({"error": response.error_message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:user_id>/bookmarks', methods=['GET'])
def get_bookmarked_events(user_id):
    # Fetch the bookmarked event IDs for the user
    response = supabase.table('Bookmarks').select('event_id').eq('user_id', user_id).execute()
    
    if response.data:
        # Get the event details for the bookmarked events
        event_ids = [bookmark['event_id'] for bookmark in response.data]
        
        if event_ids:
            events_response = supabase.table('Events').select('*').in_('event_id', event_ids).execute()
            return jsonify(events_response.data), 200
        else:
            return jsonify([]), 200
    else:
        return jsonify({"error": "No bookmarked events found"}), 404
    
@bp.route('/', methods=['DELETE'])
def remove_bookmark():
    bookmark_data = request.get_json()

    user_id = bookmark_data.get('user_id')
    event_id = bookmark_data.get('event_id')

    try:
        # Remove the bookmark for the user
        response = supabase.table('Bookmarks').delete()\
            .eq('user_id', user_id).eq('event_id', event_id).execute()

        if response.data:
            return jsonify({"message": "Bookmark removed successfully!"}), 200
        else:
            return jsonify({"error": "Bookmark not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
