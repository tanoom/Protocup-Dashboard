#!/usr/bin/env python3
"""
Robot Simulator for Dashboard Testing

This module simulates multiple robots sending data to the dashboard
for development and testing purposes. It generates realistic robot
behavior including movement, ball detection, and game state changes.
"""

import json
import socket
import threading
import time
import math
import random
from typing import List, Dict, Any


class SimulatedRobot:
    """Simulates a single robot's behavior and data transmission"""
    
    def __init__(self, robot_id: int, team_id: int = 1):
        self.robot_id = robot_id
        self.team_id = team_id
        self.robot_name = f"robot{robot_id + 1}"
        
        # Robot state
        self.pose_x = random.uniform(-3.0, 3.0)
        self.pose_y = random.uniform(-2.0, 2.0)
        self.pose_theta = random.uniform(0, 2 * math.pi)
        
        # Movement parameters
        self.target_x = self.pose_x
        self.target_y = self.pose_y
        self.movement_speed = 0.5  # m/s
        
        # Game state
        self.game_states = ["INITIAL", "READY", "SET", "PLAY", "END"]
        self.current_game_state_idx = 0
        self.score = 0
        
        # Ball state
        self.ball_detected = False
        self.ball_x = 0.0
        self.ball_y = 0.0
        self.ball_range = 0.0
        
        # Collaboration
        self.roles = ["master", "slave", "striker", "goalkeeper", "follower"]
        self.current_role = random.choice(self.roles[:2])  # Start with master/slave
        self.dynamic_role = robot_id  # 0=goalkeeper, 1=striker, 2=follower
        self.has_possession = False
        self.ball_cost = random.uniform(0.5, 5.0)
        
        # Behavior
        self.decisions = ["search_ball", "approach_ball", "kick_ball", "defend_goal", "position"]
        self.current_decision = random.choice(self.decisions)
        
        # Performance
        self.avg_loop_time = random.uniform(0.008, 0.025)  # 8-25ms
        self.max_loop_time = self.avg_loop_time * random.uniform(1.5, 3.0)
        
        # Head tracking
        self.head_pitch = random.uniform(-0.5, 0.5)
        self.head_yaw = random.uniform(-1.0, 1.0)
        
        # Recovery
        self.recovery_state = 0
        self.recovery_available = True
        
        # Simulation timing
        self.last_update = time.time()
        self.last_target_change = time.time()
        self.last_game_state_change = time.time()
        
    def update_simulation(self, dt: float, ball_pos: tuple = None):
        """Update robot simulation state"""
        current_time = time.time()
        
        # Update movement towards target
        dx = self.target_x - self.pose_x
        dy = self.target_y - self.pose_y
        distance_to_target = math.sqrt(dx*dx + dy*dy)
        
        if distance_to_target > 0.1:  # Move towards target
            move_distance = min(self.movement_speed * dt, distance_to_target)
            self.pose_x += (dx / distance_to_target) * move_distance
            self.pose_y += (dy / distance_to_target) * move_distance
            
            # Update orientation to face movement direction
            self.pose_theta = math.atan2(dy, dx) + random.uniform(-0.1, 0.1)
        
        # Change target occasionally
        if current_time - self.last_target_change > random.uniform(3.0, 8.0):
            self.target_x = random.uniform(-4.0, 4.0)
            self.target_y = random.uniform(-2.5, 2.5)
            self.last_target_change = current_time
            
        # Update ball detection
        if ball_pos:
            ball_x, ball_y = ball_pos
            distance_to_ball = math.sqrt((ball_x - self.pose_x)**2 + (ball_y - self.pose_y)**2)
            
            # Detect ball if within range (with some randomness)
            detection_range = 3.0 + random.uniform(-0.5, 0.5)
            self.ball_detected = distance_to_ball < detection_range
            
            if self.ball_detected:
                # Add some noise to ball position
                self.ball_x = ball_x + random.uniform(-0.2, 0.2)
                self.ball_y = ball_y + random.uniform(-0.2, 0.2)
                self.ball_range = distance_to_ball + random.uniform(-0.1, 0.1)
                
                # Possession logic
                self.has_possession = distance_to_ball < 0.5 and random.random() < 0.3
                
                # Update ball cost based on distance
                self.ball_cost = distance_to_ball + random.uniform(0.1, 0.5)
                
                # Head tracking towards ball
                angle_to_ball = math.atan2(ball_y - self.pose_y, ball_x - self.pose_x)
                self.head_yaw = angle_to_ball - self.pose_theta + random.uniform(-0.1, 0.1)
                self.head_pitch = random.uniform(-0.2, 0.2)
            else:
                self.has_possession = False
                # Random head movement when not tracking ball
                self.head_yaw = random.uniform(-1.0, 1.0)
                self.head_pitch = random.uniform(-0.3, 0.3)
        
        # Update game state occasionally
        if current_time - self.last_game_state_change > random.uniform(10.0, 30.0):
            self.current_game_state_idx = (self.current_game_state_idx + 1) % len(self.game_states)
            self.last_game_state_change = current_time
            
            # Increment score occasionally
            if random.random() < 0.1:
                self.score += 1
        
        # Update behavior decision
        if random.random() < 0.1:  # 10% chance to change decision each update
            self.current_decision = random.choice(self.decisions)
        
        # Update performance metrics with some variation
        self.avg_loop_time = 0.015 + random.uniform(-0.005, 0.010)
        self.max_loop_time = self.avg_loop_time * random.uniform(1.2, 2.5)
        
        # Keep robot on field
        self.pose_x = max(-4.5, min(4.5, self.pose_x))
        self.pose_y = max(-3.0, min(3.0, self.pose_y))
        
    def generate_data(self) -> Dict[str, Any]:
        """Generate robot data in the format expected by the dashboard"""
        return {
            "robot_id": self.robot_id,
            "robot_name": self.robot_name,
            "team_id": self.team_id,
            "timestamp": time.time(),
            
            "game": {
                "state": self.game_states[self.current_game_state_idx],
                "kickoff_side": self.robot_id == 0,  # Robot 0 gets kickoff
                "score": self.score
            },
            
            "robot": {
                "pose": {
                    "x": self.pose_x,
                    "y": self.pose_y,
                    "theta": self.pose_theta
                },
                "ball": {
                    "detected": self.ball_detected,
                    "x": self.ball_x if self.ball_detected else 0.0,
                    "y": self.ball_y if self.ball_detected else 0.0,
                    "range": self.ball_range if self.ball_detected else 0.0
                }
            },
            
            "collaboration": {
                "role": self.current_role,
                "dynamic_role": self.dynamic_role,
                "has_possession": self.has_possession,
                "possession_player": self.robot_id if self.has_possession else -1,
                "ball_cost": self.ball_cost
            },
            
            "behavior": {
                "decision": self.current_decision,
                "ball_location_known": self.ball_detected
            },
            
            "performance": {
                "avg_loop_time": self.avg_loop_time,
                "max_loop_time": self.max_loop_time
            },
            
            "head": {
                "pitch": self.head_pitch,
                "yaw": self.head_yaw
            },
            
            "recovery": {
                "state": self.recovery_state,
                "available": self.recovery_available
            },
            
            "team_count": 2  # Number of teammates (excluding self)
        }


class RobotSimulator:
    """Simulates multiple robots for dashboard testing"""
    
    def __init__(self, num_robots: int = 3, team_id: int = 1, 
                 target_ip: str = "127.0.0.1", port: int = 8080):
        self.num_robots = num_robots
        self.team_id = team_id
        self.target_ip = target_ip
        self.port = port
        
        # Create simulated robots
        self.robots: List[SimulatedRobot] = []
        for i in range(num_robots):
            robot = SimulatedRobot(i, team_id)
            self.robots.append(robot)
        
        # Ball simulation
        self.ball_x = 0.0
        self.ball_y = 0.0
        self.ball_vx = random.uniform(-1.0, 1.0)
        self.ball_vy = random.uniform(-1.0, 1.0)
        
        # Network
        self.socket = None
        self.running = False
        
    def update_ball_simulation(self, dt: float):
        """Update ball position"""
        # Simple ball physics
        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt
        
        # Bounce off field boundaries
        if abs(self.ball_x) > 4.0:
            self.ball_vx *= -0.8  # Some energy loss
            self.ball_x = 4.0 if self.ball_x > 0 else -4.0
            
        if abs(self.ball_y) > 2.5:
            self.ball_vy *= -0.8
            self.ball_y = 2.5 if self.ball_y > 0 else -2.5
        
        # Slow down ball over time
        self.ball_vx *= 0.99
        self.ball_vy *= 0.99
        
        # Randomly kick ball
        if random.random() < 0.01:  # 1% chance per update
            self.ball_vx = random.uniform(-2.0, 2.0)
            self.ball_vy = random.uniform(-2.0, 2.0)
    
    def run(self):
        """Run the robot simulator"""
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.running = True
            
            print(f"Robot simulator sending data to {self.target_ip}:{self.port}")
            print(f"Simulating {self.num_robots} robots")
            
            last_time = time.time()
            
            while self.running:
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time
                
                # Update ball simulation
                self.update_ball_simulation(dt)
                
                # Update each robot and send data
                for robot in self.robots:
                    robot.update_simulation(dt, (self.ball_x, self.ball_y))
                    
                    # Generate and send robot data
                    data = robot.generate_data()
                    json_data = json.dumps(data)
                    
                    try:
                        self.socket.sendto(json_data.encode('utf-8'), 
                                         (self.target_ip, self.port))
                    except Exception as e:
                        print(f"Failed to send data for robot {robot.robot_id}: {e}")
                
                # Send updates at ~10 Hz
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Simulator error: {e}")
        finally:
            if self.socket:
                self.socket.close()
            print("Robot simulator stopped")
    
    def stop(self):
        """Stop the simulator"""
        self.running = False


if __name__ == "__main__":
    # Test the robot simulator
    import argparse
    
    parser = argparse.ArgumentParser(description='Robot Simulator for Dashboard Testing')
    parser.add_argument('--robots', type=int, default=3, help='Number of robots to simulate')
    parser.add_argument('--port', type=int, default=8080, help='Target port')
    parser.add_argument('--ip', default='127.0.0.1', help='Target IP address')
    
    args = parser.parse_args()
    
    simulator = RobotSimulator(num_robots=args.robots, target_ip=args.ip, port=args.port)
    
    try:
        print(f"Starting robot simulator with {args.robots} robots")
        print(f"Sending data to {args.ip}:{args.port}")
        print("Press Ctrl+C to stop")
        simulator.run()
    except KeyboardInterrupt:
        print("\nStopping simulator...")
        simulator.stop() 