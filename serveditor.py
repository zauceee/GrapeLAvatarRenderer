from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageOps
import io
import base64
import threading

app = Flask(__name__)

# Constants
WIDTH, HEIGHT = 1653, 2486
DEFAULT_AVATAR_COLOR = (0, 0, 255)  # Default color: Blue

# Load your avatar image and face image
avatar_image = Image.open("avatar.png") 
avatar_image = avatar_image.resize((WIDTH, HEIGHT))
face_image = Image.open("face.png")  # Replace with the path to your face image

# Function to edit the avatar color
def edit_avatar_color(rgb_color):
    avatar_color = tuple(map(int, rgb_color))
    avatar_with_color = avatar_image.copy()
    avatar_with_color = ImageOps.colorize(avatar_with_color.convert('L'), "#000000", f"rgb{avatar_color}")
    avatar_with_color.putalpha(avatar_image.getchannel('A'))
    return avatar_with_color

# Function to remove white background from an image and make it transparent
def remove_white_background(image):
    image = image.convert("RGBA")
    image_data = image.getdata()
    new_image_data = []
    for item in image_data:
        # If the pixel is white, make it transparent
        if item[:3] == (255, 255, 255):
            new_image_data.append((255, 255, 255, 0))
        else:
            new_image_data.append(item)
    image.putdata(new_image_data)
    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edit_avatar', methods=['POST'])
def edit_avatar():
    try:
        data = request.json
        rgb_color = data.get('color')
        if rgb_color:
            edited_avatar = edit_avatar_color(rgb_color)
                        
            if data.get('face') == 1:
                face_image = Image.open("default.png")
            else:
                face_image = Image.open("face.png")
            
            # Remove the white background from the face image
            transparent_face = remove_white_background(face_image)
            
            # Overlay the transparent face image onto the avatar
            edited_avatar.paste(transparent_face, transparent_face)
            
            # Convert the edited image to base64
            buffered = io.BytesIO()
            edited_avatar.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode()

            return jsonify({'image_base64': image_base64})
        else:
            return jsonify({'error': 'Invalid data'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
