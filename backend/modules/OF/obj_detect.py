import cv2
import base64
from groq import Groq
import os
import tomli
import time

def load_config():
    """Load configuration from config.toml file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              'AI', 'perplexica', 'config.toml')
    try:
        with open(config_path, 'rb') as f:
            return tomli.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def capture_and_recognize_image():
    """Captures an image from the webcam, encodes it, and sends it for recognition using the Groq API."""
    
    # Load configuration
    config = load_config()
    if not config or 'API_KEYS' not in config or 'GROQ' not in config['API_KEYS']:
        print("Error: GROQ API key not found in config file")
        return

    api_key = config['API_KEYS']['GROQ']
    
    # Initialize webcam with retries
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            # Try to open the default camera
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Using DirectShow backend
            
            if not cap.isOpened():
                print(f"Attempt {attempt + 1}: Could not open webcam, trying alternative camera...")
                # Try alternative camera index
                cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                
            if not cap.isOpened():
                raise Exception("Could not open any camera")
                
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Give camera time to initialize
            time.sleep(0.5)
            
            ret, frame = cap.read()
            if not ret:
                raise Exception("Could not read frame from webcam")
                
            # Release camera immediately after capturing
            cap.release()
            cv2.destroyAllWindows()
            
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            
            # Save the image temporarily
            temp_img_filename = 'captured_image.jpg'
            with open(temp_img_filename, 'wb') as f:
                f.write(base64.b64decode(jpg_as_text))
            
            # Perform image recognition using the Groq API
            try:
                # Initialize the Groq client
                client = Groq(api_key=api_key)

                # Send the image for recognition
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "What's in this image?"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"file://{os.path.abspath(temp_img_filename)}",
                                    },
                                },
                            ],
                        }
                    ],
                    model="llava-v1.5-7b-4096-preview",
                )

                # Output the recognition result
                print("Recognition Result:", chat_completion.choices[0].message.content)
                return True

            except Exception as e:
                print(f"Error during image recognition: {e}")
                return False
                
            finally:
                # Clean up temporary image file
                if os.path.exists(temp_img_filename):
                    os.remove(temp_img_filename)
                    
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All attempts to access camera failed")
                return False

# Only run if this file is executed directly
if __name__ == "__main__":
    capture_and_recognize_image()
