# linear_transformation_visualizer.py
# Main application class that coordinates all components

import pygame
from pygame.locals import *
import numpy as np
from OpenGL.GL import *
import threading

from transformation_manager import TransformationManager
from grid_manager import GridManager
from camera import Camera
from renderer import Renderer
from matrix_input_gui import MatrixInputGUI


class LinearTransformationVisualizer:
    """Main application class that coordinates all components"""
    
    def __init__(self):
        self.width = 1400
        self.height = 900
        
        # Initialize components
        self.transform_manager = TransformationManager()
        self.grid_manager = GridManager()
        self.camera = Camera()
        self.renderer = Renderer(self.width, self.height)
        
        # GUI components
        self.gui = None
        self.gui_thread = None

    def show_matrix_gui(self):
        """Show the matrix input GUI"""
        if self.gui_thread and self.gui_thread.is_alive():
            return
        
        def gui_callback(matrix):
            self.transform_manager.apply_transformation(matrix)
            self.grid_manager.apply_transformation(matrix)

        self.gui = MatrixInputGUI(gui_callback)
        self.gui_thread = threading.Thread(target=self.gui.show)
        self.gui_thread.daemon = True
        self.gui_thread.start()

    def run(self):
        """Main application loop"""
        self.renderer.init_pygame()
        
        clock = pygame.time.Clock()
        running = True

        print("Linear Transformations Visualizer - First Octant Unit Cube")
        print("=" * 60)
        print("Controls:")
        print("G: Open transformation matrix GUI")
        print("R: Reset to identity matrix")
        print("Mouse drag: Rotate Camera")
        print("Mouse wheel: Zoom in/out")
        print("ESC: Exit")
        print("\nThe unit cube starts at origin (0,0,0) extending to (1,1,1)")
        print("Watch how the entire coordinate space transforms!")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.show_matrix_gui()
                    elif event.key == pygame.K_r:
                        self.transform_manager.apply_transformation(np.eye(3))
                        self.grid_manager.apply_transformation(np.eye(3))
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.camera.handle_mouse_motion(event)
                elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                    self.camera.handle_mouse_button(event)

            # Update animations
            self.transform_manager.update_animation()
            if self.transform_manager.is_animating:
                t = self.transform_manager.ease_in_out(self.transform_manager.animation_progress)
                self.grid_manager.update_animation(t)

            # Clear screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Set up camera
            self.camera.set_camera()

            # Draw scene
            self.renderer.draw_transformed_grid(
                self.grid_manager.current_grid_lines,
                self.transform_manager.current_basis
            )

            # Draw cubes
            if (self.transform_manager.is_animating or 
                not np.allclose(self.transform_manager.transform_matrix, np.eye(3))):
                # Draw original cube (wireframe/ghost) when transformation is active
                self.renderer.draw_cube(
                    self.transform_manager.original_cube, 
                    color=(0.8, 0.8, 0.8), 
                    alpha=0.3, 
                    wireframe=True
                )

            # Draw current/transformed cube
            self.renderer.draw_cube(
                self.transform_manager.current_cube,
                color=(1.0, 0.718, 0.2),
                alpha=0.7,
                wireframe=False
            )

            # Draw information panel
            self.renderer.draw_info_panel(self.transform_manager)

            # Update display
            pygame.display.flip()
            clock.tick(60)

        # Cleanup
        if self.gui and self.gui.root:
            self.gui.close_gui()
        pygame.quit()


if __name__ == "__main__":
    visualizer = LinearTransformationVisualizer()
    visualizer.run()