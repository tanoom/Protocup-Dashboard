# RoboCup Humanoid Robot Dashboard

A comprehensive real-time dashboard system for monitoring and controlling RoboCup 3v3 humanoid soccer robots. This system provides live visualization of robot status, field positions, game state, and performance metrics.

## 🎯 Overview

The dashboard system consists of two main components:

1. **Robot Side (C++)**: Data collection and transmission from robots to dashboard
2. **Dashboard Side (Python)**: Data reception, processing, visualization, and remote control

The robots collect and transmit data via UDP to a central dashboard running on a laptop (Mac), which processes and displays all information while providing remote control capabilities.

## ✨ Features

### Real-time Monitoring
- **Multi-Robot Status**: Live display of all connected robots with health indicators
- **Field Visualization**: 2D field view with robot positions, orientations, and ball tracking
- **Game State Tracking**: Current game phase, score, and team status
- **Performance Analytics**: Loop times, resource usage, and system metrics
- **Ball Possession Flow**: Real-time tracking of ball possession and handovers

### Robot Control
- **Remote Commands**: Send build/start/stop commands to individual robots or groups
- **Emergency Stop**: Immediate stop command for all robots
- **Robot Selection**: Target specific robots or broadcast to all
- **Connection Monitoring**: Automatic detection of connected/disconnected robots

### Data Visualization
- **Robot Status Cards**: Individual status panels for each robot showing:
  - Connection status and robot name
  - Game state and position coordinates
  - Current role and ball possession
  - Ball detection status and position
  - Performance metrics and behavior decisions
- **Field Canvas**: Interactive field visualization with:
  - Accurate RoboCup field dimensions (9m x 6m)
  - Robot positions with orientation indicators
  - Ball position from multiple robot perspectives
  - Goal areas and field markings
- **Game State Panel**: Overall match information including:
  - Current game state (INITIAL, READY, SET, PLAY, END)
  - Team score and connected robot count
  - Ball possession status

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- macOS (primary target), Linux, or Windows
- Network connectivity between robots and laptop

### Installation

1. **Clone or download the dashboard system**:
   ```bash
   cd /path/to/your/dashboard/directory
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Note: `tkinter` is included with Python by default.

3. **Configure robot-side communication** (C++):
   Ensure your robots are configured to send data to the dashboard IP and port.
   Default configuration:
   - Dashboard IP: `192.168.4.77` (Mac laptop)
   - Dashboard Port: `8080`

### Running the Dashboard

#### Standard Mode (Receiving Real Robot Data)
```bash
python main.py
```

#### Custom Port
```bash
python main.py --port 9090
```

#### Simulation Mode (For Testing)
```bash
python main.py --simulate
```

#### Command Line Options
- `--port PORT`: UDP port to listen for robot data (default: 8080)
- `--simulate`: Start with simulated robot data for testing
- `--timeout SECONDS`: Robot timeout in seconds (default: 5)

## 🔧 Configuration

### Robot Side Configuration

The robots should be configured to send JSON data to the dashboard. You can set environment variables:

```bash
export DASHBOARD_IP="192.168.4.77"    # Your Mac's IP address
export DASHBOARD_PORT="8080"           # Dashboard port
```

### Network Setup

1. **Ensure all robots and the dashboard laptop are on the same WiFi network**
2. **Find your Mac's IP address**:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
3. **Update the robot configuration** to use your Mac's IP address
4. **Test connectivity**:
   ```bash
   # On robot: ping your_mac_ip
   ping 192.168.4.77
   ```

## 📊 Data Format

The dashboard expects JSON data from robots in the following format:

```json
{
  "robot_id": 0,
  "robot_name": "robot1",
  "team_id": 1,
  "timestamp": 1634567890.123,
  "game": {
    "state": "PLAY",
    "kickoff_side": true,
    "score": 2
  },
  "robot": {
    "pose": {
      "x": 1.5,
      "y": -0.8,
      "theta": 0.785
    },
    "ball": {
      "detected": true,
      "x": 2.1,
      "y": -0.5,
      "range": 0.8
    }
  },
  "collaboration": {
    "role": "master",
    "dynamic_role": 1,
    "has_possession": false,
    "possession_player": 2,
    "ball_cost": 1.2
  },
  "behavior": {
    "decision": "approach_ball",
    "ball_location_known": true
  },
  "performance": {
    "avg_loop_time": 0.015,
    "max_loop_time": 0.032
  },
  "head": {
    "pitch": -0.2,
    "yaw": 0.5
  },
  "recovery": {
    "state": 0,
    "available": true
  },
  "team_count": 2
}
```

## 🎮 Usage Guide

### Dashboard Interface

The dashboard interface consists of several main areas:

1. **Left Panel**:
   - **Game State**: Overall match status and team information
   - **Robot Status Cards**: Individual robot monitoring panels
   - **Control Panel**: Remote robot control commands

2. **Right Panel**:
   - **Field View**: 2D visualization of the soccer field with robot positions
   - **Ball Tracking**: Real-time ball position from robot sensors

3. **Status Bar**: Connection status and robot count

### Understanding Robot Status

- **Green Circle (●)**: Robot connected and sending data
- **Red Circle (●)**: Robot disconnected or not responding
- **Yellow Robot**: Robot has ball possession
- **Ball Indicators**: Orange circles show detected ball positions

### Using Remote Control

1. **Select Target**: Choose individual robot or "All Robots"
2. **Send Commands**:
   - **Build**: Trigger robot build process
   - **Start**: Start robot systems
   - **Stop**: Stop robot systems
   - **Emergency Stop**: Immediate stop for all robots (confirmation required)

### Troubleshooting

#### No Robots Appearing
1. Check network connectivity between robots and laptop
2. Verify robots are sending data to correct IP:PORT
3. Check firewall settings on laptop
4. Use simulation mode to test dashboard functionality:
   ```bash
   python main.py --simulate
   ```

#### Robots Keep Disconnecting
1. Check WiFi signal strength
2. Verify robot timeout settings (default: 5 seconds)
3. Increase timeout if needed:
   ```bash
   python main.py --timeout 10
   ```

#### Performance Issues
1. Close other applications to free up resources
2. Reduce GUI update frequency if needed
3. Check network bandwidth usage

## 🧪 Development and Testing

### Robot Simulator

For development and testing without physical robots:

```bash
# Run dashboard with simulator
python main.py --simulate

# Or run simulator separately
python robot_simulator.py --robots 3 --port 8080
```

The simulator generates realistic robot behavior including:
- Movement around the field
- Ball detection and tracking
- Game state transitions
- Performance metrics
- Collaboration behaviors

### Extending the Dashboard

The modular design allows easy extension:

1. **Add new data fields**: Update `RobotData` class in `dashboard_core.py`
2. **Create new visualizations**: Add widgets to `dashboard_gui.py`
3. **Implement new commands**: Extend `ControlPanel` class
4. **Add data processing**: Modify `DashboardCore` class

## 📋 System Requirements

### Minimum Requirements
- **CPU**: Dual-core 2.0 GHz
- **RAM**: 4 GB
- **Network**: WiFi 802.11n
- **OS**: macOS 10.14+, Ubuntu 18.04+, or Windows 10

### Recommended Requirements
- **CPU**: Quad-core 2.5 GHz or better
- **RAM**: 8 GB or more
- **Network**: WiFi 802.11ac or Ethernet
- **Display**: 1920x1080 or larger for optimal viewing

## 🔮 Future Enhancements

Based on `DASHBOARD_FEATURES.md`, planned enhancements include:

- **Advanced Analytics**: Machine learning integration and predictive maintenance
- **3D Visualization**: Three-dimensional field and robot visualization
- **Mobile Support**: Mobile app for remote monitoring
- **Data Logging**: Historical data analysis and replay capabilities
- **Multi-Monitor Support**: Distributed dashboard across multiple displays
- **Voice Alerts**: Audio notifications and speech synthesis
- **Customizable Layouts**: Drag-and-drop dashboard configuration

## 🤝 Contributing

1. Follow the existing code structure and documentation style
2. Test new features with the robot simulator
3. Update this README when adding new features
4. Ensure compatibility with the robot-side C++ implementation

## 📄 License

This project is part of the RoboCup robot system. Please follow your team's licensing requirements.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Test with simulation mode to isolate issues
3. Verify network connectivity and configuration
4. Review robot-side logs for transmission errors

---

**Happy Robotics! 🤖⚽** 