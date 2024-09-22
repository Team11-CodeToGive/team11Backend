from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client
from werkzeug.exceptions import BadRequest

bp = Blueprint('community_routes', __name__)
supabase = get_supabase_client()

@bp.route('/create', methods=['POST'])
def create_community():
    community_data = request.get_json()
    if not community_data:
        raise BadRequest("No input data provided")
    try:
        response = supabase.table('Community').insert(community_data).execute()
        
        if len(response.data) >0:
            community_data["community_id"] = response.data[0]["community_id"]
            del community_data['name']
            del community_data['description']
            del community_data['members']
            del community_data['logo']
            community_data['user_id'] = community_data.pop("owner_id")
            supabase.table('CommunityRegistration').insert(community_data).execute()
            return jsonify({"message": "Community created successfully!"})
        else:
            return jsonify({"error": response.error_message}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400
    
@bp.route('/<int:community_id>', methods=['PUT','PATCH'])
def edit_community(community_id):
    data = request.get_json()
    if not data:
        raise BadRequest('No input data provided')
    try:
        update_response = supabase.table('Community').update(data).eq('community_id', community_id).execute()
        if update_response.data:
            return jsonify({"message": "Community updated successfuly!"})
        else:
            return jsonify({"error": "Community not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:community_id>', methods=['DELETE'])
def del_community(community_id):
    try:
        del_response = supabase.table('Community').delete().eq('community_id', community_id).execute()
        if del_response.data:
            return jsonify({"message": "Community deleted successfuly!"})
        else:
            return jsonify({"error": "Community not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@bp.route('/<int:community_id>', methods=['GET'])
def get_community(community_id):
    try:
        response = supabase.table('Community').select('*').eq('community_id', community_id).execute()
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    

@bp.route('/<int:community_id>/join', methods=['POST'])
def join_community(community_id):
    data = request.get_json()
    data["community_id"] = community_id
    if not data:
        raise BadRequest('No input data provided')
    try:
        response = supabase.table('CommunityRegistration').insert(data).execute()
        if len(response.data) > 0:
            members_result = supabase.table('CommunityRegistration').select('user_id').eq('community_id', community_id).execute()
            member_ids = [row['user_id'] for row in members_result.data]
            supabase.table('Community').update({"members": member_ids}).eq('community_id',community_id).execute()
            return jsonify({"message": "Community Joined successfully"})
        else:
            return jsonify({"error": response.error.message}), 400
    except Exception as e:
        print(e)
        return jsonify({"error":str(e)}),400

@bp.route('/<int:community_id>/leave', methods=['DELETE'])
def leave_community(community_id):
    data = request.get_json()
    if not data:
        raise BadRequest('No input data provided')
    try:
        response = supabase.table('CommunityRegistration').select('registration_id').eq('community_id', community_id).eq('user_id', data['user_id']).execute()
        registration_id = response.data[0]['registration_id']
        if len(response.data) > 0:
            registration_id = response.data[0]['registration_id']
            supabase.table('CommunityRegistration').delete().eq('registration_id',registration_id).execute()
            members_result = supabase.table('CommunityRegistration').select('user_id').eq('community_id', community_id).execute()
            member_ids = [row['user_id'] for row in members_result.data]
            supabase.table('Community').update({"members": member_ids}).eq('community_id',community_id).execute()
            return jsonify({"message": "Community Left successfully"})
        else:
            return jsonify({"error": response.error.message}), 400
    except Exception as e:
        print(e)
        return jsonify({"error":str(e)}),400
    
@bp.route('/', methods=['GET'])
def get_communties():
    response = supabase.table('Community').select('*').execute()
    return response.data

 
