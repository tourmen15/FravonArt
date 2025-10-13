import os
import uuid
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

from config import config
from image_processor import ImageProcessor
from animation_engine import AnimationEngine
from video_renderer import VideoRenderer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config)
CORS(app)

# Ensure directories exist
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

# Global job tracking
jobs = {}

class AnimationJob:
    def __init__(self, job_id, image_path, focus_type):
        self.job_id = job_id
        self.image_path = image_path
        self.focus_type = focus_type
        self.status = 'pending'  # pending, processing, completed, error
        self.progress = 0
        self.output_path = None
        self.error_message = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def process_animation_job(job):
    """Background job processor"""
    try:
        job.status = 'processing'
        
        # Step 1: Process image with AI models
        job.progress = 10
        logger.info(f"Job {job.job_id}: Processing image...")
        processor = ImageProcessor()
        segmentation_data = processor.segment_image(job.image_path)
        depth_data = processor.estimate_depth(job.image_path)
        reconstruction_data = processor.reconstruct_3d(job.image_path, segmentation_data, depth_data)
        
        job.progress = 40
        
        # Step 2: Create animation
        logger.info(f"Job {job.job_id}: Generating animation...")
        animator = AnimationEngine()
        animation_data = animator.create_animation_sequence(
            reconstruction_data, 
            job.focus_type
        )
        
        job.progress = 70
        
        # Step 3: Render video
        logger.info(f"Job {job.job_id}: Rendering video...")
        renderer = VideoRenderer()
        output_filename = f"{job.job_id}.mp4"
        output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)
        
        renderer.render_video(
            animation_data,
            output_path,
            duration=config.VIDEO_DURATION
        )
        
        job.progress = 100
        job.output_path = output_path
        job.status = 'completed'
        logger.info(f"Job {job.job_id}: Completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job.job_id}: Error - {str(e)}")
        job.status = 'error'
        job.error_message = str(e)

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Handle image upload and start animation generation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        focus_type = request.form.get('focus_type', 'auto')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique job ID
            job_id = str(uuid.uuid4())
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(config.UPLOAD_FOLDER, f"{job_id}_{filename}")
            file.save(file_path)
            
            # Create job
            job = AnimationJob(job_id, file_path, focus_type)
            jobs[job_id] = job
            
            # Start processing in background thread
            thread = threading.Thread(target=process_animation_job, args=(job,))
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'job_id': job_id,
                'status': 'pending',
                'message': 'Animation generation started'
            }), 202
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Check job status and progress"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    response = {
        'job_id': job_id,
        'status': job.status,
        'progress': job.progress
    }
    
    if job.status == 'completed':
        response['download_url'] = f'/api/download/{job_id}'
    elif job.status == 'error':
        response['error'] = job.error_message
    
    return jsonify(response)

@app.route('/api/download/<job_id>', methods=['GET'])
def download_video(job_id):
    """Download completed animation video"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job.status != 'completed':
        return jsonify({'error': 'Video not ready'}), 400
    
    if not job.output_path or not os.path.exists(job.output_path):
        return jsonify({'error': 'Video file not found'}), 404
    
    return send_file(
        job.output_path,
        as_attachment=True,
        download_name=f'architectural_animation_{job_id}.mp4'
    )

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Architectural Animator Pro'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
