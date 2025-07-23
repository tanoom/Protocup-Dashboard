#!/usr/bin/env python3

import json
import socket
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import queue
from dataclasses import dataclass, field


@dataclass
class RobotData:
    """Data structure for robot information"""
    robot_id: int = -1
    robot_name: str = ""
    team_id: int = -1
    timestamp: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    
    # Game state
    game_state: str = "UNKNOWN"
    kickoff_side: bool = False
    score: int = 0
    
    # Robot pose
    pose_x: float = 0.0
    pose_y: float = 0.0
    pose_theta: float = 0.0
    
    # Ball information
    ball_detected: bool = False
    ball_x: float = 0.0
    ball_y: float = 0.0
    ball_range: float = 0.0
    
    # Collaboration
    role: str = "unknown"
    dynamic_role: int = -1
    has_possession: bool = False
    possession_player: int = -1
    ball_cost: float = 0.0
    
    # Behavior
    decision: str = "unknown"
    ball_location_known: bool = False
    
    # Performance
    avg_loop_time: float = 0.0
    max_loop_time: float = 0.0
    
    # Head tracking
    head_pitch: float = 0.0
    head_yaw: float = 0.0
    
    # Recovery state
    recovery_state: int = 0
    recovery_available: bool = False
    
    # Team count
    team_count: int = 0
    
    # Connection status
    is_connected: bool = False


class DashboardCore:
    """Core dashboard system for receiving and processing robot data"""
    
    def __init__(self, port: int = 8080, timeout_seconds: int = 5):
        self.port = port
        self.timeout_seconds = timeout_seconds
        self.robots: Dict[int, RobotData] = {}
        self.data_queue = queue.Queue()
        self.running = False
        
        # Network
        self.socket = None
        self.receive_thread = None
        self.cleanup_thread = None
        
        # Callbacks for data updates
        self.update_callbacks = []
        
    def add_update_callback(self, callback):
        """Add callback function that gets called when robot data is updated"""
        self.update_callbacks.append(callback)
        
    def start(self):
        """Start the dashboard core receiver"""
        if self.running:
            return
            
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', self.port))
            self.socket.settimeout(1.0)  # 1 second timeout for clean shutdown
            
            self.running = True
            
            # Start receiver thread
            self.receive_thread = threading.Thread(target=self._receive_data, daemon=True)
            self.receive_thread.start()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(target=self._cleanup_expired_robots, daemon=True)
            self.cleanup_thread.start()
            
            print(f"Dashboard core started on port {self.port}")
            
        except Exception as e:
            print(f"Failed to start dashboard core: {e}")
            self.stop()
            
    def stop(self):
        """Stop the dashboard core"""
        self.running = False
        
        if self.socket:
            self.socket.close()
            self.socket = None
            
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=2.0)
            
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=2.0)
            
        print("Dashboard core stopped")
        
    def _receive_data(self):
        """Thread function to receive UDP data from robots"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)  # Max 4KB per message
                
                # Parse JSON data
                try:
                    raw_data = data.decode('utf-8')
                    robot_data_json = json.loads(raw_data)
                    self._process_robot_data(robot_data_json, addr)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON from {addr}: {e}")
                    # Debug: Show the problematic JSON around the error location
                    raw_data = data.decode('utf-8', errors='replace')
                    error_pos = getattr(e, 'pos', 0)
                    start = max(0, error_pos - 50)
                    end = min(len(raw_data), error_pos + 50)
                    print(f"JSON context around error: '{raw_data[start:end]}'")
                    print(f"Full JSON (first 500 chars): '{raw_data[:500]}'")
                except Exception as e:
                    print(f"Error processing data from {addr}: {e}")
                    
            except socket.timeout:
                continue  # Normal timeout for clean shutdown
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    print(f"Socket error: {e}")
                break
                
    def _process_robot_data(self, data: Dict[str, Any], addr):
        """Process incoming robot data and update robot state"""
        try:
            robot_id = data.get('robot_id', -1)
            if robot_id == -1:
                return
                
            # Create or update robot data
            if robot_id not in self.robots:
                self.robots[robot_id] = RobotData()
                
            robot = self.robots[robot_id]
            
            # Update basic info
            robot.robot_id = robot_id
            robot.robot_name = data.get('robot_name', f"robot{robot_id}")
            robot.team_id = data.get('team_id', -1)
            robot.timestamp = data.get('timestamp', 0.0)
            robot.last_update = datetime.now()
            robot.is_connected = True
            
            # Update game state
            game_data = data.get('game', {})
            robot.game_state = game_data.get('state', 'UNKNOWN')
            robot.kickoff_side = game_data.get('kickoff_side', False)
            robot.score = game_data.get('score', 0)
            
            # Update robot pose
            robot_data = data.get('robot', {})
            pose_data = robot_data.get('pose', {})
            robot.pose_x = pose_data.get('x', 0.0)
            robot.pose_y = pose_data.get('y', 0.0)
            robot.pose_theta = pose_data.get('theta', 0.0)
            
            # Update ball information
            ball_data = robot_data.get('ball', {})
            robot.ball_detected = ball_data.get('detected', False)
            robot.ball_x = ball_data.get('x', 0.0)
            robot.ball_y = ball_data.get('y', 0.0)
            robot.ball_range = ball_data.get('range', 0.0)
            
            # Update collaboration
            collab_data = data.get('collaboration', {})
            robot.role = collab_data.get('role', 'unknown')
            robot.dynamic_role = collab_data.get('dynamic_role', -1)
            robot.has_possession = collab_data.get('has_possession', False)
            robot.possession_player = collab_data.get('possession_player', -1)
            robot.ball_cost = collab_data.get('ball_cost', 0.0)
            
            # Update behavior
            behavior_data = data.get('behavior', {})
            robot.decision = behavior_data.get('decision', 'unknown')
            robot.ball_location_known = behavior_data.get('ball_location_known', False)
            
            # Update performance
            perf_data = data.get('performance', {})
            robot.avg_loop_time = perf_data.get('avg_loop_time', 0.0)
            robot.max_loop_time = perf_data.get('max_loop_time', 0.0)
            
            # Update head tracking
            head_data = data.get('head', {})
            robot.head_pitch = head_data.get('pitch', 0.0)
            robot.head_yaw = head_data.get('yaw', 0.0)
            
            # Update recovery state
            recovery_data = data.get('recovery', {})
            robot.recovery_state = recovery_data.get('state', 0)
            robot.recovery_available = recovery_data.get('available', False)
            
            # Update team count
            robot.team_count = data.get('team_count', 0)
            
            # Notify callbacks
            for callback in self.update_callbacks:
                try:
                    callback(robot_id, robot)
                except Exception as e:
                    print(f"Error in update callback: {e}")
                    
        except Exception as e:
            print(f"Error processing robot data: {e}")
            
    def _cleanup_expired_robots(self):
        """Thread function to cleanup robots that haven't sent data recently"""
        while self.running:
            try:
                current_time = datetime.now()
                timeout_delta = timedelta(seconds=self.timeout_seconds)
                
                expired_robots = []
                for robot_id, robot in self.robots.items():
                    if current_time - robot.last_update > timeout_delta:
                        expired_robots.append(robot_id)
                        robot.is_connected = False
                        
                # Notify callbacks about disconnected robots
                for robot_id in expired_robots:
                    for callback in self.update_callbacks:
                        try:
                            callback(robot_id, self.robots[robot_id])
                        except Exception as e:
                            print(f"Error in disconnect callback: {e}")
                            
                # Remove very old robots (after 30 seconds)
                very_old_delta = timedelta(seconds=30)
                for robot_id in list(self.robots.keys()):
                    if current_time - self.robots[robot_id].last_update > very_old_delta:
                        print(f"Removing very old robot {robot_id}")
                        del self.robots[robot_id]
                        
            except Exception as e:
                print(f"Error in cleanup thread: {e}")
                
            time.sleep(1.0)  # Check every second
            
    def get_robots(self) -> Dict[int, RobotData]:
        """Get current robot data"""
        return self.robots.copy()
        
    def get_connected_robots(self) -> Dict[int, RobotData]:
        """Get only connected robots"""
        return {rid: robot for rid, robot in self.robots.items() if robot.is_connected}
        
    def send_command_to_robot(self, robot_ip: str, command: Dict[str, Any]) -> bool:
        """Send command to specific robot (placeholder for future implementation)"""
        # TODO: Implement robot command sending
        print(f"Would send command to {robot_ip}: {command}")
        return True


if __name__ == "__main__":
    # Test the dashboard core
    def on_robot_update(robot_id: int, robot_data: RobotData):
        status = "CONNECTED" if robot_data.is_connected else "DISCONNECTED"
        print(f"Robot {robot_id} ({robot_data.robot_name}): {status} - "
              f"State: {robot_data.game_state}, Pose: ({robot_data.pose_x:.1f}, {robot_data.pose_y:.1f})")
    
    dashboard = DashboardCore()
    dashboard.add_update_callback(on_robot_update)
    
    try:
        dashboard.start()
        print("Dashboard core running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        dashboard.stop() 