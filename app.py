import tkinter as tk
from typing import List, Optional


class Elevator:
    def __init__(self, canvas: tk.Canvas, id: str, x_position: int):
        self.id = id
        self.current_floor = 0
        self.destination_floor: Optional[int] = None
        self.canvas = canvas
        self.x_position = x_position
        self.rect = canvas.create_rectangle(self.x_position, 450 - 40, self.x_position + 40, 450, fill="green")
        self.text = canvas.create_text(self.x_position + 20, 450 - 20, text=f"E{id}", fill="white")
        self.moving = False

    def move(self) -> None:
        if self.destination_floor is not None and not self.moving:
            self.moving = True
            self.canvas.itemconfig(self.rect, fill="yellow")

        if self.moving:
            if self.current_floor < self.destination_floor:
                self.current_floor += 1
            elif self.current_floor > self.destination_floor:
                self.current_floor -= 1

            y_movement = self.current_floor * 40
            self.canvas.coords(self.rect, self.x_position, 450 - y_movement - 40,
                               self.x_position + 40, 450 - y_movement)
            self.canvas.coords(self.text, self.x_position + 20, 450 - y_movement - 20)

            if self.current_floor == self.destination_floor:
                self.open_doors()

    def set_destination(self, destination_floor: int) -> None:
        if not self.moving and self.current_floor != destination_floor:
            self.destination_floor = destination_floor

    def open_doors(self) -> None:
        self.canvas.itemconfig(self.rect, fill="red")
        self.destination_floor = None
        self.moving = False

    def close_doors(self) -> None:
        self.canvas.itemconfig(self.rect, fill="green")
        self.destination_floor = None
        self.moving = False


class Building:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.canvas_width = 1200
        self.canvas_height = 1000
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(expand=True)

        center_x = self.canvas_width / 2
        elevator_gap = 80

        self.elevators_south = [Elevator(self.canvas, f"S{i + 1}", center_x - (3 * elevator_gap) + (i * elevator_gap))
                                for i in range(4)]
        self.elevators_north = [Elevator(self.canvas, f"N{i + 1}", center_x + elevator_gap + (i * elevator_gap)) for i
                                in range(4)]
        self.elevators = self.elevators_south + self.elevators_north

        self.selected_elevator = tk.StringVar(value="S1")
        self.selected_floor = tk.IntVar(value=0)

        self.draw_building()
        self.create_call_buttons()
        self.setup_ui()
        self.step()

    def draw_building(self) -> None:
        for i in range(-7, 12):
            self.canvas.create_line(0, 450 - (i * 40), self.canvas_width, 450 - (i * 40))
            floor_label = "L" if i == 0 else f"B{7 - i}" if i < 0 else f"F{i}"
            self.canvas.create_text(30, 450 - (i * 40) + 20, text=floor_label, anchor="w")

    def create_call_buttons(self) -> None:
        for i in range(-7, 12):
            y = 450 - (i * 40) + 20
            button_south = tk.Button(self.canvas, text="S",
                                     command=lambda floor=i, wing="S": self.call_elevator(floor, wing))
            button_north = tk.Button(self.canvas, text="N",
                                     command=lambda floor=i, wing="N": self.call_elevator(floor, wing))
            self.canvas.create_window(80, y, window=button_south)
            self.canvas.create_window(120, y, window=button_north)

    def call_elevator(self, floor: int, wing: str) -> None:
        elevators = self.elevators_south if wing == "S" else self.elevators_north
        available_elevators = [e for e in elevators if not e.moving]

        if available_elevators:
            nearest_elevator = min(available_elevators, key=lambda e: abs(e.current_floor - floor))
            if nearest_elevator.current_floor == floor and self.canvas.itemcget(nearest_elevator.rect, "fill") == "red":
                nearest_elevator.close_doors()
            else:
                nearest_elevator.set_destination(floor)
        else:
            print(f"No hay elevadores disponibles en el ala {wing} en este momento.")

    def setup_ui(self) -> None:
        ui_frame = tk.Frame(self.root)
        ui_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.create_elevator_selector(ui_frame)
        self.create_floor_selector(ui_frame)
        self.create_move_button(ui_frame)

    def create_elevator_selector(self, parent: tk.Frame) -> None:
        selector_frame = tk.Frame(parent)
        selector_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(selector_frame, text="Select Elevator:").pack(side=tk.LEFT)
        tk.OptionMenu(selector_frame, self.selected_elevator, *(e.id for e in self.elevators)).pack(side=tk.LEFT)

    def create_floor_selector(self, parent: tk.Frame) -> None:
        floor_selector_frame = tk.Frame(parent)
        floor_selector_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(floor_selector_frame, text="Select Floor:").pack(side=tk.LEFT)
        floor_options = [(-i, f"B{7 - i}") for i in range(7, 0, -1)] + [(0, "L")] + [(i, f"F{i}") for i in range(1, 12)]
        tk.OptionMenu(floor_selector_frame, self.selected_floor, *[value for value, _ in floor_options]).pack(
            side=tk.LEFT)

    def create_move_button(self, parent: tk.Frame) -> None:
        tk.Button(parent, text="Move", command=self.request_elevator).pack(side=tk.LEFT, padx=10)

    def step(self) -> None:
        for elevator in self.elevators:
            elevator.move()
        self.root.after(200, self.step)

    def request_elevator(self) -> None:
        selected_elevator = next(e for e in self.elevators if e.id == self.selected_elevator.get())
        selected_elevator.set_destination(self.selected_floor.get())


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Elevator Simulation")
    Building(root)
    root.mainloop()