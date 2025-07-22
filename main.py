#!/usr/bin/env python3
"""
RoboCup Humanoid Robot Dashboard
Main launcher script for the dashboard system.

This dashboard receives real-time data from robots and provides:
- Multi-robot status monitoring
- Field visualization with robot positions
- Game state tracking
- Remote robot control capabilities
- Performance analytics

Usage:
    python main.py              # Start dashboard on default port 8080
    python main.py --port 9090  # Start dashboard on custom port
    python main.py --simulate   # Start with simulated robot data for testing
"""

import argparse
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dashboard_gui import RoboCupDashboard


def main():
    """Main entry point for the dashboard application"""
    parser = argparse.ArgumentParser(description='RoboCup Humanoid Robot Dashboard')
    
    parser.add_argument('--port', type=int, default=8080,
                       help='UDP port to listen for robot data (default: 8080)')
    parser.add_argument('--simulate', action='store_true',
                       help='Start with simulated robot data for testing')
    parser.add_argument('--timeout', type=int, default=5,
                       help='Robot timeout in seconds (default: 5)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("RoboCup Humanoid Robot Dashboard")
    print("=" * 60)
    print(f"Listening on port: {args.port}")
    print(f"Robot timeout: {args.timeout} seconds")
    
    if args.simulate:
        print("WARNING: Running in simulation mode with fake robot data")
        print("This is for development and testing only!")
        
        # Start robot simulator in a separate process
        import threading
        from robot_simulator import RobotSimulator
        
        simulator = RobotSimulator(port=args.port)
        sim_thread = threading.Thread(target=simulator.run, daemon=True)
        sim_thread.start()
        print("Robot simulator started")
    
    print("-" * 60)
    print("Expected robot data format from brain_communication.cpp:")
    print("- Robot ID, name, team ID")
    print("- Game state, score, kickoff side")
    print("- Robot pose (x, y, theta)")
    print("- Ball detection and position")
    print("- Collaboration role and possession")
    print("- Behavior decisions and performance metrics")
    print("-" * 60)
    print("Dashboard ready! Starting GUI...")
    print("Close the GUI window or press Ctrl+C to exit")
    
    try:
        # Create and run dashboard
        dashboard = RoboCupDashboard()
        dashboard.dashboard_core.port = args.port
        dashboard.dashboard_core.timeout_seconds = args.timeout
        dashboard.run()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Dashboard stopped")


if __name__ == "__main__":
    main() 