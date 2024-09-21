from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client

bp = Blueprint('event_routes', __name__)
supabase = get_supabase_client()

@bp.route('/', methods=['GET'])
def get_events():
    pass  # GET method to retrieve all events

@bp.route('/create', methods=['POST'])
def create_event():
    pass

@bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    pass

@bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    pass

@bp.route('/<int:event_id>', methods=['DELETE'])
def cancel_event(event_id):
    pass