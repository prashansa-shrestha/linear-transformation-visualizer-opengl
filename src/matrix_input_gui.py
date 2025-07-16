# GUI for matrix input

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np


class MatrixInputGUI:
    
    def __init__(self, callback):
        self.callback = callback
        self.matrix = None
        self.root = None

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("Linear Transformation Matrix Input")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        title_label = ttk.Label(main_frame, text="Enter Transformation Matrix",
                              font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))        

        self.entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                entry = ttk.Entry(main_frame, width=10, font=("Arial", 12))
                entry.grid(row=i+1, column=j, padx=5, pady=5)
                if i == j:
                    entry.insert(0, "1")
                else:
                    entry.insert(0, "0")
                row_entries.append(entry)
            self.entries.append(row_entries)

        preset_frame = ttk.Frame(main_frame)
        preset_frame.grid(row=4, column=0, columnspan=3, pady=20)

        presets = [
            ("Identity", np.eye(3)),
            ("Scale 2x", np.diag([2, 2, 2])),
            ("Scale XY", np.diag([2, 2, 1])),
            ("Rotate Z 90°", np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])),
            ("Rotate Y 90°", np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])),
            ("Rotate X 90°", np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])),
            ("Shear X", np.array([[1, 0.5, 0], [0, 1, 0], [0, 0, 1]])),
            ("Shear Y", np.array([[1, 0, 0], [0.5, 1, 0], [0, 0, 1]])),
            ("Reflect X", np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]]))
        ]

        for idx, (name, matrix) in enumerate(presets):
            row = idx // 3 + 1
            col = idx % 3
            btn = ttk.Button(preset_frame, text=name,
                           command=lambda m=matrix: self.set_matrix_gui(m))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Apply Transformation",
                   command=self.apply_matrix).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Reset to Identity",
                   command=self.reset_matrix).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Close",
                   command=self.close_gui).grid(row=0, column=2, padx=5)

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self.close_gui)

    def set_matrix_gui(self, matrix):
        for i in range(3):
            for j in range(3):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, f"{matrix[i,j]:.1f}")
    
    def reset_matrix(self):
        self.set_matrix_gui(np.eye(3))

    def apply_matrix(self):
        try:
            matrix = np.zeros((3, 3))
            for i in range(3):
                for j in range(3):
                    value = float(self.entries[i][j].get())
                    matrix[i, j] = value
                
            # Check if the matrix is invertible
            det = np.linalg.det(matrix)
            if abs(det) < 1e-10:
                messagebox.showwarning("Warning",
                    f"Matrix is not invertible (determinant={det:.6f})\n"
                    "The transformation will collapse the space")
                
            self.callback(matrix)
            messagebox.showinfo("Success", "Transformation applied!")

        except ValueError:
            messagebox.showerror("Error", "Invalid matrix values. Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", f"Error applying matrix")

    def close_gui(self):
        if self.root:
            self.root.destroy()
            self.root = None
    
    def show(self):
        self.create_gui()
        self.root.mainloop()