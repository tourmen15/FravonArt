import os
import numpy as np
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx.all import volumex
import cv2
from PIL import Image, ImageDraw, ImageFont
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class VideoRenderer:
    """Renders the final MP4 video with animations and audio"""
    
    def __init__(self):
        self.video_width = 1920
        self.video_height = 1080
        self.fps = 30
        self.assets_path = "assets/static"
    
    def render_video(self, animation_data, output_path, duration=30):
        """Render the complete animation video"""
        logger.info(f"Rendering video to: {output_path}")
        
        try:
            # Create animation frames
            def make_frame(t):
                return self._render_frame(t, animation_data, duration)
            
            # Create video clip
            video = VideoClip(make_frame, duration=duration)
            video = video.set_fps(self.fps)
            
            # Add audio
            audio = self._create_audio_track(duration)
            video = video.set_audio(audio)
            
            # Write video file
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            logger.info("Video rendering completed successfully")
            
        except Exception as e:
            logger.error(f"Video rendering error: {e}")
            raise
    
    def _render_frame(self, t, animation_data, total_duration):
        """Render a single frame at time t"""
        # Create blank canvas
        frame = np.zeros((self.video_height, self.video_width, 3), dtype=np.uint8)
        frame[:, :] = [240, 240, 240]  # Light gray background
        
        # Determine current animation phase
        phase = self._get_current_phase(t, animation_data['animation_phases'])
        
        # Render based on phase
        if phase['name'] == "Analytical Deconstruction":
            frame = self._render_analytical_phase(frame, t, phase, animation_data)
        elif phase['name'] == "2D Plan Emergence":
            frame = self._render_2d_phase(frame, t, phase, animation_data)
        elif phase['name'] == "3D Extrusion & Materialization":
            frame = self._render_3d_phase(frame, t, phase, animation_data)
        elif phase['name'] == "Final Reveal & Loop":
            frame = self._render_final_phase(frame, t, phase, animation_data)
        
        return frame
    
    def _get_current_phase(self, t, phases):
        """Get the current animation phase based on time"""
        for phase in phases:
            if phase['start_time'] <= t <= phase['end_time']:
                return phase
        return phases[-1]  # Return last phase if out of bounds
    
    def _render_analytical_phase(self, frame, t, phase, animation_data):
        """Render analytical deconstruction phase"""
        # Convert frame to PIL for drawing
        pil_img = Image.fromarray(frame)
        draw = ImageDraw.Draw(pil_img)
        
        # Calculate progress within phase (0 to 1)
        phase_duration = phase['end_time'] - phase['start_time']
        phase_progress = (t - phase['start_time']) / phase_duration
        
        # Draw wireframe tracing
        self._draw_wireframe_tracing(draw, phase_progress, animation_data)
        
        return np.array(pil_img)
    
    def _render_2d_phase(self, frame, t, phase, animation_data):
        """Render 2D plan emergence phase"""
        pil_img = Image.fromarray(frame)
        draw = ImageDraw.Draw(pil_img)
        
        phase_duration = phase['end_time'] - phase['start_time']
        phase_progress = (t - phase['start_time']) / phase_duration
        
        # Draw 2D floor plan
        self._draw_2d_plan(draw, phase_progress, animation_data)
        
        return np.array(pil_img)
    
    def _render_3d_phase(self, frame, t, phase, animation_data):
        """Render 3D extrusion and materialization phase"""
        pil_img = Image.fromarray(frame)
        draw = ImageDraw.Draw(pil_img)
        
        phase_duration = phase['end_time'] - phase['start_time']
        phase_progress = (t - phase['start_time']) / phase_duration
        
        # Draw 3D model with materials
        self._draw_3d_model(draw, phase_progress, animation_data)
        
        return np.array(pil_img)
    
    def _render_final_phase(self, frame, t, phase, animation_data):
        """Render final reveal phase"""
        pil_img = Image.fromarray(frame)
        draw = ImageDraw.Draw(pil_img)
        
        phase_duration = phase['end_time'] - phase['start_time']
        phase_progress = (t - phase['start_time']) / phase_duration
        
        # Draw final 3D model with enhancements
        self._draw_final_reveal(draw, phase_progress, animation_data)
        
        # Add title card in last 3 seconds
        if t > phase['end_time'] - 3:
            self._draw_title_card(draw, phase_progress)
        
        return np.array(pil_img)
    
    def _draw_wireframe_tracing(self, draw, progress, animation_data):
        """Draw the wireframe tracing animation"""
        # Mock wireframe drawing - in production, use actual line data
        center_x, center_y = self.video_width // 2, self.video_height // 2
        size = min(self.video_width, self.video_height) * 0.6
        
        # Blue color for tracing
        blue_color = (0, 212, 255)  # #00D4FF
        
        # Draw bounding box
        left = center_x - size // 2
        top = center_y - size // 2
        right = center_x + size // 2
        bottom = center_y + size // 2
        
        # Animated tracing effect
        tracing_progress = min(progress * 1.2, 1.0)  # Speed up tracing
        
        if tracing_progress < 0.25:
            # Top line
            line_end = left + (right - left) * (tracing_progress * 4)
            draw.line([(left, top), (line_end, top)], fill=blue_color, width=3)
        elif tracing_progress < 0.5:
            # Right line
            draw.line([(left, top), (right, top)], fill=blue_color, width=3)
            line_end = top + (bottom - top) * ((tracing_progress - 0.25) * 4)
            draw.line([(right, top), (right, line_end)], fill=blue_color, width=3)
        elif tracing_progress < 0.75:
            # Bottom line
            draw.line([(left, top), (right, top)], fill=blue_color, width=3)
            draw.line([(right, top), (right, bottom)], fill=blue_color, width=3)
            line_end = right - (right - left) * ((tracing_progress - 0.5) * 4)
            draw.line([(right, bottom), (line_end, bottom)], fill=blue_color, width=3)
        else:
            # Complete box
            draw.rectangle([left, top, right, bottom], outline=blue_color, width=3)
            
            # Add cross lines for 3D effect
            if progress > 0.7:
                alpha = int(255 * (progress - 0.7) / 0.3)
                semi_transparent = blue_color + (alpha,)
                draw.line([(left, top), (right, bottom)], fill=semi_transparent, width=2)
                draw.line([(right, top), (left, bottom)], fill=semi_transparent, width=2)
    
    def _draw_2d_plan(self, draw, progress, animation_data):
        """Draw the 2D floor plan"""
        center_x, center_y = self.video_width // 2, self.video_height // 2
        size = min(self.video_width, self.video_height) * 0.5
        
        # Black lines for architectural drawing
        black = (0, 0, 0)
        
        # Draw main rectangle (building outline)
        left = center_x - size // 2
        top = center_y - size // 2
        right = center_x + size // 2
        bottom = center_y + size // 2
        
        # Solid walls
        wall_thickness = 5
        draw.rectangle([left, top, right, bottom], outline=black, width=wall_thickness)
        
        # Interior walls (appear with progress)
        if progress > 0.3:
            alpha = int(255 * min((progress - 0.3) / 0.3, 1.0))
            wall_color = black + (alpha,)
            
            # Vertical interior wall
            wall_x = left + (right - left) * 0.4
            draw.line([(wall_x, top), (wall_x, bottom)], fill=wall_color, width=wall_thickness)
            
            # Horizontal interior wall
            wall_y = top + (bottom - top) * 0.6
            draw.line([(left, wall_y), (wall_x, wall_y)], fill=wall_color, width=wall_thickness)
        
        # Windows and doors (appear later)
        if progress > 0.6:
            alpha = int(255 * min((progress - 0.6) / 0.4, 1.0))
            feature_color = black + (alpha,)
            
            # Windows
            window_width = 30
            # Left wall window
            window_y = center_y - 20
            draw.line([(left, window_y), (left, window_y + window_width)], 
                     fill=feature_color, width=2)
            # Right wall window
            draw.line([(right, window_y), (right, window_y + window_width)], 
                     fill=feature_color, width=2)
            
            # Door
            door_width = 20
            door_x = center_x - door_width // 2
            draw.line([(door_x, bottom), (door_x + door_width, bottom)], 
                     fill=feature_color, width=3)
        
        # Room labels (appear last)
        if progress > 0.8:
            try:
                font = ImageFont.truetype("arial.ttf", 24)
                alpha = int(255 * min((progress - 0.8) / 0.2, 1.0))
                text_color = (0, 0, 0, alpha)
                
                # Living room label
                living_x = left + (wall_x - left) // 2
                living_y = top + (wall_y - top) // 2
                draw.text((living_x, living_y), "LIVING ROOM", fill=text_color, font=font)
                
                # Kitchen label
                kitchen_x = wall_x + (right - wall_x) // 2
                kitchen_y = wall_y + (bottom - wall_y) // 2
                draw.text((kitchen_x, kitchen_y), "KITCHEN", fill=text_color, font=font)
                
            except:
                # Fallback if font not available
                pass
    
    def _draw_3d_model(self, draw, progress, animation_data):
        """Draw the 3D model extrusion and materialization"""
        center_x, center_y = self.video_width // 2, self.video_height // 2
        base_size = min(self.video_width, self.video_height) * 0.4
        
        # Calculate extrusion height based on progress
        if progress < 0.3:
            # Geometry extrusion phase
            extrusion_progress = progress / 0.3
            height = base_size * 0.8 * extrusion_progress
        else:
            height = base_size * 0.8
        
        # Draw 3D box (simplified representation)
        left = center_x - base_size // 2
        right = center_x + base_size // 2
        top = center_y - base_size // 2
        bottom = center_y + base_size // 2
        top_3d = top - height
        
        # Base rectangle
        draw.rectangle([left, top, right, bottom], outline=(100, 100, 100), width=2)
        
        # Top rectangle (3D)
        if progress > 0.1:
            top_alpha = int(255 * min((progress - 0.1) / 0.2, 1.0))
            draw.rectangle([left, top_3d, right, top], 
                         outline=(100, 100, 100, top_alpha), width=2)
        
        # Connection lines
        if progress > 0.15:
            connect_alpha = int(255 * min((progress - 0.15) / 0.15, 1.0))
            connect_color = (100, 100, 100, connect_alpha)
            draw.line([(left, top), (left, top_3d)], fill=connect_color, width=2)
            draw.line([(right, top), (right, top_3d)], fill=connect_color, width=2)
        
        # Material application (simplified)
        if progress > 0.3:
            material_progress = (progress - 0.3) / 0.7
            
            # Wall material
            if material_progress < 0.25:
                wall_alpha = int(255 * (material_progress / 0.25))
                wall_color = (180, 120, 80, wall_alpha)  # Brick color
                draw.rectangle([left, top_3d, right, bottom], 
                             outline=wall_color, fill=wall_color, width=1)
            
            # Roof material
            elif material_progress < 0.5:
                roof_alpha = int(255 * ((material_progress - 0.25) / 0.25))
                roof_color = (80, 80, 80, roof_alpha)  # Roof color
                draw.polygon([(left, top_3d), (right, top_3d), 
                            (center_x, top_3d - height * 0.3)], 
                           outline=roof_color, fill=roof_color)
            
            # Windows
            elif material_progress < 0.75:
                window_alpha = int(255 * ((material_progress - 0.5) / 0.25))
                window_color = (200, 230, 255, window_alpha)  # Glass blue
                
                # Draw some windows
                window_size = 20
                for i in range(2):
                    for j in range(2):
                        win_left = left + (i + 1) * (base_size // 3) - window_size // 2
                        win_top = top_3d + (j + 1) * (height // 3) - window_size // 2
                        draw.rectangle([win_left, win_top, 
                                      win_left + window_size, win_top + window_size],
                                     fill=window_color)
    
    def _draw_final_reveal(self, draw, progress, animation_data):
        """Draw the final enhanced 3D model"""
        # Reuse 3D model drawing but with enhancements
        self._draw_3d_model(draw, 1.0, animation_data)  # Draw complete model
        
        # Add lighting effects in final phase
        if progress > 0.5:
            # Sun rays effect
            ray_alpha = int(100 * (progress - 0.5) / 0.5)
            if ray_alpha > 0:
                center_x, center_y = self.video_width // 2, self.video_height // 2
                
                # Draw some light rays
                for i in range(5):
                    angle = (i / 5) * 360
                    length = 200
                    end_x = center_x + length * np.cos(np.radians(angle))
                    end_y = center_y + length * np.sin(np.radians(angle))
                    
                    ray_color = (255, 255, 200, ray_alpha // 2)
                    draw.line([(center_x, center_y), (end_x, end_y)], 
                             fill=ray_color, width=2)
    
    def _draw_title_card(self, draw, progress):
        """Draw the final title card"""
        center_x, center_y = self.video_width // 2, self.video_height // 2
        
        # Background overlay
        overlay_alpha = int(200 * progress)
        overlay_color = (0, 0, 0, overlay_alpha)
        draw.rectangle([0, 0, self.video_width, self.video_height], 
                      fill=overlay_color)
        
        # Title text
        try:
            title_font = ImageFont.truetype("arial.ttf", 60)
            subtitle_font = ImageFont.truetype("arial.ttf", 30)
            
            title_alpha = int(255 * progress)
            text_color = (255, 255, 255, title_alpha)
            
            # Main title
            title_text = "Architectural Animator Pro"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = center_x - title_width // 2
            title_y = center_y - 50
            
            draw.text((title_x, title_y), title_text, fill=text_color, font=title_font)
            
            # Subtitle
            subtitle_text = "Transforming Visions into Motion"
            subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = center_x - subtitle_width // 2
            subtitle_y = center_y + 30
            
            draw.text((subtitle_x, subtitle_y), subtitle_text, 
                     fill=text_color, font=subtitle_font)
                     
        except:
            # Fallback drawing
            title_color = (255, 255, 255, int(255 * progress))
            draw.text((center_x - 150, center_y - 20), "Architectural Animator Pro", 
                     fill=title_color)
    
    def _create_audio_track(self, duration):
        """Create the complete audio track with music and sound effects"""
        try:
            # This would load actual audio files in production
            # For demo, we'll create silent audio and add it later with real files
            
            # Placeholder - in production, you would:
            # 1. Load background music from assets/static/music/
            # 2. Load sound effects from assets/static/sfx/
            # 3. Mix them at appropriate timings
            
            # For now, return silent audio
            from moviepy.audio.AudioClip import AudioClip
            import numpy as np
            
            def make_silence(t):
                return np.zeros((2,))  # Stereo silence
            
            silent_audio = AudioClip(make_silence, duration=duration)
            return silent_audio
            
        except Exception as e:
            logger.warning(f"Audio creation failed: {e}. Proceeding with silent video.")
            # Return silent audio as fallback
            from moviepy.audio.AudioClip import AudioClip
            import numpy as np
            
            def make_silence(t):
                return np.zeros((2,))
                
            return AudioClip(make_silence, duration=duration)
