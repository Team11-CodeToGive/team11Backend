from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client, upload_image_to_supabase
from werkzeug.utils import secure_filename
import os
import random,string

bp = Blueprint('image_upload_routes', __name__)
supabase = get_supabase_client()

# Set allowed file types for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Check if the file extension is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/uploadImage', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_content = file.read()
            
            # Upload to Supabase bucket (e.g., 'event-images')
            response = upload_image_to_supabase('event-images', filename + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)), file_content)
            
            # Image uploaded successfully, return the public URL
            image_url = f"{supabase.storage.from_('event-images').get_public_url(filename)}"
            return jsonify({"message": "Image uploaded successfully!", "image_url": image_url}), 201
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file type"}), 400
