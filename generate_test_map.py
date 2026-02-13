#!/usr/bin/env python3
"""
Generate a test mission configuration for SAR simulation
Saves to mission_config.json
"""

import json

def generate_test_mission():
    """Generate a realistic SAR mission configuration"""

    # Map boundaries
    width = 500
    height = 400

    # Search Area (center-right, large polygon)
    search_area = [
        [200, 250],
        [450, 250],
        [450, 100],
        [200, 100]
    ]

    # No-Fly Zone (bottom-right corner, away from search)
    no_fly_zone = [
        [350, 50],
        [480, 50],
        [480, 10],
        [350, 10]
    ]

    # Start Point (bottom-left)
    start_point = [50, 50]

    # Transit Waypoints (from start to search area entry)
    transit_waypoints = [
        [100, 100],
        [150, 150],
        [200, 200]
    ]

    # Search Waypoints (lawnmower pattern inside search area)
    search_waypoints = [
        [220, 230],  # Start top-left
        [420, 230],  # Go right
        [420, 200],  # Drop down
        [220, 200],  # Go left
        [220, 170],  # Drop down
        [420, 170],  # Go right
        [420, 140],  # Drop down
        [220, 140],  # Go left
        [220, 110],  # Drop down
        [420, 110],  # Go right (final pass)
    ]

    # Dummy Location (casualty - in path of search)
    dummy_location = [350, 170]

    # Create configuration
    config = {
        "map_size": {
            "width": width,
            "height": height
        },
        "search_area": search_area,
        "no_fly_zone": no_fly_zone,
        "start_point": start_point,
        "transit_waypoints": transit_waypoints,
        "search_waypoints": search_waypoints,
        "dummy_location": dummy_location
    }

    # Save to file
    with open('mission_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("=" * 60)
    print("TEST MISSION CONFIGURATION GENERATED")
    print("=" * 60)
    print(f"\nSaved to: mission_config.json")
    print(f"\nMap Size: {width}x{height}")
    print(f"Search Area: 4 points")
    print(f"No-Fly Zone: 4 points (bottom-right corner)")
    print(f"Start Point: {start_point}")
    print(f"Transit Waypoints: {len(transit_waypoints)}")
    print(f"Search Waypoints: {len(search_waypoints)} (lawnmower pattern)")
    print(f"Dummy Location: {dummy_location}")
    print("\n" + "=" * 60)
    print("Ready to run simulation!")
    print("Run: python simple_simulator.py")
    print("=" * 60)

if __name__ == "__main__":
    generate_test_mission()
