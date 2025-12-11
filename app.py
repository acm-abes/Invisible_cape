from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
from scipy import ndimage
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

class InvisibleCloak:
    def __init__(self):
        self.background = None
        self.color_lower = np.array([100, 50, 50])  # Default blue color range
        self.color_upper = np.array([130, 255, 255])
        self.current_frame = None
        
    def decode_image(self, base64_string):
        """Decode base64 image to numpy array"""
        try:
            # Remove data URL prefix if present
            if 'base64,' in base64_string:
                base64_string = base64_string.split('base64,')[1]
            
            # Decode base64 to image
            img_data = base64.b64decode(base64_string)
            img = Image.open(BytesIO(img_data))
            
            # Convert to numpy array and BGR format for OpenCV
            frame = np.array(img)
            if len(frame.shape) == 2:  # Grayscale
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif frame.shape[2] == 4:  # RGBA
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            else:  # RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            return frame
        except Exception as e:
            print(f"Error decoding image: {e}")
            return None
        
    def capture_background_from_frame(self, frame):
        """Capture the background from a provided frame"""
        if frame is not None:
            # Convert to HSV for better color detection
            self.background = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            return True
        return False
        
    def detect_color_mask(self, frame):
        """Detect the colored cloak and create a mask"""
        # Convert frame to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for the specified color range
        mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask
        
    def apply_sobel_edge_smoothing(self, mask):
        """Apply Sobel filters for edge smoothing"""
        # Convert mask to float for processing
        mask_float = mask.astype(np.float32) / 255.0
        
        # Apply Gaussian blur to smooth the mask
        mask_blurred = cv2.GaussianBlur(mask_float, (5, 5), 0)
        
        # Apply Sobel filters for edge detection
        sobel_x = cv2.Sobel(mask_blurred, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(mask_blurred, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Normalize and create smooth edges
        gradient_magnitude = np.clip(gradient_magnitude, 0, 1)
        
        # Create smooth transition at edges
        smooth_mask = mask_blurred - gradient_magnitude * 0.3
        smooth_mask = np.clip(smooth_mask, 0, 1)
        
        return (smooth_mask * 255).astype(np.uint8)
        
    def blend_background(self, frame, mask):
        """Blend the background with the current frame"""
        if self.background is None:
            return frame
            
        # Convert current frame to HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Convert background back to BGR for blending
        background_bgr = cv2.cvtColor(self.background, cv2.COLOR_HSV2BGR)
        
        # Create 3-channel mask
        mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
        
        # Blend the images
        result = frame * (1 - mask_3channel) + background_bgr * mask_3channel
        
        return result.astype(np.uint8)
        
    def process_frame(self, frame):
        """Process a single frame for the invisible cloak effect"""
        if frame is None:
            return None
        
        # Detect color mask
        mask = self.detect_color_mask(frame)
        
        # Apply edge smoothing
        smooth_mask = self.apply_sobel_edge_smoothing(mask)
        
        # Blend with background
        result = self.blend_background(frame, smooth_mask)
        
        self.current_frame = result
        return result
        
    def set_color_range(self, color_name):
        """Set color detection range based on color name"""
        color_ranges = {
            'red': ([0, 50, 50], [10, 255, 255]),
            'blue': ([100, 50, 50], [130, 255, 255]),
            'green': ([40, 50, 50], [80, 255, 255]),
            'yellow': ([20, 50, 50], [40, 255, 255]),
            'purple': ([130, 50, 50], [160, 255, 255])
        }
        
        if color_name in color_ranges:
            self.color_lower = np.array(color_ranges[color_name][0])
            self.color_upper = np.array(color_ranges[color_name][1])

# Global instance
cloak = InvisibleCloak()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Process a frame from the browser"""
    try:
        data = request.get_json()
        frame_data = data.get('frame')
        
        if not frame_data:
            return jsonify({'success': False, 'error': 'No frame data'})
        
        # Decode the frame
        frame = cloak.decode_image(frame_data)
        if frame is None:
            return jsonify({'success': False, 'error': 'Failed to decode frame'})
        
        # Process the frame
        processed_frame = cloak.process_frame(frame)
        
        if processed_frame is not None:
            # Encode back to base64
            _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return jsonify({'success': True, 'frame': f'data:image/jpeg;base64,{frame_base64}'})
        else:
            return jsonify({'success': False, 'error': 'Processing failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/capture_background', methods=['POST'])
def capture_background():
    """Capture background endpoint"""
    try:
        data = request.get_json()
        frame_data = data.get('frame')
        
        if not frame_data:
            return jsonify({'success': False, 'error': 'No frame data'})
        
        # Decode the frame
        frame = cloak.decode_image(frame_data)
        if frame is None:
            return jsonify({'success': False, 'error': 'Failed to decode frame'})
        
        success = cloak.capture_background_from_frame(frame)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/set_color', methods=['POST'])
def set_color():
    """Set color detection range"""
    try:
        data = request.get_json()
        color = data.get('color', 'blue')
        cloak.set_color_range(color)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
