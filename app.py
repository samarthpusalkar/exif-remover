from flask import Flask, render_template, request, send_file, jsonify, after_this_request
import os
import tempfile
import uuid
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
from datetime import datetime, timedelta
import threading
import time
import argparse
import sys

app = Flask(__name__)

# Configuration from environment variables with defaults
DEFAULT_PORT = 4001
DEFAULT_HOST = '0.0.0.0'
DEFAULT_MAX_SIZE = 50 * 1024 * 1024  # 50MB

# Get configuration from environment variables
PORT = int(os.environ.get('PORT', DEFAULT_PORT))
HOST = os.environ.get('HOST', DEFAULT_HOST)
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', DEFAULT_MAX_SIZE))

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create directories if they don't exist
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

class FileProcessor:
    """Extensible file processor for different formats"""
    
    @staticmethod
    def process_image(input_path, output_path):
        """Remove EXIF data from image"""
        try:
            with Image.open(input_path) as image:
                # Convert to RGB if necessary (handles RGBA, P modes)
                if image.mode in ('RGBA', 'P'):
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = rgb_image
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Save without EXIF data
                image.save(output_path, 'JPEG', quality=95, optimize=True)
                return True
        except Exception as e:
            print(f"Error processing image: {e}")
            return False
    
    @staticmethod
    def get_exif_info(image_path):
        """Extract EXIF information for display"""
        try:
            with Image.open(image_path) as image:
                exif_data = {}
                if hasattr(image, '_getexif') and image._getexif() is not None:
                    exif = image._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
                return exif_data
        except Exception:
            return {}
    
    @staticmethod
    def process_file(input_path, output_path, file_type):
        """Main processing function - extensible for different formats"""
        if file_type.lower() in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            return FileProcessor.process_image(input_path, output_path)
        # Future: Add PDF processing here
        # elif file_type.lower() == 'pdf':
        #     return FileProcessor.process_pdf(input_path, output_path)
        else:
            return False

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    while True:
        try:
            current_time = datetime.now()
            for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        if os.path.isfile(file_path):
                            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                            if current_time - file_time > timedelta(hours=1):
                                os.remove(file_path)
                                print(f"Cleaned up old file: {filename}")
            time.sleep(3600)  # Run every hour
        except Exception as e:
            print(f"Cleanup error: {e}")
            time.sleep(3600)

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    # Pass configuration to template for display
    config_info = {
        'max_file_size': MAX_FILE_SIZE,
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024)
    }
    return render_template('index.html', config=config_info)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file size
    if hasattr(file, 'content_length') and file.content_length > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE // (1024 * 1024)
        return jsonify({'error': f'File size exceeds {max_size_mb}MB limit'}), 413
    
    if file:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Unsupported file type. Supported formats: JPG, PNG, TIFF, BMP'}), 400
        
        # Save uploaded file
        input_filename = f"{file_id}_input{file_ext}"
        output_filename = f"{file_id}_output.jpg"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        
        try:
            file.save(input_path)
            
            # Check actual file size after saving
            actual_size = os.path.getsize(input_path)
            if actual_size > MAX_FILE_SIZE:
                os.remove(input_path)  # Clean up
                max_size_mb = MAX_FILE_SIZE // (1024 * 1024)
                return jsonify({'error': f'File size exceeds {max_size_mb}MB limit'}), 413
            
            # Get original EXIF data
            original_exif = FileProcessor.get_exif_info(input_path)
            
            # Process file
            success = FileProcessor.process_file(input_path, output_path, file_ext[1:])
            
            if success:
                # Get file sizes
                original_size = os.path.getsize(input_path)
                processed_size = os.path.getsize(output_path)
                
                return jsonify({
                    'success': True,
                    'file_id': file_id,
                    'original_filename': file.filename,
                    'original_size': original_size,
                    'processed_size': processed_size,
                    'exif_data': original_exif
                })
            else:
                # Clean up on failure
                if os.path.exists(input_path):
                    os.remove(input_path)
                return jsonify({'error': 'Failed to process file. Please ensure it\'s a valid image.'}), 500
                
        except Exception as e:
            # Clean up on error
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/download/<file_id>')
def download_file(file_id):
    try:
        output_filename = f"{file_id}_output.jpg"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'File not found or has expired'}), 404
        
        @after_this_request
        def cleanup_files(response):
            # Clean up files after download
            try:
                input_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(file_id)]
                for f in input_files:
                    file_path = os.path.join(UPLOAD_FOLDER, f)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Cleaned up: {file_path}")
                        
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"Cleaned up: {output_path}")
            except Exception as e:
                print(f"Cleanup error: {e}")
            return response
        
        return send_file(output_path, as_attachment=True, 
                        download_name=f"exif_removed_{file_id}.jpg")
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024),
        'supported_formats': ['JPG', 'JPEG', 'PNG', 'TIFF', 'BMP']
    })

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='EXIF Data Remover Web Application')
    parser.add_argument('--port', type=int, default=PORT,
                       help=f'Port to run the server on (default: {PORT})')
    parser.add_argument('--host', type=str, default=HOST,
                       help=f'Host to bind the server to (default: {HOST})')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')
    parser.add_argument('--max-size', type=int,
                       help=f'Maximum file size in MB (default: {MAX_FILE_SIZE // (1024 * 1024)})')
    
    return parser.parse_args()

def print_startup_info(host, port, debug_mode):
    """Print startup information"""
    print("=" * 60)
    print("🛡️  EXIF Data Remover - Privacy First Image Processing")
    print("=" * 60)
    print(f"🌐 Server running at: http://{host}:{port}")
    if host == '0.0.0.0':
        print(f"🔗 Local access: http://localhost:{port}")
    print(f"📊 Max file size: {MAX_FILE_SIZE // (1024 * 1024)}MB")
    print(f"📁 Supported formats: JPG, PNG, TIFF, BMP")
    print(f"🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
    print(f"🔄 Auto cleanup: Every hour")
    print("=" * 60)
    print("💡 Tip: Use Ctrl+C to stop the server")
    print("🔒 Your files are processed locally and never leave your computer!")
    print("=" * 60)

if __name__ == '__main__':
    args = parse_arguments()
    
    # Override configuration with command line arguments
    final_port = args.port
    final_host = args.host
    debug_mode = args.debug
    
    # Update max file size if provided
    if args.max_size:
        MAX_FILE_SIZE = args.max_size * 1024 * 1024
        app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
    
    # Print startup information
    print_startup_info(final_host, final_port, debug_mode)
    
    try:
        app.run(debug=debug_mode, host=final_host, port=final_port)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thank you for using EXIF Data Remover!")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
