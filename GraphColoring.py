import math
import random
import tkinter as tk
from tkinter import messagebox, Canvas, Menu, StringVar

num_edges = 100
node_scale = 15  
edge_width = 2
padding = 100


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = None
        self.neighbors = []

    def draw(self, canvas):
        color = self.color if self.color else "black"
        canvas.create_oval(
            self.x - node_scale,
            self.y - node_scale,
            self.x + node_scale,
            self.y + node_scale,
            fill=color,
        )


class Edge:
    def __init__(self, a, b):
        self.node_a = a
        self.node_b = b
        self.length = math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    def draw(self, canvas, color="grey", style=(2, 4)):
        canvas.create_line(
            self.node_a.x,
            self.node_a.y,
            self.node_b.x,
            self.node_b.y,
            fill=color,
            width=edge_width,
            dash=style,
        )


class AntColony:
    def __init__(self, nodes, num_ants, num_colors, evaporation_rate=0.5):
        self.nodes = nodes
        self.num_ants = num_ants
        self.num_colors = num_colors
        self.evaporation_rate = evaporation_rate
        self.pheromone = {node: [1.0] * num_colors for node in nodes}

    def color_graph(self):
        best_coloring = {}
        best_cost = float('inf')

        for _ in range(self.num_ants):
            coloring = {}
            for node in self.nodes:
                available_colors = set(range(self.num_colors)) - {coloring.get(neighbor.color) for neighbor in node.neighbors}
                if available_colors:
                    probabilities = [self.pheromone[node][c] for c in range(self.num_colors) if c in available_colors]
                    total_prob = sum(probabilities)
                    probabilities = [p / total_prob for p in probabilities]  

                    chosen_color = random.choices(list(available_colors), weights=probabilities)[0]
                    coloring[node] = chosen_color
                else:
                    coloring[node] = random.randint(0, self.num_colors - 1)

            cost = self.calculate_cost(coloring)
            if cost < best_cost:
                best_cost = cost
                best_coloring = coloring

            
            for node in self.nodes:
                color = coloring[node]
                self.pheromone[node][color] += 1.0 / (cost + 1)  

            
            for node in self.nodes:
                for color in range(self.num_colors):
                    self.pheromone[node][color] *= (1 - self.evaporation_rate)

        return best_coloring

    def calculate_cost(self, coloring):
        conflicts = 0
        for node in self.nodes:
            for neighbor in node.neighbors:
                if coloring[node] == coloring[neighbor]:
                    conflicts += 1
        return conflicts


class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Graph Coloring with ACO")
        self.option_add("*tearOff", False)
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (width, height))
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=width, height=height)
        w = width - padding
        h = height - padding * 2

        self.nodes_list = []
        self.edges_list = []
        self.edges_set = set()

        
        self.circle_count_var = StringVar()
        circle_count_label = tk.Label(self, text="Enter number of circles (at least 50):")
        circle_count_label.pack(pady=10)
        circle_count_entry = tk.Entry(self, textvariable=self.circle_count_var)
        circle_count_entry.pack(pady=10)

        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack(pady=10)

        
        generate_button = tk.Button(self, text="Generate Graph", command=self.generate_graph)
        generate_button.pack(pady=5)

        
        menu_bar = Menu(self)
        self["menu"] = menu_bar

        menu_gc = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_gc, label="Graph Coloring", underline=0)
        menu_gc.add_command(label="Solve", command=self.solve, underline=0)

        self.mainloop()

    def add_node(self):
        x = random.randint(padding, self.canvas.winfo_width() - padding)
        y = random.randint(padding, self.canvas.winfo_height() - padding)
        node = Node(x, y)
        self.nodes_list.append(node)

    def add_edge(self):
        a = random.randint(0, len(self.nodes_list) - 1)
        b = random.randint(0, len(self.nodes_list) - 1)
        edge_key = (min(a, b), max(a, b))
        while a == b or edge_key in self.edges_set:
            a = random.randint(0, len(self.nodes_list) - 1)
            b = random.randint(0, len(self.nodes_list) - 1)
            edge_key = (min(a, b), max(a, b))

        edge = Edge(self.nodes_list[a], self.nodes_list[b])
        self.edges_set.add(edge_key)
        self.edges_list.append(edge)

        
        self.nodes_list[a].neighbors.append(self.nodes_list[b])
        self.nodes_list[b].neighbors.append(self.nodes_list[a])

    def generate_graph(self):
        self.nodes_list.clear()
        self.edges_list.clear()
        self.edges_set.clear()
        
        try:
            num_nodes = int(self.circle_count_var.get())  
            if num_nodes < 50:  
                raise ValueError("Number of circles must be at least 50.")
        except ValueError as e:
            self.status_label.config(text=str(e))
            messagebox.showerror("Input Error", str(e))
            return
            
        for _ in range(num_nodes):
            self.add_node()
        for _ in range(num_edges):
            self.add_edge()
        self.draw_graph()

    def draw_graph(self):
        self.clear_canvas()
        for e in self.edges_list:
            e.draw(self.canvas)
        for n in self.nodes_list:
            n.draw(self.canvas)

    def clear_canvas(self):
        self.canvas.delete("all")

    def solve(self):
        aco = AntColony(self.nodes_list, num_ants=10, num_colors=10)
        coloring = aco.color_graph()
        
        for i, node in enumerate(self.nodes_list):
            node.color = f'#{random.randint(0, 0xFFFFFF):06x}'  
            if i in coloring:
                node.color = f'#{(coloring[node] * 60) % 255:02x}{(coloring[node] * 100) % 255:02x}{(coloring[node] * 140) % 255:02x}'
        
        self.draw_graph()


if __name__ == "__main__":
    UI()
