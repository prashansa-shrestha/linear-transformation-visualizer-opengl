import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

class LinearTransformationVisualizer:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        
        self.width = 800
        self.height = 600
        
        # Create OpenGL display
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Linear Transformation Visualizer")
        
        # Initialize OpenGL
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.2, 1.0)
        
        # Set up perspective
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width/self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Initialize transformation data
        self.transform_matrix = np.eye(3)
        self.original_determinant = 1.0
        self.transformed_determinant = 1.0
        self.is_animating = False
        self.animation_progress = 0.0
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        print("Initialization complete")
        print(f"Display mode: {pygame.display.get_surface().get_flags()}")
        print(f"OpenGL version: {glGetString(GL_VERSION).decode()}")
    
    def ease_in_out(self, t):
        """Simple easing function"""
        return t * t * (3.0 - 2.0 * t)
    
    def draw_3d_scene(self):
        """Draw a simple 3D scene"""
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)
        
        # Draw a simple cube
        glBegin(GL_QUADS)
        # Front face (red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        
        # Back face (green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0)
        
        # Top face (blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0)
        
        # Bottom face (yellow)
        glColor3f(1.0, 1.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        
        # Right face (purple)
        glColor3f(1.0, 0.0, 1.0)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(1.0, -1.0, 1.0)
        
        # Left face (cyan)
        glColor3f(0.0, 1.0, 1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glEnd()
    
    def draw_info_panel(self):
        """Draw the info panel with proper text rendering"""
        # Calculate current determinant
        current_determinant = self.original_determinant
        if self.is_animating:
            t = self.ease_in_out(self.animation_progress)
            current_determinant = (1 - t) * self.original_determinant + t * self.transformed_determinant
        elif not np.allclose(self.transform_matrix, np.eye(3)):
            current_determinant = self.transformed_determinant
        
        volume_scale = abs(current_determinant)
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
        
        animation_status = "ANIMATING" if self.is_animating else "STATIC"
        animation_progress_percent = self.animation_progress * 100
        
        # Create a pygame surface for the text overlay
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
            ("", None, None),  # Empty line
            ("TRANSFORMATION MATRIX:", self.font, (200, 200, 200)),
        ]
        
        # Add matrix rows
        for row in self.transform_matrix:
            text_lines.append((f"[{row[0]:6.3f} {row[1]:6.3f} {row[2]:6.3f}]", self.small_font, (230, 230, 230)))
        
        text_lines.extend([
            ("", None, None),  # Empty line
            (f"Determinant: {current_determinant:.6f}", self.font, (255, 255, 100)),
            (f"Volume Scale: {volume_scale:.3f}x", self.font, (100, 255, 100)),
            (f"Type: {transform_type}", self.font, type_color),
            ("", None, None),  # Empty line
            (f"Animation: {animation_status} ({animation_progress_percent:.1f}%)", self.font, (100, 255, 255)),
            ("", None, None),  # Empty line
            ("CONTROLS:", self.font, (200, 200, 200)),
            ("G - Toggle Animation", self.small_font, (180, 180, 180)),
            ("R - Reset to Identity", self.small_font, (180, 180, 180)),
            ("T - Test Transformation", self.small_font, (180, 180, 180)),
            ("ESC - Exit", self.small_font, (180, 180, 180)),
        ])
        
        for text, font, color in text_lines:
            if text and font and color:
                text_render = font.render(text, True, color)
                text_surface.blit(text_render, (20, y))
            y += line_spacing if text else line_spacing // 2
        
        # Convert pygame surface to OpenGL texture
        texture_data = pygame.image.tostring(text_surface, 'RGBA', False)  # No flip here!
        
        # Set up OpenGL for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)  # Standard screen coordinates
        
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
    

    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        print("Starting main loop...")
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        # Reset transformation
                        self.transform_matrix = np.eye(3)
                        self.original_determinant = 1.0
                        self.transformed_determinant = 1.0
                        self.is_animating = False
                        self.animation_progress = 0.0
                        print("Transformation reset")
                    elif event.key == pygame.K_g:
                        # Toggle animation for testing
                        self.is_animating = not self.is_animating
                        if self.is_animating:
                            self.animation_progress = 0.0
                        print(f"Animation toggled: {self.is_animating}")
                    elif event.key == pygame.K_t:
                        # Test transformation
                        self.transform_matrix = np.array([
                            [2.0, 0.5, 0.0],
                            [0.0, 1.5, 0.0],
                            [0.0, 0.0, 1.0]
                        ])
                        self.transformed_determinant = np.linalg.det(self.transform_matrix)
                        print("Applied test transformation")
            
            # Update animation
            if self.is_animating:
                self.animation_progress += 0.01
                if self.animation_progress >= 1.0:
                    self.animation_progress = 1.0
                    self.is_animating = False
            
            # Clear screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Draw 3D scene
            self.draw_3d_scene()
            
            # Draw info panel
            self.draw_info_panel()
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
        
        print("Exiting...")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        visualizer = LinearTransformationVisualizer()
        visualizer.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)