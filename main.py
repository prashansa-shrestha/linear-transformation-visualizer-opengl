import math  # Add this import
import numpy as np
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import ttk,messagebox
from math import cos,sin
from OpenGL.GL import *
from OpenGL.GLU import *
import threading

class MatrixInputGUI:
    def __init__(self, callback):
        self.callback=callback
        # what does callback mean
        self.matrix=None
        self.root=None

    def create_gui(self):
        self.root=tk.Tk()
        self.root.title("Linear Transformation Matrix Input")
        self.root.geometry("500x400")
        self.root.resizable(False,False)

        main_frame=ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0,column=0,sticky="nsew")
        
        title_label=ttk.Label(main_frame, text="Enter Transformation Matrix",
                              font=("Arial",14,"bold"))
        title_label.grid(row=0,column=0,columnspan=3, pady=(0,20))        

        self.entries=[]
        for i in range(3):
            row_entries=[]
            for j in range(3):
                entry=ttk.Entry(main_frame, width=10, font=("Arial",12))
                entry.grid(row=i+1, column=j,padx=5,pady=5)
                if i==j:
                    entry.insert(0,"1")
                else:
                    entry.insert(0,"0")
                row_entries.append(entry)
            self.entries.append(row_entries)

        preset_frame=ttk.Frame(main_frame)
        preset_frame.grid(row=4,column=0,columnspan=3,pady=20)

        presets=[
            ("Identity",np.eye(3)),
            ("Scale 2x",np.diag([2,2,2])),
            ("Scale XY",np.diag([2,2,1])),
            ("Rotate Z 90°",np.array([[0,-1,0],[1,0,0],[0,0,1]])),
            ("Rotate Y 90°",np.array([[0,0,1],[0,1,0],[-1,0,0]])),
            ("Rotate X 90°",np.array([[1,0,0],[0,0,-1],[0,1,0]])),
            ("Shear X",np.array([[1,0.5,0],[0,1,0],[0,0,1]])),
            ("Shear Y",np.array([[1,0,0],[0.5,1,0],[0,0,1]])),
            ("Reflect X",np.array([[-1,0,0],[0,1,0],[0,0,1]]))
        ]

        for idx, (name,matrix) in enumerate(presets):
            row=idx//3+1
            col=idx%3
            btn=ttk.Button(preset_frame, text=name,
                           command=lambda m=matrix: self.set_matrix(m))
            btn.grid(row=row,column=col,padx=5,pady=5,sticky='ew')
        
        button_frame=ttk.Frame(main_frame)
        button_frame.grid(row=5,column=0, columnspan=3,pady=20)

        ttk.Button(button_frame, text="Apply Transformation",
                   command=self.apply_matrix).grid(row=0,column=0,padx=5)
        ttk.Button(button_frame, text="Reset to Identity",
                   command=self.reset_matrix).grid(row=0,column=1,padx=5)
        ttk.Button(button_frame, text="Close",
                   command=self.close_gui).grid(row=0,column=2,padx=5)

        info_text=("The unit cube will be positioned with one corner at origin (0,0,0)\n and externd to (1,1,1) in the first octant.\n The entire coordinate space will transform according to your matrix")
        info_label=ttk.Label(main_frame, text=info_text,
                             font=("Arial",10),foreground="gray")
        info_label.grid(row=6,column=0,columnspan=3,pady=10)

        self.root.update_idletasks()
        x=(self.root.winfo_screenwidth()//2)-(500//2)
        y=(self.root.winfo_screenheight()//2)-(400//2)
        self.root.geometry(f"500x400+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW",self.close_gui)



    def set_matrix(self,matrix):
        for i in range(3):
            for j in range(3):
                self.entries[i][j].delete(0,tk.END)
                self.entries[i][j].insert(0,f"{matrix[i,j]:.3f}")
    
    def reset_matrix(self):
        self.set_matrix(np.eye(3))

    def apply_matrix(self):
        try:
            matrix=np.zeros((3,3))
            for i in range(3):
                for j in range(3):
                    value=float(self.entries[i][j].get())
                    matrix[i,j]=value
                
            #checking if the matrix is invertible
            det=np.linalg.det(matrix)
            if abs(det)<1e-10:
                messagebox.showwarning("Warning",
                    f"Matrix is not invertible (determinant={det:.6f})\n"
                    "The transformation will collapse the space")
                
            self.callback(matrix)
            messagebox.showinfo("Sucess", "Transformation applied!")

        except ValueError:
            messagebox.showerror("Error","Invalid matrix values. Please enter valid numbers")

        except Exception as e:
            messagebox.showerror("Error",f"Error applying matrix")


    def close_gui(self):
        if self.root:
            self.root.destroy()
            self.root=None
    
    def show(self):
        self.create_gui()
        self.root.mainloop()

class LinearTransformationVisualizer:
    def __init__(self):
        self.width=1400
        self.height=900

        self.camera_distance=8
        self.camera_angle_x=25
        self.camera_angle_y=45
        
        self.animation_speed=0.015
        self.animation_progress=0
        self.is_animating=False

        self.original_cube=np.array([
            [0,0,0],[1,0,0],[1,1,0],[0,1,0],
            [0,0,1],[1,0,1],[1,1,1],[0,1,1]
        ])

        self.transformed_cube=self.original_cube.copy()
        self.current_cube=self.original_cube.copy()

        self.transform_matrix=np.eye(3)
        self.original_determinant=1.0
        self.transformed_determinant=1.0

        self.grid_size=8
        self.grid_spacing=1
        
        self.original_grid_lines=self.generate_grid_lines()
        self.transformed_grid_lines=self.original_grid_lines.copy()
        self.current_grid_lines=self.original_grid_lines.copy()

        #original basis vectors
        self.original_basis=np.array([
            [2,0,0],
            [0,2,0],
            [0,0,2]
        ])

        self.transformed_basis=self.original_basis.copy()
        self.current_basis=self.original_basis.copy()

        self.mouse_drag=False
        self.last_mouse_pos=[0,0]

        self.gui=None
        self.gui_thread=None

    def generate_grid_lines(self):
        lines=[]

        grid_range=self.grid_size
        step=self.grid_spacing

        #XY plane lines
        for i in range(-grid_range, grid_range+1,step):
            #lines parallel to X axis
            lines.append([[i,-grid_range,0],[i,grid_range,0]])
            #lines parallel to Y axis
            lines.append([[-grid_range,i,0],[grid_range,i,0]])

        #XZ plane lines
        for i in range(-grid_range,grid_range+1,step):
            #line parallel to X axis
            lines.append([[i,0,-grid_range],[i,0,grid_range]])
            #line parallel to Z axis
            lines.append([[-grid_range,0,i],[grid_range,0,i]])

        #YZ plane lines
        for i in range(-grid_range,grid_range+1,step):
            #line parallel to Y axis
            lines.append([[0,i,-grid_range],[0,i,grid_range]])
            #line parallel to Z axis
            lines.append([[0,-grid_range,i],[0,grid_range,i]])

        return np.array(lines)
    
    def init_pygame(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((self.width,self.height),DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Linear Transformations Visualizer")

        # Initialize fonts for the info panel
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glClearColor(0.05,0.05,0.1,1.0)

        #defining the camera lens

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45,(self.width/self.height),0.1,50.0)
        #defining the object and the camera
        glMatrixMode(GL_MODELVIEW)

    def set_camera(self):
        glLoadIdentity()

        #x_c_angle=latitude
        #y_c_angle=longitutude
        x_c_angle=math.radians(self.camera_angle_x)
        y_c_angle=math.radians(self.camera_angle_y)
        # z_c_angle=math.radians(self.camera_angle_z)

        #how far left or right=sin(y_c_angle)
        #how far front or back=cos(y_c_angle) and cos(x_c_angle)
        #how far you've tilted up or down (x_c_angle)
        r=self.camera_distance
                
        horizontal_radius=r*cos(x_c_angle)
        vertical_height=r*sin(x_c_angle)

        x=horizontal_radius*sin(y_c_angle)
        y=vertical_height
        z=horizontal_radius*cos(y_c_angle)

        gluLookAt(x,y,z,0,0,0,0,1,0)

    def draw_transformed_grid(self):
        #line thickness
        glLineWidth(1)

        # #drawing original grid linesss
        # #color of the lines
        # glColor4f(0.3,0.3,0.3,0.4)
        # glBegin(GL_LINES)
        # for line in self.original_grid_lines:
        #     glVertex3f(line[0][0],line[0][1],line[0][2])
        #     glVertex3f(line[1][0],line[1][1],line[1][2])
        # glEnd()

        #drawing transformed grid linesss
        glColor4f(0.6,0.8,1.0,0.8)
        glBegin(GL_LINES)
        for line in self.current_grid_lines:
            glVertex3f(line[0][0],line[0][1],line[0][2])
            glVertex3f(line[1][0],line[1][1],line[1][2])
        glEnd()

             # highlighting the coordinate axes
        basis_vectors = self.current_basis
        
        glLineWidth(2)

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

        #Drawing origin point

        glPointSize(8)
        glColor3f(1.0,1.0,1.0)
        glBegin(GL_POINTS)
        glVertex3f(0,0,0)
        glEnd()

    def draw_cube(self, vertices, color=(0.5,0.8,1),alpha=0.7,wireframe=False):

        #defining cube faces
        faces=[
            [0,1,2,3],
            [4,5,6,7],
            [0,1,5,4],
            [2,3,7,6],
            [0,3,7,4],
            [1,2,6,5]
        ]

        if not wireframe:
            
            #drawing semi-transparent cube faces
            glColor4f(color[0],color[1],color[2],alpha)
            glBegin(GL_QUADS)
            #draws the whole cube
            for face in faces:
                #draws each face
                for vertex in face:
                    x_coordinate=vertices[vertex][0]
                    y_coordinate=vertices[vertex][1]
                    z_coordinate=vertices[vertex][2]
                    
                    glVertex3f(x_coordinate,y_coordinate,z_coordinate)

            glEnd()

        
            #draw cube edges
            glColor3f(color[0]*0.7,color[1]*0.7,color[2]*0.7)
            glLineWidth(2)

            edges=[
                [0, 1], [1, 2], [2, 3], [3, 0],  # bottom face
                [4, 5], [5, 6], [6, 7], [7, 4],  # top face
                [0, 4], [1, 5], [2, 6], [3, 7]   # vertical edges
            ]

            glBegin(GL_LINES)
            for edge in edges:
                for vertex in edge:
                    x=vertices[vertex][0]
                    y=vertices[vertex][1]
                    z=vertices[vertex][2]
                    glVertex3f(x,y,z)
            glEnd()

            #drawing vertices
            glBegin(GL_POINTS)
            for vertex in vertices:
                x=vertex[0]
                y=vertex[1]
                z=vertex[2]
                glVertex3f(x,y,z)
            glEnd()

    def apply_transformation(self,matrix):
        #applying transformation matrix to cube, grid and basis vectors
        self.transform_matrix=matrix
        
        #transforming cube vertices
        self.transformed_cube=np.array([matrix@vertex for vertex in self.original_cube])
        
        #transforming basis
        self.transformed_basis=np.array([matrix@basis for basis in self.original_basis])
        
        #transforming grid
        self.transformed_grid_lines=np.array([
            [matrix@line[0],matrix@line[1]] for line in self.original_grid_lines
        ])
        
        #calculate determinants
        self.original_determinant=np.linalg.det(np.eye(3))
        self.transformed_determinant=np.linalg.det(matrix)

        #start animation
        self.animation_progress=0
        self.is_animating=True

    def update_animation(self):
        if self.is_animating:
            self.animation_progress+=self.animation_speed
        
            if self.animation_progress>=1.0:
                self.animation_progress=1.0
                self.is_animating=False

            t=self.ease_in_out(self.animation_progress)

            #animation of cube vertices
            self.current_cube=(1-t)*self.original_cube + t*self.transformed_cube
            #animation of basis vectors
            self.current_basis=(1-t)*self.original_basis+t*self.transformed_basis
            #animation of grid lines
            self.current_grid_lines=(1-t)*self.original_grid_lines+t*self.transformed_grid_lines

    #smooth ease in function
    def ease_in_out(self,t):
        return t*t*(3.0-2.0*t)
 

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
        text_lines.extend([
            ("", None, None),  # Empty line
            (f"Determinant: {current_determinant:.1f}", self.font, (255, 255, 100)),
            (f"Volume Scale: {volume_scale:.1f}x", self.font, (100, 255, 100)),
            (f"Type: {transform_type}", self.font, type_color),
            ("", None, None),  # Empty line
            (f"Animation: ({animation_progress_percent:.1f}%)", self.font, (100, 255, 255)),
            ("", None, None),  # Empty line
            ("CONTROLS:", self.font, (200, 200, 200)),
            ("G - Toggle Animation", self.small_font, (180, 180, 180)),
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
        
    def handle_mouse_button(self,event):
        if event.type==MOUSEBUTTONDOWN:
            #left click
            if event.button==1:
                self.mouse_drag=True #set the mouse drag flag
                self.last_mouse_pos=event.pos #records where the mouse button is pressed
            elif event.button==4:
                self.camera_distance=max(3,self.camera_distance-0.5)
            elif event.button==5:
                self.camera_distance=min(20,self.camera_distance+0.5)
        elif event.type==MOUSEBUTTONUP:
            if event.button==1:
                self.mouse_drag=False
    
    def handle_mouse_motion(self, event):
        if self.mouse_drag:
            current_pos = event.pos
            dx = current_pos[0] - self.last_mouse_pos[0]
            dy = current_pos[1] - self.last_mouse_pos[1]
            
            self.camera_angle_y += dx * 0.5
            self.camera_angle_x += dy * 0.5
            
            # Clamp vertical angle
            self.camera_angle_x = max(-89, min(89, self.camera_angle_x))
            
            self.last_mouse_pos = current_pos

    def show_matrix_gui(self):
        # Check if GUI is already running
        if self.gui_thread and self.gui_thread.is_alive():
            return
        #gui_callback = a function that responds to gui events
        def gui_callback(matrix):
            self.apply_transformation(matrix)

        #create gui
        self.gui=MatrixInputGUI(gui_callback)
        #prepare to run gui in a thread
        self.gui_thread=threading.Thread(target=self.gui.show)
        #marks the gui as a background task
        self.gui_thread.daemon=True
        #start the gui as a thread
        self.gui_thread.start()

    def run(self):
        self.init_pygame()

        clock=pygame.time.Clock()
        running=True

        print("Linear Transformations Visualizer-First Octant Unit Cube")
        print("="*60)
        print("Controls:")
        print("G: Open transformation matrix GUI")
        print("R: reset to identity matrix")
        print("Mouse drag: Rotate Camera")
        print("Mouse wheel: Zoom in/out")
        print("ESC: Exit")
        print("\n The unit cube startsa t origin (0,0,0) extending to (1,1,1)")
        print("Watch how the entire coordinate space transforms!")

        while running:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False
                elif event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_g: #g is pressed
                        self.show_matrix_gui()
                    elif event.key==pygame.K_r:
                        self.apply_transformation(np.eye(3))
                    elif event.key==pygame.K_ESCAPE:
                        running=False
                elif event.type==pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event)
                elif event.type in [pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP]:
                    self.handle_mouse_button(event)

            self.update_animation()

            #clear screen
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            #set up camera
            self.set_camera()

            #draw scene
            self.draw_transformed_grid()

            #if the final cube is different from the original
            # draw original cube (semi-transparent wireframe)
            if self.is_animating or not np.allclose(self.transform_matrix, np.eye(3)):
                self.draw_cube(self.original_cube, color=(0.8,0.8,0.8),alpha=0.3, wireframe=True)

            #draw current cube
            self.draw_cube(self.current_cube,color=(1.0,0.6,0.2),alpha=0.8)

            # #draw info panel
            self.draw_info_panel()

            pygame.display.flip()
            clock.tick(60)
        
        #clean up GIU
        if self.gui and self.gui.root:
            self.gui.close_gui()

        pygame.quit()

def main():
    try:
        visualizer=LinearTransformationVisualizer()
        visualizer.run()

    except Exception as e:
        print(f"Error running viusalizer: {e}")
        print("Make sure you have the required packages installed:")
        print("pip install pygame PyOpenGL PyOpenGL_accelerate numpy")

if __name__=="__main__":
    main()