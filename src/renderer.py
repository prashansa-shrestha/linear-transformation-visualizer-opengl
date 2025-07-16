# Handles all rendering operations

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


class Renderer:
    """Handles all rendering operations"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = None
        self.small_font = None
    
    def init_pygame(self):
        """Initialize pygame and OpenGL"""
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Linear Transformations Visualizer")
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # OpenGL setup
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        
        glClearColor(0.05, 0.05, 0.1, 1.0)
        
        # Set up projection
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.width/self.height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
    
    def draw_transformed_grid(self, grid_lines, basis_vectors):

        """Draw the transformed grid and basis vectors"""
        glLineWidth(1)
        
        # Draw grid lines
        glColor4f(0.3, 0.5, 0.7, 0.2)
        glBegin(GL_LINES)
        for line in grid_lines:
            glVertex3f(line[0][0], line[0][1], line[0][2])
            glVertex3f(line[1][0], line[1][1], line[1][2])
        glEnd()
        


        # Draw basis vectors
        glLineWidth(4)
        
        # X axis (RED)
        glColor3f(1.0, 0.3, 0.3)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(basis_vectors[0][0], basis_vectors[0][1], basis_vectors[0][2])
        glEnd()
        
        # Y axis (GREEN)
        glColor3f(0.3, 1.0, 0.3)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(basis_vectors[1][0], basis_vectors[1][1], basis_vectors[1][2])
        glEnd()
        
        # Z axis (BLUE)
        glColor3f(0.3, 0.3, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(basis_vectors[2][0], basis_vectors[2][1], basis_vectors[2][2])
        glEnd()
        


        # Draw origin point
        glPointSize(8)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glEnd()
    
    def draw_cube(self, vertices, color=(0.5, 0.8, 1), alpha=0.7, wireframe=False):
        """Draw a cube with given vertices"""
        faces = [
            [0,1,2,3], [4,5,6,7], [0,1,5,4],
            [2,3,7,6], [0,3,7,4], [1,2,6,5]
        ]
        
        if not wireframe:
            # Draw semi-transparent cube faces
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(color[0], color[1], color[2], alpha)
            glBegin(GL_QUADS)
            for face in faces:
                for vertex in face:
                    x, y, z = vertices[vertex]
                    glVertex3f(x, y, z)
            glEnd()
            
            # Draw cube edges
            glColor3f(color[0]*0.7, color[1]*0.7, color[2]*0.7)
            glLineWidth(2)
            
            edges = [
                [0, 1], [1, 2], [2, 3], [3, 0],  # bottom face
                [4, 5], [5, 6], [6, 7], [7, 4],  # top face
                [0, 4], [1, 5], [2, 6], [3, 7]   # vertical edges
            ]
            
            glBegin(GL_LINES)
            for edge in edges:
                for vertex in edge:
                    x, y, z = vertices[vertex]
                    glVertex3f(x, y, z)
            glEnd()
            
            # Draw vertices
            glBegin(GL_POINTS)
            for vertex in vertices:
                x, y, z = vertex
                glVertex3f(x, y, z)
            glEnd()
    
    def draw_info_panel(self, transform_manager):
        """Draw the information panel"""
        current_determinant = transform_manager.get_current_determinant()
        volume_scale = abs(current_determinant)
        
        # Determine transformation type
        if abs(current_determinant) < 1e-10:
            transform_type = "SINGULAR (Non-invertible)"
            type_color = (255, 80, 80)
        elif current_determinant < 0:
            transform_type = "ORIENTATION REVERSING"
            type_color = (255, 200, 100)
        elif abs(current_determinant - 1.0) < 1e-6:
            transform_type = "ORTHOGONAL (Preserves volume)"
            type_color = (100, 255, 100)
        else:
            transform_type = "GENERAL LINEAR"
            type_color = (120, 200, 255)
        
        animation_progress_percent = transform_manager.animation_progress * 100
        
        # Create text surface
        panel_width = 450
        panel_height = 300
        text_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Draw panel background
        pygame.draw.rect(text_surface, (0, 0, 0, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(text_surface, (100, 200, 255), (0, 0, panel_width, panel_height), 2)
        
        # Render text lines
        y = 20
        line_spacing = 25
        
        text_lines = [
            ("LINEAR TRANSFORMATION VISUALIZER", self.font, (255, 255, 255)),
            ("", None, None),
            (f"Determinant: {current_determinant:.1f}", self.font, (255, 255, 100)),
            (f"Volume Scale: {volume_scale:.1f}x", self.font, (100, 255, 100)),
            (f"Transformation: {transform_type}", self.font, type_color),
            ("", None, None),
            (f"Animation State: ({animation_progress_percent:.1f}%)", self.font, (100, 255, 255)),
            ("", None, None),
            ("CONTROLS:", self.font, (200, 200, 200)),
            ("G - Toggle Animation", self.small_font, (180, 180, 180)),
            ("ESC - Exit", self.small_font, (180, 180, 180)),
        ]
        
        for text, font, color in text_lines:
            if text and font and color:
                text_render = font.render(text, True, color)
                text_surface.blit(text_render, (20, y))
            y += line_spacing if text else line_spacing // 2
        
        # Render to OpenGL
        self._render_text_surface_to_opengl(text_surface, panel_width, panel_height)
    
    def _render_text_surface_to_opengl(self, text_surface, panel_width, panel_height):
        """Helper method to render pygame surface to OpenGL"""
        texture_data = pygame.image.tostring(text_surface, 'RGBA', False)
        
        # Set up OpenGL for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth testing and enable blending
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        
        # Create and bind texture
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, panel_width, panel_height, 
                     0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Render the text panel
        glColor4f(1.0, 1.0, 1.0, 1.0)
        panel_x = 10
        panel_y = 10
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(panel_x, panel_y)
        glTexCoord2f(1, 0); glVertex2f(panel_x + panel_width, panel_y)
        glTexCoord2f(1, 1); glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glTexCoord2f(0, 1); glVertex2f(panel_x, panel_y + panel_height)
        glEnd()
        
        # Cleanup
        glDeleteTextures(1, [texture_id])
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        
        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)