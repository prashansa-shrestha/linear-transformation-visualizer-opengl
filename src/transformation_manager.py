# Handles all transformation-related calculations and animations

import numpy as np


class TransformationManager:
    """Handles all transformation-related calculations and animations"""
    
    def __init__(self):
        self.animation_speed = 0.015
        self.animation_progress = 0
        self.is_animating = False
        
        # Initialize original objects
        self.original_cube = np.array([
            [0,0,0],[1,0,0],[1,1,0],[0,1,0],
            [0,0,1],[1,0,1],[1,1,1],[0,1,1]
        ])
        
        self.original_basis = np.array([
            [2,0,0], [0,2,0], [0,0,2]
        ])
        
        # Current state objects
        self.transformed_cube = self.original_cube.copy()
        self.current_cube = self.original_cube.copy()
        self.transformed_basis = self.original_basis.copy()
        self.current_basis = self.original_basis.copy()
        
        self.transform_matrix = np.eye(3)
        self.original_determinant = 1.0
        self.transformed_determinant = 1.0
    
    def apply_transformation(self, matrix):
        """Apply transformation matrix to all objects"""
        self.transform_matrix = matrix
        
        # Transform cube vertices
        self.transformed_cube = np.array([matrix @ vertex for vertex in self.original_cube])
        
        # Transform basis vectors
        self.transformed_basis = np.array([matrix @ basis for basis in self.original_basis])
        
        # Calculate determinants
        self.original_determinant = np.linalg.det(np.eye(3))
        self.transformed_determinant = np.linalg.det(matrix)
        
        # Start animation
        self.animation_progress = 0
        self.is_animating = True
    
    def update_animation(self):
        """Update animation progress"""
        if self.is_animating:
            self.animation_progress += self.animation_speed
            
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.is_animating = False
            
            t = self.ease_in_out(self.animation_progress)
            
            # Animate cube vertices
            self.current_cube = (1-t) * self.original_cube + t * self.transformed_cube
            # Animate basis vectors
            self.current_basis = (1-t) * self.original_basis + t * self.transformed_basis
    
    def ease_in_out(self, t):
        """Smooth ease in/out function"""
        return t * t * (3.0 - 2.0 * t)
    
    def get_current_determinant(self):
        """Get the current determinant based on animation state"""
        if self.is_animating:
            t = self.ease_in_out(self.animation_progress)
            return (1 - t) * self.original_determinant + t * self.transformed_determinant
        elif not np.allclose(self.transform_matrix, np.eye(3)):
            return self.transformed_determinant
        return self.original_determinant