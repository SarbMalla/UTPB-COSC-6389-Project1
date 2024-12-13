import tkinter as tk
from tkinter import ttk
import numpy as np
import random
import colorsys

class GraphColoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Coloring Solver")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f0f0")

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))

        # Frame for input and controls
        control_frame = ttk.Frame(root, padding="20")
        control_frame.pack(fill=tk.X)

        # Number of vertices input
        ttk.Label(control_frame, text="Number of Vertices:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.vertex_entry = ttk.Entry(control_frame, width=10)
        self.vertex_entry.grid(row=0, column=1, padx=5, pady=5)

        # Solver selection dropdown
        ttk.Label(control_frame, text="Solver:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.solver_var = tk.StringVar(value="Backtracking")
        self.solver_dropdown = ttk.Combobox(control_frame, textvariable=self.solver_var, values=["Backtracking", "Ant Colony Optimization"], state="readonly")
        self.solver_dropdown.grid(row=0, column=3, padx=5, pady=5)

        # Create graph button
        self.create_button = ttk.Button(control_frame, text="Create Graph", command=self.create_graph)
        self.create_button.grid(row=0, column=4, padx=5, pady=5)

        # Canvas for graph visualization
        self.canvas = tk.Canvas(root, width=500, height=400, bg="white", relief=tk.RAISED, borderwidth=2)
        self.canvas.pack(pady=10)

        # Control buttons frame
        button_frame = ttk.Frame(root, padding="20")
        button_frame.pack(fill=tk.X)

        # Solve and reset buttons
        self.solve_button = ttk.Button(button_frame, text="Find Solution", command=self.solve_graph_coloring, state=tk.DISABLED)
        self.solve_button.grid(row=0, column=0, padx=5)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_graph)
        self.reset_button.grid(row=0, column=1, padx=5)

        # Status and generation information
        status_frame = ttk.Frame(root, padding="20")
        status_frame.pack(fill=tk.X)

        self.generation_label = ttk.Label(status_frame, text="Iterations: 0")
        self.generation_label.pack(side=tk.LEFT)

        self.solution_label = ttk.Label(status_frame, text="", foreground="green")
        self.solution_label.pack(side=tk.LEFT, padx=10)

        # Initialize variables
        self.graph = None
        self.n = 0
        self.max_colors = 4  # Default maximum colors
        self.positions = []

    def create_graph(self):
        try:
            self.n = int(self.vertex_entry.get())
            if self.n < 3:
                raise ValueError("Number of vertices must be at least 3.")

            # Initialize the adjacency matrix with zeros
            self.graph = np.zeros((self.n, self.n), dtype=int)

            # Create random edges
            num_edges_to_add = int(self.n * 2)  # Adjust this number to add more edges
            for _ in range(num_edges_to_add):
                v1, v2 = random.sample(range(self.n), 2)
                while self.graph[v1][v2] == 1 or v1 == v2:  # Ensure no self-loop and no duplicate edges
                    v1, v2 = random.sample(range(self.n), 2)
                self.graph[v1][v2] = 1
                self.graph[v2][v1] = 1  # Since the graph is undirected

            # Calculate vertex positions for visualization
            radius = 180
            center_x, center_y = 250, 200
            self.positions = [
                (
                    center_x + radius * np.cos(2 * np.pi * i / self.n),
                    center_y + radius * np.sin(2 * np.pi * i / self.n),
                )
                for i in range(self.n)
            ]

            # Reset the canvas and UI elements
            self.canvas.delete("all")
            self.solution_label.config(text="")
            self.generation_label.config(text="Iterations: 0")
            self.draw_graph()

            # Enable solve button
            self.solve_button.config(state=tk.NORMAL)

        except ValueError as e:
            self.solution_label.config(text=f"Error: {e}", foreground="red")

    def generate_distinct_colors(self, num_colors):
        """Generate visually distinct colors."""
        colors = []
        for i in range(num_colors):
            hue = i / num_colors
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.8)
            color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            colors.append(color)
        return colors

    def draw_graph(self, colors=None):
        """Draws the graph with optional vertex coloring."""
        self.canvas.delete("all")

        # Generate color palette
        color_palette = self.generate_distinct_colors(self.max_colors)

        # Draw edges
        for i in range(self.n):
            for j in range(i+1, self.n):  # Avoid duplicate edges
                if self.graph[i][j] == 1:
                    x1, y1 = self.positions[i]
                    x2, y2 = self.positions[j]
                    self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=2)

        # Draw vertices
        for i, (x, y) in enumerate(self.positions):
            # Use provided colors or random colors
            if colors is not None:
                color = color_palette[colors[i]]
            else:
                color = color_palette[random.randint(0, self.max_colors - 1)]

            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, 
                                    fill=color, outline="black", width=2)
            self.canvas.create_text(x, y, text=str(i), fill="white", font=("Arial", 10, "bold"))

    def reset_graph(self):
        """Reset the graph and UI elements."""
        self.canvas.delete("all")
        self.solution_label.config(text="")
        self.generation_label.config(text="Iterations: 0")
        self.solve_button.config(state=tk.DISABLED)
        self.vertex_entry.delete(0, tk.END)

    def is_safe_color(self, vertex, color, colors):
        """Check if a color is safe for the given vertex."""
        for i in range(self.n):
            if self.graph[vertex][i] and colors[i] == color:
                return False
        return True

    def solve_graph_coloring(self):
        """Main function to solve graph coloring."""
        selected_solver = self.solver_var.get()

        if selected_solver == "Backtracking":
            self.solve_with_backtracking()
        elif selected_solver == "Ant Colony Optimization":
            self.solve_with_aco()

    def solve_with_backtracking(self):
        """Solve graph coloring using backtracking."""
        self.max_colors = max(4, int(np.sqrt(self.n)) + 1)
        colors = [-1] * self.n
        iterations = [0]

        if self.solve_graph_coloring_util(colors, 0, iterations):
            self.solution_label.config(text="Solution Found!", foreground="green")
            self.draw_graph(colors)
        else:
            self.solution_label.config(text="No solution found", foreground="red")

        self.generation_label.config(text=f"Iterations: {iterations[0]}")

    def solve_with_aco(self):
        """Solve graph coloring using Ant Colony Optimization."""
        iterations = 100
        num_ants = 20
        pheromone = np.ones((self.n, self.max_colors))
        evaporation_rate = 0.5
        best_colors = None
        best_cost = float('inf')

        for iteration in range(iterations):
            all_colors = []
            all_costs = []

            for ant in range(num_ants):
                colors = [-1] * self.n
                for vertex in range(self.n):
                    probabilities = pheromone[vertex] / pheromone[vertex].sum()
                    chosen_color = np.random.choice(self.max_colors, p=probabilities)
                    colors[vertex] = chosen_color

                cost = self.calculate_cost(colors)
                all_colors.append(colors)
                all_costs.append(cost)

                if cost < best_cost:
                    best_colors = colors
                    best_cost = cost

            pheromone *= (1 - evaporation_rate)
            for colors, cost in zip(all_colors, all_costs):
                for vertex, color in enumerate(colors):
                    pheromone[vertex][color] += 1.0 / (1 + cost)

            self.generation_label.config(text=f"Iterations: {iteration + 1}")
            self.root.update_idletasks()

        if best_cost == 0:
            self.solution_label.config(text="Solution Found with ACO!", foreground="green")
            self.draw_graph(best_colors)
        else:
            self.solution_label.config(text="No perfect solution found with ACO.", foreground="red")

    def calculate_cost(self, colors):
        """Calculate the cost of a color assignment."""
        cost = 0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if self.graph[i][j] == 1 and colors[i] == colors[j]:
                    cost += 1
        return cost

    def solve_graph_coloring_util(self, colors, vertex, iterations):
        if vertex == self.n:
            return True

        iterations[0] += 1

        for color in range(self.max_colors):
            if self.is_safe_color(vertex, color, colors):
                colors[vertex] = color
                if self.solve_graph_coloring_util(colors, vertex + 1, iterations):
                    return True
                colors[vertex] = -1

        return False

def main():
    root = tk.Tk()
    app = GraphColoringApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
