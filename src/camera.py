# Manages camera positioning and controls

import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import cos, sin


class Camera:
    """Manages camera positioning and controls"""
    
    def __init__(self):
        self.distance = 8
        self.angle_x = 25
        self.angle_y = 45
        self.mouse_drag = False
        self.last_mouse_pos = [0, 0]
    
    def set_camera(self):
        """Set up camera position"""
        glLoadIdentity()
        
        x_c_angle = math.radians(self.angle_x)
        y_c_angle = math.radians(self.angle_y)
        
        r = self.distance
        horizontal_radius = r * cos(x_c_angle)
        vertical_height = r * sin(x_c_angle)
        
        x = horizontal_radius * sin(y_c_angle)
        y = vertical_height
        z = horizontal_radius * cos(y_c_angle)
        
        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)
    
    def handle_mouse_button(self, event):
        """Handle mouse button events"""
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_drag = True
                self.last_mouse_pos = event.pos
            elif event.button == 4:
                self.distance = max(3, self.distance - 0.5)
            elif event.button == 5:
                self.distance = min(20, self.distance + 0.5)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_drag = False
    
    def handle_mouse_motion(self, event):
        """Handle mouse motion for camera rotation"""
        if self.mouse_drag:
            current_pos = event.pos
            dx = current_pos[0] - self.last_mouse_pos[0]
            dy = current_pos[1] - self.last_mouse_pos[1]
            
            self.angle_y += dx * 0.5
            self.angle_x += dy * 0.5
            
            # Clamp vertical angle
            self.angle_x = max(-89, min(89, self.angle_x))
            
            self.last_mouse_pos = current_pos