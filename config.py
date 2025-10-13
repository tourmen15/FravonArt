import os
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'output'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    # AI Model paths (placeholder for demo)
    SEGMENTATION_MODEL = 'torchhub/pytorch/vision/deeplabv3_resnet101'
    DEPTH_MODEL = 'intel-isl/MiDaS'
    RECONSTRUCTION_MODEL = 'facebook_detr_resnet50'
    
    # Rendering settings
    VIDEO_WIDTH = 1920
    VIDEO_HEIGHT = 1080
    FPS = 30
    VIDEO_DURATION = 30

config = Config()
