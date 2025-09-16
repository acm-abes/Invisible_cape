from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
from scipy import ndimage
import threading
import time

app = Flask(__name__)

class InvisibleCloak:
    def __init__(self):
        self.cap = None
        self.background = None
        self.color_lower = np.array([100, 50, 50])  # Default blue color range
        self.color_upper = np.array([130, 255, 255])
        self.is_capturing_background = False
        self.frame = None
        self.lock = threading.Lock()
        
    def start_camera(self):
        """Initialize camera capture"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open camera")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
    def stop_camera(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()
            
    def capture_background(self):
        """Capture the background when no object is present"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
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
        
    def process_frame(self):
        """Process a single frame for the invisible cloak effect"""
        if not self.cap or not self.cap.isOpened():
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect color mask
        mask = self.detect_color_mask(frame)
        
        # Apply edge smoothing
        smooth_mask = self.apply_sobel_edge_smoothing(mask)
        
        # Blend with background
        result = self.blend_background(frame, smooth_mask)
        
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

def generate_frames():
    """Generate video frames for streaming"""
    while True:
        with cloak.lock:
            frame = cloak.process_frame()
            
        if frame is not None:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture_background', methods=['POST'])
def capture_background():
    """Capture background endpoint"""
    try:
        with cloak.lock:
            success = cloak.capture_background()
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

@app.route('/start_camera', methods=['POST'])
def start_camera():
    """Start camera endpoint"""
    try:
        cloak.start_camera()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    """Stop camera endpoint"""
    try:
        cloak.stop_camera()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    finally:
        cloak.stop_camera()
