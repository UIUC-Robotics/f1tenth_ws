#!/usr/bin/env python3

import sys
import csv
import math
import matplotlib.pyplot as plt
import numpy as np


def plot_waypoints(csv_file, show_heading=True, arrow_spacing=10):
    """
    Plot waypoints from a CSV file.
    
    Args:
        csv_file: Path to the CSV file containing waypoints (x, y, yaw_degrees)
        show_heading: Whether to show heading arrows
        arrow_spacing: Show every Nth arrow (to avoid clutter)
    """
    waypoints_x = []
    waypoints_y = []
    waypoints_yaw = []
    
    # Read CSV file
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                # Skip empty rows
                if not row or len(row) < 3:
                    continue
                
                try:
                    x = float(row[0])
                    y = float(row[1])
                    yaw = float(row[2])
                    
                    waypoints_x.append(x)
                    waypoints_y.append(y)
                    waypoints_yaw.append(yaw)
                except ValueError:
                    # Skip rows that can't be converted to numbers
                    continue
        
        if len(waypoints_x) == 0:
            print(f"Error: No valid waypoints found in {csv_file}")
            return
        
        print(f"Loaded {len(waypoints_x)} waypoints from {csv_file}")
        
    except FileNotFoundError:
        print(f"Error: File not found: {csv_file}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot the waypoint path
    ax.plot(waypoints_x, waypoints_y, 'b-', linewidth=2, label='Path')
    ax.plot(waypoints_x, waypoints_y, 'ro', markersize=3, alpha=0.5, label='Waypoints')
    
    # Mark start and end points
    ax.plot(waypoints_x[0], waypoints_y[0], 'go', markersize=15, 
            label='Start', markeredgecolor='black', markeredgewidth=2)
    ax.plot(waypoints_x[-1], waypoints_y[-1], 'rs', markersize=15, 
            label='End', markeredgecolor='black', markeredgewidth=2)
    
    # Show heading arrows
    if show_heading and len(waypoints_x) > 1:
        arrow_length = 0.1  # meters
        
        for i in range(0, len(waypoints_x), arrow_spacing):
            x = waypoints_x[i]
            y = waypoints_y[i]
            yaw_rad = math.radians(waypoints_yaw[i])
            
            dx = arrow_length * math.cos(yaw_rad)
            dy = arrow_length * math.sin(yaw_rad)
            
            ax.arrow(x, y, dx, dy, 
                    head_width=0.05, head_length=0.03, 
                    fc='green', ec='green', alpha=0.6)
    
    # Calculate some statistics
    total_distance = 0
    for i in range(1, len(waypoints_x)):
        dist = math.sqrt((waypoints_x[i] - waypoints_x[i-1])**2 + 
                        (waypoints_y[i] - waypoints_y[i-1])**2)
        total_distance += dist
    
    # Set plot properties
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.set_title(f'Waypoint Path\n{len(waypoints_x)} waypoints, {total_distance:.2f}m total distance', 
                fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    # Add text with statistics
    stats_text = f'Min X: {min(waypoints_x):.3f}m\n'
    stats_text += f'Max X: {max(waypoints_x):.3f}m\n'
    stats_text += f'Min Y: {min(waypoints_y):.3f}m\n'
    stats_text += f'Max Y: {max(waypoints_y):.3f}m'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.show()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 plot_waypoints.py <csv_file> [--no-arrows] [--arrow-spacing N]")
        print("\nExample:")
        print("  python3 plot_waypoints.py waypoints/my_track.csv")
        print("  python3 plot_waypoints.py waypoints/my_track.csv --no-arrows")
        print("  python3 plot_waypoints.py waypoints/my_track.csv --arrow-spacing 20")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    show_heading = True
    arrow_spacing = 10
    
    # Parse optional arguments
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == '--no-arrows':
            show_heading = False
        elif sys.argv[i] == '--arrow-spacing' and i + 1 < len(sys.argv):
            try:
                arrow_spacing = int(sys.argv[i + 1])
            except ValueError:
                print(f"Warning: Invalid arrow spacing value: {sys.argv[i + 1]}")
    
    plot_waypoints(csv_file, show_heading, arrow_spacing)


if __name__ == '__main__':
    main()

