import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from flask import Blueprint, request, jsonify, session,send_file
from ..supabase_service import get_supabase_client
bp = Blueprint('create_flyer_routes', __name__)
supabase = get_supabase_client()

@bp.route('/<event_id>', methods=['GET'])
def get_flyer(event_id):
    response = supabase.table('Events').select('*').eq('event_id', event_id).execute()
    
    if response.data:
        event = response.data[0]
        image_url = "https://image.pollinations.ai/prompt/no-letters-on-image"+event['title'].replace(' ','-')
        flyer_image = create_flyer_from_url(image_url=image_url,title=event['title'],location="123 Main St, City",
    time="September 25, 2024, 6:00 PM",description=event['description'])
        return send_file(flyer_image, mimetype='image/jpeg')
    else:
        return jsonify({"error": "User not found"}), 404

def get_text_color_for_background(image, position, font, text, draw):
    # Sample a small area of the image under the text
    bbox = draw.textbbox(position, text, font=font)  # Get text bounding box
    cropped_image = image.crop(bbox)  # Crop the image to the text area
    
    # Calculate the average brightness of the background under the text
    pixels = list(cropped_image.getdata())
    avg_luminance = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pixels) / len(pixels)
    
    # Return white text for dark background and black text for light background
    return (255, 255, 255) if avg_luminance < 128 else (0, 0, 0)

def create_flyer_from_url(image_url, title, location, time, description):
    # Fetch the image from the URL
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))

    # Get image width and calculate max width for text
    image_width, image_height = image.size
    max_width = int(image_width * 0.8)  # Set max_width to 80% of image width

    # Set up ImageDraw to add text to the image
    draw = ImageDraw.Draw(image)

    # Load a font
    font_path = "Poppins-ExtraBoldItalic.ttf"  # Replace with the path to a .ttf font file on your system
    title_font = ImageFont.truetype(font_path, 40)  # Font size for the title
    text_font = ImageFont.truetype(font_path, 30)   # Font size for the other details

    # Define text positions (adjust as needed)
    title_position = (50, 50)
    location_position = (50, 150)
    time_position = (50, 200)
    description_position = (50, 250)

    # Add title with dynamic color based on background
    title_color = get_text_color_for_background(image, title_position, title_font, title, draw)
    draw.text(title_position, title, font=title_font, fill=title_color)

    # Add location and time with dynamic colors
    location_text = f"Location: {location}"
    location_color = get_text_color_for_background(image, location_position, text_font, location_text, draw)
    draw.text(location_position, location_text, font=text_font, fill=location_color)

    time_text = f"Time: {time}"
    time_color = get_text_color_for_background(image, time_position, text_font, time_text, draw)
    draw.text(time_position, time_text, font=text_font, fill=time_color)

    # Dynamically wrap description text to fit within max_width
    def wrap_text(text, font, max_width):
        lines = []
        words = text.split(' ')
        line = ""
        for word in words:
            test_line = line + word + " "
            # Calculate the width of the text with this test line
            bbox = draw.textbbox((0, 0), test_line, font=font)  # Bounding box for the text
            text_width = bbox[2] - bbox[0]  # Calculate text width from bbox
            if text_width <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
        return lines

    # Wrap the description text to fit within the max_width
    lines = wrap_text(description, text_font, max_width)

    # Draw the description line by line with dynamic color
    y_text = description_position[1]
    for line in lines:
        description_color = get_text_color_for_background(image, (description_position[0], y_text), text_font, line, draw)
        draw.text((description_position[0], y_text), line, font=text_font, fill=description_color)
        y_text += draw.textbbox((0, 0), line, font=text_font)[3] - draw.textbbox((0, 0), line, font=text_font)[1] + 5  # Move down for the next line

    # Save the image to a BytesIO object
    img_io = BytesIO()
    image.save(img_io, 'JPEG')
    img_io.seek(0)

    return img_io
