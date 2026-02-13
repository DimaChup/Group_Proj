#!/usr/bin/env python3
"""
Interactive Map Setup Tool for SAR Mission
Draw your environment once, save it, reuse it for all simulations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import numpy as np
from matplotlib.backend_bases import MouseButton

class MapSetupTool:
    def __init__(self, width=500, height=400):
        self.width = width
        self.height = height

        # Data storage
        self.search_area = []  # List of points defining search polygon
        self.no_fly_zone = []  # List of points defining no-fly polygon
        self.start_point = None  # Single point (x, y)
        self.transit_waypoints = []  # List of waypoints from start to search
        self.search_waypoints = []  # List of waypoints for search pattern
        self.dummy_location = None  # Single point (x, y)

        # Drawing state
        self.current_mode = None
        self.temp_points = []

        # Setup figure
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.ax.set_xlim(0, width)
        self.ax.set_ylim(0, height)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('SAR Mission Map Setup Tool', fontsize=14, fontweight='bold')

        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        self.draw_instructions()
        self.update_display()

    def draw_instructions(self):
        instructions = [
            "=== INSTRUCTIONS ===",
            "1: Draw Search Area (click points, press ENTER to close)",
            "2: Draw No-Fly Zone (click points, press ENTER to close)",
            "3: Place Start Point (single click)",
            "4: Place Transit Waypoints (click points, press ENTER when done)",
            "5: Place Search Waypoints (click points, press ENTER when done)",
            "6: Place Dummy Location (single click)",
            "",
            "S: Save configuration",
            "L: Load configuration",
            "C: Clear all",
            "Q: Quit",
            "",
            f"Current Mode: {self.current_mode or 'None - Press a number key'}"
        ]

        # Clear previous text
        for txt in self.ax.texts:
            txt.remove()

        y_pos = self.height - 20
        for line in instructions:
            self.ax.text(10, y_pos, line, fontsize=9, family='monospace',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            y_pos -= 15

    def update_display(self):
        # Clear previous drawings
        for patch in list(self.ax.patches):
            patch.remove()
        for line in list(self.ax.lines):
            line.remove()

        # Draw search area
        if len(self.search_area) > 2:
            poly = patches.Polygon(self.search_area, closed=True,
                                  edgecolor='blue', facecolor='blue',
                                  alpha=0.2, linewidth=2, label='Search Area')
            self.ax.add_patch(poly)

        # Draw no-fly zone
        if len(self.no_fly_zone) > 2:
            poly = patches.Polygon(self.no_fly_zone, closed=True,
                                  edgecolor='red', facecolor='red',
                                  alpha=0.3, linewidth=2, label='No-Fly Zone')
            self.ax.add_patch(poly)

        # Draw start point
        if self.start_point:
            self.ax.plot(self.start_point[0], self.start_point[1], 'go',
                        markersize=15, label='Start Point', markeredgecolor='black', markeredgewidth=2)
            self.ax.text(self.start_point[0] + 10, self.start_point[1] + 10,
                        'START', fontsize=10, fontweight='bold')

        # Draw transit waypoints
        if self.transit_waypoints:
            transit_x = [p[0] for p in self.transit_waypoints]
            transit_y = [p[1] for p in self.transit_waypoints]
            self.ax.plot(transit_x, transit_y, 'c^-', markersize=10,
                        linewidth=2, label='Transit Waypoints', markeredgecolor='black')
            for i, (x, y) in enumerate(self.transit_waypoints):
                self.ax.text(x + 5, y + 5, f'T{i+1}', fontsize=8)

        # Draw search waypoints
        if self.search_waypoints:
            search_x = [p[0] for p in self.search_waypoints]
            search_y = [p[1] for p in self.search_waypoints]
            self.ax.plot(search_x, search_y, 'mo-', markersize=8,
                        linewidth=1.5, label='Search Waypoints', alpha=0.7)
            for i, (x, y) in enumerate(self.search_waypoints):
                self.ax.text(x + 3, y + 3, f'S{i+1}', fontsize=7, color='purple')

        # Draw dummy location
        if self.dummy_location:
            self.ax.plot(self.dummy_location[0], self.dummy_location[1], 'r*',
                        markersize=25, label='Dummy (Casualty)', markeredgecolor='black', markeredgewidth=2)
            self.ax.text(self.dummy_location[0] + 10, self.dummy_location[1] + 10,
                        'CASUALTY', fontsize=10, fontweight='bold', color='red')

        # Draw temporary points
        if self.temp_points:
            temp_x = [p[0] for p in self.temp_points]
            temp_y = [p[1] for p in self.temp_points]
            self.ax.plot(temp_x, temp_y, 'ko--', markersize=6, alpha=0.5)

        self.ax.legend(loc='upper right', fontsize=9)
        self.draw_instructions()
        plt.draw()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        if event.button == MouseButton.LEFT:
            x, y = event.xdata, event.ydata

            if self.current_mode == 'search_area':
                self.temp_points.append((x, y))
                print(f"Search Area point added: ({x:.1f}, {y:.1f})")

            elif self.current_mode == 'no_fly_zone':
                self.temp_points.append((x, y))
                print(f"No-Fly Zone point added: ({x:.1f}, {y:.1f})")

            elif self.current_mode == 'start_point':
                self.start_point = (x, y)
                print(f"Start point set: ({x:.1f}, {y:.1f})")
                self.current_mode = None

            elif self.current_mode == 'transit_waypoints':
                self.temp_points.append((x, y))
                print(f"Transit waypoint added: ({x:.1f}, {y:.1f})")

            elif self.current_mode == 'search_waypoints':
                self.temp_points.append((x, y))
                print(f"Search waypoint added: ({x:.1f}, {y:.1f})")

            elif self.current_mode == 'dummy_location':
                self.dummy_location = (x, y)
                print(f"Dummy location set: ({x:.1f}, {y:.1f})")
                self.current_mode = None

            self.update_display()

    def on_key(self, event):
        key = event.key

        if key == '1':
            self.current_mode = 'search_area'
            self.temp_points = []
            print("\n=== MODE: Drawing Search Area ===")
            print("Click to add points, press ENTER when done")

        elif key == '2':
            self.current_mode = 'no_fly_zone'
            self.temp_points = []
            print("\n=== MODE: Drawing No-Fly Zone ===")
            print("Click to add points, press ENTER when done")

        elif key == '3':
            self.current_mode = 'start_point'
            print("\n=== MODE: Place Start Point ===")
            print("Click to place start point")

        elif key == '4':
            self.current_mode = 'transit_waypoints'
            self.temp_points = []
            print("\n=== MODE: Place Transit Waypoints ===")
            print("Click to add waypoints, press ENTER when done")

        elif key == '5':
            self.current_mode = 'search_waypoints'
            self.temp_points = []
            print("\n=== MODE: Place Search Waypoints ===")
            print("Click to add waypoints, press ENTER when done")

        elif key == '6':
            self.current_mode = 'dummy_location'
            print("\n=== MODE: Place Dummy Location ===")
            print("Click to place casualty")

        elif key == 'enter':
            if self.current_mode == 'search_area' and len(self.temp_points) >= 3:
                self.search_area = self.temp_points.copy()
                print(f"Search area saved with {len(self.search_area)} points")
                self.temp_points = []
                self.current_mode = None

            elif self.current_mode == 'no_fly_zone' and len(self.temp_points) >= 3:
                self.no_fly_zone = self.temp_points.copy()
                print(f"No-fly zone saved with {len(self.no_fly_zone)} points")
                self.temp_points = []
                self.current_mode = None

            elif self.current_mode == 'transit_waypoints':
                self.transit_waypoints = self.temp_points.copy()
                print(f"Transit waypoints saved: {len(self.transit_waypoints)} points")
                self.temp_points = []
                self.current_mode = None

            elif self.current_mode == 'search_waypoints':
                self.search_waypoints = self.temp_points.copy()
                print(f"Search waypoints saved: {len(self.search_waypoints)} points")
                self.temp_points = []
                self.current_mode = None

        elif key == 's':
            self.save_configuration()

        elif key == 'l':
            self.load_configuration()

        elif key == 'c':
            if input("Clear all? (y/n): ").lower() == 'y':
                self.clear_all()

        elif key == 'q':
            plt.close()
            return

        self.update_display()

    def save_configuration(self, filename='mission_config.json'):
        config = {
            'map_size': {'width': self.width, 'height': self.height},
            'search_area': self.search_area,
            'no_fly_zone': self.no_fly_zone,
            'start_point': self.start_point,
            'transit_waypoints': self.transit_waypoints,
            'search_waypoints': self.search_waypoints,
            'dummy_location': self.dummy_location
        }

        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n✓ Configuration saved to {filename}")

    def load_configuration(self, filename='mission_config.json'):
        try:
            with open(filename, 'r') as f:
                config = json.load(f)

            self.search_area = config.get('search_area', [])
            self.no_fly_zone = config.get('no_fly_zone', [])
            self.start_point = tuple(config['start_point']) if config.get('start_point') else None
            self.transit_waypoints = config.get('transit_waypoints', [])
            self.search_waypoints = config.get('search_waypoints', [])
            self.dummy_location = tuple(config['dummy_location']) if config.get('dummy_location') else None

            print(f"\n✓ Configuration loaded from {filename}")
            self.update_display()

        except FileNotFoundError:
            print(f"\n✗ File {filename} not found")

    def clear_all(self):
        self.search_area = []
        self.no_fly_zone = []
        self.start_point = None
        self.transit_waypoints = []
        self.search_waypoints = []
        self.dummy_location = None
        self.temp_points = []
        self.current_mode = None
        print("\n✓ All cleared")
        self.update_display()

    def run(self):
        plt.show()

if __name__ == "__main__":
    print("=== SAR Mission Map Setup Tool ===")
    print("Creating interactive map editor...")

    tool = MapSetupTool(width=500, height=400)
    tool.run()

    print("\nMap setup complete!")
