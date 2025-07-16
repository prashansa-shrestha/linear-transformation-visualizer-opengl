# Manages grid generation and transformation

import numpy as np


class GridManager:
    """Manages grid generation and transformation"""
    
    def __init__(self, grid_size=8, grid_spacing=1):
        self.grid_size = grid_size
        self.grid_spacing = grid_spacing
        
        self.original_grid_lines = self.generate_grid_lines()
        self.transformed_grid_lines = self.original_grid_lines.copy()
        self.current_grid_lines = self.original_grid_lines.copy()
    
    def generate_grid_lines(self):
        """Generate grid lines for all three planes"""
        lines = []
        grid_range = self.grid_size
        step = self.grid_spacing
        
        # XY plane lines
        for i in range(-grid_range, grid_range+1, step):
            lines.append([[i, -grid_range, 0], [i, grid_range, 0]])
            lines.append([[-grid_range, i, 0], [grid_range, i, 0]])
        
        # XZ plane lines
        for i in range(-grid_range, grid_range+1, step):
            lines.append([[i, 0, -grid_range], [i, 0, grid_range]])
            lines.append([[-grid_range, 0, i], [grid_range, 0, i]])
        
        # YZ plane lines
        for i in range(-grid_range, grid_range+1, step):
            lines.append([[0, i, -grid_range], [0, i, grid_range]])
            lines.append([[0, -grid_range, i], [0, grid_range, i]])
        
        return np.array(lines)
    
    def apply_transformation(self, matrix):
        """Apply transformation to grid lines"""
        self.transformed_grid_lines = np.array([
            [matrix @ line[0], matrix @ line[1]] for line in self.original_grid_lines
        ])
    
    def update_animation(self, t):
        """Update grid animation"""
        self.current_grid_lines = (1-t) * self.original_grid_lines + t * self.transformed_grid_lines