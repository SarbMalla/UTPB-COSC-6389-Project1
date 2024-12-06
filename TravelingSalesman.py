import math
import random
import tkinter as tk
from tkinter import messagebox

# Configuration parameters
num_cities = 25
city_radius = 10
road_width = 2
padding = 50

class Location:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id  # Unique identifier for the city

    def draw(self, canvas, color='blue'):
        canvas.create_oval(
            self.x - city_radius, self.y - city_radius,
            self.x + city_radius, self.y + city_radius,
            fill=color, outline='black'
        )


class Path:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.distance = math.hypot(start.x - end.x, start.y - end.y)

    def draw(self, canvas, color='gray', dashed=False):
        kwargs = {'fill': color, 'width': road_width}
        if dashed:
            kwargs['dash'] = (4, 2)
        canvas.create_line(
            self.start.x, self.start.y,
            self.end.x, self.end.y,
            **kwargs
        )


class SalesmanProblemSolver:
    def __init__(self, locations):
        self.locations = locations
        self.num_locations = len(locations)
        self.distance_matrix = self.calculate_distance_matrix()
        self.current_solution = list(range(self.num_locations))
        random.shuffle(self.current_solution)
        self.best_solution = self.current_solution[:]
        self.best_distance = self.calculate_total_distance(self.best_solution)
        self.temperature = 10000
        self.cooling_rate = 0.995

    def calculate_distance_matrix(self):
        matrix = [[0]*self.num_locations for _ in range(self.num_locations)]
        for i in range(self.num_locations):
            for j in range(i+1, self.num_locations):
                dist = math.hypot(
                    self.locations[i].x - self.locations[j].x,
                    self.locations[i].y - self.locations[j].y
                )
                matrix[i][j] = dist
                matrix[j][i] = dist
        return matrix

    def calculate_total_distance(self, solution):
        distance = 0
        for i in range(len(solution)):
            a = solution[i]
            b = solution[(i + 1) % len(solution)]
            distance += self.distance_matrix[a][b]
        return distance

    def swap_locations(self, solution):
        new_solution = solution[:]
        i, j = random.sample(range(self.num_locations), 2)
        new_solution[i], new_solution[j] = new_solution[j], new_solution[i]
        return new_solution

    def anneal(self):
        new_solution = self.swap_locations(self.current_solution)
        current_distance = self.calculate_total_distance(self.current_solution)
        new_distance = self.calculate_total_distance(new_solution)
        acceptance_prob = self.acceptance_probability(current_distance, new_distance, self.temperature)
        if acceptance_prob > random.random():
            self.current_solution = new_solution
            current_distance = new_distance
            if current_distance < self.best_distance:
                self.best_distance = current_distance
                self.best_solution = self.current_solution[:]
        self.temperature *= self.cooling_rate

    def acceptance_probability(self, current_distance, new_distance, temperature):
        if new_distance < current_distance:
            return 1.0
        else:
            return math.exp((current_distance - new_distance) / temperature)


class TravelingSalesmanUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Traveling Salesman Problem Solver")
        self.geometry("800x600")
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.locations_list = []
        self.solver = None
        self.is_running = False

        # Menu Bar
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.create_menu()

        # Status label
        self.status_label = tk.Label(self, text="Shortest Path Length: --", anchor="w", bg="lightgray", relief="sunken")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Generate Locations", command=self.generate)
        file_menu.add_command(label="Start Solving", command=self.start_solver)
        file_menu.add_command(label="Reset", command=self.reset)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

    def generate(self):
        self.clear_canvas()
        self.locations_list.clear()
        for i in range(num_cities):
            self.add_location(i)
        self.draw_locations()

    def add_location(self, id):
        x = random.randint(padding, self.winfo_width() - padding)
        y = random.randint(padding, self.winfo_height() - padding)
        location = Location(x, y, id)
        self.locations_list.append(location)

    def draw_locations(self):
        for location in self.locations_list:
            location.draw(self.canvas)

    def clear_canvas(self):
        self.canvas.delete("all")

    def start_solver(self):
        if not self.locations_list:
            self.generate()
        self.solver = SalesmanProblemSolver(self.locations_list)
        self.is_running = True
        self.run_solver()

    def run_solver(self):
        if self.is_running and self.solver.temperature > 1:
            self.solver.anneal()
            self.clear_canvas()
            self.draw_solution(self.solver.current_solution)
            self.canvas.update()
            self.after(10, self.run_solver)  # Increased delay for better user experience
        else:
            self.is_running = False
            self.display_best_distance()

    def display_best_distance(self):
        self.status_label.config(text=f"Shortest Path Length: {int(self.solver.best_distance)}")

    def reset(self):
        self.clear_canvas()
        self.locations_list.clear()
        self.status_label.config(text="Shortest Path Length: --")
        self.is_running = False

    def draw_solution(self, solution):
        for i in range(len(solution)):
            location_a = self.locations_list[solution[i]]
            location_b = self.locations_list[solution[(i + 1) % len(solution)]]
            path = Path(location_a, location_b)
            path.draw(self.canvas, color='blue', dashed=True)  # Dotted lines for solution path
        for location in self.locations_list:
            location.draw(self.canvas, color='red')  # Cities shown in red


if __name__ == '__main__':
    ui = TravelingSalesmanUI()
    ui.mainloop()
