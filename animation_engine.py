import json
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

@dataclass
class AnimationPhase:
    name: str
    start_time: float
    end_time: float
    elements: List[Dict[str, Any]]

@dataclass
class CameraKeyframe:
    time: float
    position: List[float]
    target: List[float]
    fov: float
    ease_type: str = "linear"

class AnimationEngine:
    """Generates the animation sequence and 3D scene"""
    
    def __init__(self):
        self.scene_data = {}
        self.animation_phases = []
        self.camera_path = []
    
    def create_animation_sequence(self, reconstruction_data, focus_type="auto"):
        """Create complete animation sequence"""
        logger.info("Creating animation sequence...")
        
        # Determine focus type if auto
        if focus_type == "auto":
            focus_type = self._detect_focus_type(reconstruction_data)
        
        # Build scene graph
        self.scene_data = self._build_scene_graph(reconstruction_data, focus_type)
        
        # Define animation phases
        self._define_animation_phases()
        
        # Generate camera path
        self._generate_camera_path(focus_type)
        
        return {
            'scene_graph': self.scene_data,
            'animation_phases': [phase.__dict__ for phase in self.animation_phases],
            'camera_path': [kf.__dict__ for kf in self.camera_path],
            'focus_type': focus_type,
            'total_duration': 30.0  # 30 seconds
        }
    
    def _detect_focus_type(self, reconstruction_data):
        """Auto-detect if image is interior or exterior"""
        # Simple heuristic based on geometry and colors
        vertices = reconstruction_data.get('vertices', [])
        textures = reconstruction_data.get('textures', {})
        
        if len(vertices) > 10:  # More complex geometry suggests interior
            return "interior"
        else:
            return "exterior"
    
    def _build_scene_graph(self, reconstruction_data, focus_type):
        """Build hierarchical scene graph from reconstruction data"""
        scene = {
            'name': 'ArchitecturalScene',
            'children': [],
            'materials': self._create_material_library(),
            'lights': self._create_lighting_setup(focus_type)
        }
        
        # Main building structure
        building = self._create_building_structure(reconstruction_data, focus_type)
        scene['children'].append(building)
        
        # Environmental elements
        environment = self._create_environment(focus_type)
        scene['children'].append(environment)
        
        return scene
    
    def _create_building_structure(self, reconstruction_data, focus_type):
        """Create the main building structure"""
        vertices = reconstruction_data.get('vertices', [])
        faces = reconstruction_data.get('faces', [])
        textures = reconstruction_data.get('textures', {})
        
        building = {
            'type': 'building',
            'geometry': {
                'vertices': vertices,
                'faces': faces,
                'uvs': self._generate_uvs(vertices, faces)
            },
            'materials': self._assign_building_materials(textures, focus_type),
            'animation': {
                'extrusion_timing': [0.0, 0.5, 1.0],  # Normalized time points
                'material_application': [0.3, 0.6, 0.8, 1.0]
            }
        }
        
        return building
    
    def _create_environment(self, focus_type):
        """Create environmental elements based on focus type"""
        if focus_type == "exterior":
            return {
                'type': 'environment',
                'children': [
                    self._create_ground_plane(),
                    self._create_vegetation(),
                    self._create_sky()
                ]
            }
        else:
            return {
                'type': 'environment',
                'children': [
                    self._create_floor_plane(),
                    self._create_furniture(),
                    self._create_decorations()
                ]
            }
    
    def _create_ground_plane(self):
        """Create ground plane for exterior scenes"""
        return {
            'type': 'ground',
            'geometry': {
                'vertices': [[-10, -10, 0], [10, -10, 0], [10, 10, 0], [-10, 10, 0]],
                'faces': [[0, 1, 2], [0, 2, 3]]
            },
            'material': 'grass',
            'animation': {'appear_time': 0.7}
        }
    
    def _create_vegetation(self):
        """Create vegetation elements"""
        return {
            'type': 'vegetation',
            'children': [
                {
                    'type': 'tree',
                    'position': [3, 2, 0],
                    'scale': [0.8, 0.8, 0.8],
                    'animation': {'appear_time': 0.8, 'grow_duration': 0.5}
                },
                {
                    'type': 'shrub',
                    'position': [-2, 3, 0],
                    'scale': [0.5, 0.5, 0.5],
                    'animation': {'appear_time': 0.85, 'grow_duration': 0.3}
                }
            ]
        }
    
    def _create_floor_plane(self):
        """Create floor plane for interior scenes"""
        return {
            'type': 'floor',
            'geometry': {
                'vertices': [[-5, -5, 0], [5, -5, 0], [5, 5, 0], [-5, 5, 0]],
                'faces': [[0, 1, 2], [0, 2, 3]]
            },
            'material': 'wood_floor',
            'animation': {'appear_time': 0.6}
        }
    
    def _create_furniture(self):
        """Create furniture for interior scenes"""
        return {
            'type': 'furniture',
            'children': [
                {
                    'type': 'sofa',
                    'position': [1, 0, 0],
                    'rotation': [0, 0, 45],
                    'animation': {'appear_time': 0.75, 'fade_in': 0.2}
                },
                {
                    'type': 'table',
                    'position': [0, 1, 0],
                    'animation': {'appear_time': 0.8, 'fade_in': 0.2}
                }
            ]
        }
    
    def _create_decorations(self):
        """Create decorative elements"""
        return {
            'type': 'decorations',
            'children': [
                {
                    'type': 'plant',
                    'position': [2, 2, 0],
                    'animation': {'appear_time': 0.9, 'pop_effect': True}
                }
            ]
        }
    
    def _create_sky(self):
        """Create sky element"""
        return {
            'type': 'sky',
            'material': 'sky_gradient',
            'animation': {'appear_time': 0.0}
        }
    
    def _create_material_library(self):
        """Create library of PBR materials"""
        return {
            'brick': {
                'type': 'pbr',
                'albedo': [0.7, 0.3, 0.2],
                'roughness': 0.8,
                'metallic': 0.1
            },
            'concrete': {
                'type': 'pbr',
                'albedo': [0.8, 0.8, 0.8],
                'roughness': 0.9,
                'metallic': 0.0
            },
            'glass': {
                'type': 'pbr',
                'albedo': [0.9, 0.9, 1.0],
                'roughness': 0.1,
                'metallic': 0.0,
                'transparency': 0.8
            },
            'wood_floor': {
                'type': 'pbr',
                'albedo': [0.5, 0.3, 0.1],
                'roughness': 0.7,
                'metallic': 0.0
            },
            'grass': {
                'type': 'pbr',
                'albedo': [0.2, 0.6, 0.2],
                'roughness': 0.9,
                'metallic': 0.0
            }
        }
    
    def _create_lighting_setup(self, focus_type):
        """Create lighting setup based on scene type"""
        if focus_type == "exterior":
            return [
                {
                    'type': 'directional',
                    'position': [5, 5, 10],
                    'color': [1.0, 0.9, 0.8],
                    'intensity': 1.0
                },
                {
                    'type': 'ambient',
                    'color': [0.3, 0.4, 0.5],
                    'intensity': 0.4
                }
            ]
        else:
            return [
                {
                    'type': 'point',
                    'position': [2, 2, 5],
                    'color': [1.0, 0.9, 0.7],
                    'intensity': 0.8
                },
                {
                    'type': 'ambient',
                    'color': [0.4, 0.4, 0.5],
                    'intensity': 0.3
                }
            ]
    
    def _assign_building_materials(self, textures, focus_type):
        """Assign materials to building based on texture analysis"""
        dominant_colors = textures.get('dominant_colors', [[100, 100, 100]])
        
        if focus_type == "exterior":
            return {
                'walls': 'brick',
                'roof': 'concrete',
                'windows': 'glass',
                'doors': 'wood_floor'
            }
        else:
            return {
                'walls': 'concrete',
                'floor': 'wood_floor',
                'windows': 'glass',
                'furniture': 'wood_floor'
            }
    
    def _generate_uvs(self, vertices, faces):
        """Generate UV coordinates for texturing"""
        # Simple planar projection
        uvs = []
        for vertex in vertices:
            u = (vertex[0] % 10) / 10.0  # Simple repeating pattern
            v = (vertex[1] % 10) / 10.0
            uvs.append([u, v])
        return uvs
    
    def _define_animation_phases(self):
        """Define the four animation phases"""
        self.animation_phases = [
            AnimationPhase(
                name="Analytical Deconstruction",
                start_time=0.0,
                end_time=5.0,
                elements=[
                    {
                        'type': 'line_tracing',
                        'color': '#00D4FF',
                        'speed': 'fast',
                        'sound_effect': 'click'
                    },
                    {
                        'type': 'wireframe_overlay',
                        'opacity': 0.5
                    }
                ]
            ),
            AnimationPhase(
                name="2D Plan Emergence",
                start_time=5.0,
                end_time=10.0,
                elements=[
                    {
                        'type': 'plan_reveal',
                        'style': 'architectural',
                        'labels': True
                    },
                    {
                        'type': 'camera_pull_out',
                        'duration': 5.0
                    }
                ]
            ),
            AnimationPhase(
                name="3D Extrusion & Materialization",
                start_time=10.0,
                end_time=22.0,
                elements=[
                    {
                        'type': 'geometry_extrusion',
                        'duration': 3.0,
                        'easing': 'easeOutCubic'
                    },
                    {
                        'type': 'material_application',
                        'sequence': ['walls', 'roof', 'windows', 'details'],
                        'timing': [0.0, 0.3, 0.6, 0.9]
                    },
                    {
                        'type': 'environment_populate',
                        'elements': ['vegetation', 'furniture', 'decorations']
                    }
                ]
            ),
            AnimationPhase(
                name="Final Reveal & Loop",
                start_time=22.0,
                end_time=30.0,
                elements=[
                    {
                        'type': 'camera_finale',
                        'movement': 'slow_orbital'
                    },
                    {
                        'type': 'lighting_enhancement',
                        'effects': ['sun_rays', 'glow']
                    },
                    {
                        'type': 'title_card',
                        'display_time': 3.0,
                        'text': 'Architectural Animator Pro'
                    }
                ]
            )
        ]
    
    def _generate_camera_path(self, focus_type):
        """Generate camera keyframes for cinematic fly-through"""
        if focus_type == "exterior":
            self.camera_path = [
                CameraKeyframe(0.0, [0, 0, 5], [0, 0, 0], 60, "easeOutQuad"),
                CameraKeyframe(5.0, [0, 0, 10], [0, 0, 0], 45, "easeInOutQuad"),
                CameraKeyframe(10.0, [5, 5, 8], [0, 0, 0], 50, "easeInOutQuad"),
                CameraKeyframe(15.0, [8, 0, 6], [0, 0, 0], 55, "easeInOutQuad"),
                CameraKeyframe(20.0, [0, 8, 7], [0, 0, 0], 50, "easeInOutQuad"),
                CameraKeyframe(25.0, [3, 3, 12], [0, 0, 0], 40, "easeInOutQuad"),
                CameraKeyframe(30.0, [0, 0, 15], [0, 0, 0], 35, "easeInQuad")
            ]
        else:
            self.camera_path = [
                CameraKeyframe(0.0, [0, 0, 3], [0, 0, 0], 70, "easeOutQuad"),
                CameraKeyframe(5.0, [0, 0, 5], [0, 0, 0], 60, "easeInOutQuad"),
                CameraKeyframe(10.0, [2, 0, 4], [0, 0, 0], 65, "easeInOutQuad"),
                CameraKeyframe(15.0, [0, 2, 4], [0, 0, 0], 65, "easeInOutQuad"),
                CameraKeyframe(20.0, [-2, -1, 3.5], [0, 0, 0], 70, "easeInOutQuad"),
                CameraKeyframe(25.0, [1, 1, 6], [0, 0, 0], 55, "easeInOutQuad"),
                CameraKeyframe(30.0, [0, 0, 7], [0, 0, 0], 50, "easeInQuad")
            ]
