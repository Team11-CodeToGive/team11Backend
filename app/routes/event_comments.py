from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client

bp = Blueprint('event_comments_routes', __name__)
supabase = get_supabase_client()

@bp.route('/createComment', methods=['POST'])
def create_comment():
    comment_data = request.get_json()
    try:
        comment_response = supabase.table('EventComments').insert(comment_data).execute()
        if len(comment_data.data) > 0:
            return jsonify({"message": "Comment created successfully!"}), 201  
        else:
            return jsonify({"error": comment_response}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@bp.route('/createReply', methods=['POST'])
def create_reply():
    comment_data = request.get_json()
    try:
        comment_response = supabase.table('EventComments').insert(comment_data).execute()
        if len(comment_data.data) > 0:
            return jsonify({"message": "Reply created successfully!"}), 201  
        else:
            return jsonify({"error": comment_response}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@bp.route('/createReply', methods=['POST'])
def create_reply():
    comment_data = request.get_json()
    try:
        comment_response = supabase.table('EventComments').insert(comment_data).execute()
        if len(comment_data.data) > 0:
            return jsonify({"message": "Reply created successfully!"}), 201  
        else:
            return jsonify({"error": comment_response}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@bp.route('/<int:event_id>', methods=['GET'])
def get_comments(event_id):
    response = supabase.table('EventComments').select('*').eq('event_id', event_id).execute()
    
    if response.data:
        return jsonify(response.data[0]), 200
    else:
        return jsonify({"error": "Event not found"}), 404

