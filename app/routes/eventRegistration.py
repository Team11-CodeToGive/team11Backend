from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client

bp = Blueprint('event_registration_routes', __name__)
supabase = get_supabase_client()

@bp.route('/create', methods=['POST'])
def create_registration():
    pass

@bp.route('/<int:registration_id>', methods=['DELETE'])
def cancel_registrations(registration_id):
    pass