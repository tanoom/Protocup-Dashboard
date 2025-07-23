#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
from typing import Dict, Optional
from datetime import datetime
import sv_ttk

from dashboard_core import DashboardCore, RobotData


# Modern color scheme optimized for clean, professional look
COLORS = {
    'bg_primary': '#f5f5f5',      # Light background
    'bg_secondary': '#ffffff',    # White
    'bg_tertiary': '#f0f0f0',     # Light cards/panels
    'accent': '#0078d4',          # Windows 11 blue accent
    'accent_light': '#4ca5dc',    # Light blue
    'success': '#107c10',         # Windows 11 green
    'warning': '#ff8c00',         # Orange for warning
    'danger': '#d13438',          # Windows 11 red
    'text_primary': '#000000',    # Black text
    'text_secondary': '#666666',  # Dark gray text
    'text_muted': '#999999',      # Muted text
    'border': '#cccccc',          # Light border color
    'field_green': '#2d8f2d',     # Soccer field green
    'field_dark': '#1f6b1f',      # Darker field green
    'button_text': '#ffffff',     # Button text color - white
}

# Font configurations
FONTS = {
    'title': ('Segoe UI', 16, 'bold'),
    'heading': ('Segoe UI', 12, 'bold'),
    'subheading': ('Segoe UI', 10, 'bold'),
    'body': ('Segoe UI', 9),
    'caption': ('Segoe UI', 8),
    'mono': ('Consolas', 9),
}


class ModernFrame(tk.Frame):
    """A modern styled frame with rounded corners effect"""
    def __init__(self, parent, bg_color=None, **kwargs):
        bg_color = bg_color or COLORS['bg_tertiary']
        super().__init__(parent, bg=bg_color, relief='flat', bd=0, **kwargs)


class StatusIndicator(tk.Label):
    """Modern status indicator with better styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, font=('Segoe UI', 12), **kwargs)
        self.configure(bg=COLORS['bg_tertiary'])
    
    def set_status(self, connected: bool):
        if connected:
            self.configure(text="●", fg=COLORS['success'])
        else:
            self.configure(text="●", fg=COLORS['danger'])


class RobotStatusFrame(ModernFrame):
    """Modern robot status card"""
    
    def __init__(self, parent, robot_id: int):
        super().__init__(parent, bg_color=COLORS['bg_tertiary'])
        self.robot_id = robot_id
        self.robot_data: Optional[RobotData] = None
        
        self.configure(relief='solid', bd=1, highlightbackground=COLORS['border'])
        self.setup_widgets()
        
    def setup_widgets(self):
        """Setup modern robot status display"""
        # Set fixed width for the entire frame
        self.configure(padx=8, pady=8, width=420, height=250)
        self.pack_propagate(False)  # Prevent the frame from shrinking to fit content
        
        # Header section
        header = ModernFrame(self, bg_color=COLORS['bg_secondary'])
        header.pack(fill=tk.X, pady=(0, 8))
        
        self.name_label = tk.Label(header, text=f"Robot {self.robot_id}", 
                                  font=FONTS['heading'], fg=COLORS['text_primary'],
                                  bg=COLORS['bg_secondary'])
        self.name_label.pack(side=tk.LEFT, padx=8, pady=6)
        
        self.status_indicator = StatusIndicator(header)
        self.status_indicator.pack(side=tk.RIGHT, padx=8, pady=6)
        
        # Info grid with fixed spacing
        info_container = ModernFrame(self)
        info_container.pack(fill=tk.BOTH, expand=True, padx=4)
        
        self.info_labels = {}
        self.info_values = {}
        
        info_items = [
            ('Game State', 'game_state', 'UNKNOWN'),
            ('Position', 'position', '(0.0, 0.0)'),
            ('Role', 'role', 'unknown'),
            ('Ball', 'ball', 'Not detected'),
            ('Loop Time', 'performance', '0.0ms'),
            ('Decision', 'decision', 'unknown')
        ]
        
        for i, (label_text, key, default_value) in enumerate(info_items):
            # Label with fixed width
            label = tk.Label(info_container, text=f"{label_text}:", 
                           font=FONTS['caption'], fg=COLORS['text_secondary'],
                           bg=COLORS['bg_tertiary'], anchor='w', width=12)
            label.grid(row=i, column=0, sticky='w', padx=(4, 8), pady=2)
            
            # Value with fixed width to prevent resizing
            value = tk.Label(info_container, text=default_value,
                           font=FONTS['body'], fg=COLORS['text_primary'],
                           bg=COLORS['bg_tertiary'], anchor='w', width=25)
            value.grid(row=i, column=1, sticky='w', padx=(0, 4), pady=2)
            
            self.info_labels[key] = label
            self.info_values[key] = value
        
        # Configure grid with fixed column widths
        info_container.grid_columnconfigure(0, weight=0, minsize=100)
        info_container.grid_columnconfigure(1, weight=0, minsize=250)
        
    def update_data(self, robot_data: RobotData):
        """Update with modern styling and colors"""
        self.robot_data = robot_data
        
        # Update connection status and name
        self.status_indicator.set_status(robot_data.is_connected)
        if robot_data.is_connected:
            self.name_label.config(text=robot_data.robot_name, fg=COLORS['text_primary'])
        else:
            self.name_label.config(text=f"Robot {self.robot_id}", fg=COLORS['text_muted'])
            
        # Update game state with color coding
        game_state_color = COLORS['text_primary']
        if robot_data.game_state in ['PLAYING', 'READY']:
            game_state_color = COLORS['success']
        elif robot_data.game_state in ['PENALIZED', 'FINISHED', 'SET']:
            game_state_color = COLORS['danger']
            
        self.info_values['game_state'].config(text=robot_data.game_state, fg=game_state_color)
        
        # Update position
        self.info_values['position'].config(text=f"({robot_data.pose_x:.1f}, {robot_data.pose_y:.1f})")
        
        # Update role with possession indicator
        role_text = f"{robot_data.role}"
        role_color = COLORS['text_primary']
        if robot_data.has_possession:
            role_text += " [BALL]"
            role_color = COLORS['warning']
        self.info_values['role'].config(text=role_text, fg=role_color)
        
        # Update ball detection with colors
        if robot_data.ball_detected:
            ball_text = f"Detected ({robot_data.ball_x:.1f}, {robot_data.ball_y:.1f})"
            ball_color = COLORS['success']
        else:
            ball_text = "Not detected"
            ball_color = COLORS['text_muted']
        self.info_values['ball'].config(text=ball_text, fg=ball_color)
            
        # Update performance with color coding
        loop_time_ms = robot_data.avg_loop_time * 1000
        perf_color = COLORS['success'] if loop_time_ms < 50 else COLORS['warning'] if loop_time_ms < 100 else COLORS['danger']
        self.info_values['performance'].config(text=f"{loop_time_ms:.1f}ms", fg=perf_color)
        
        # Update decision
        self.info_values['decision'].config(text=robot_data.decision)


class ModernFieldCanvas(tk.Canvas):
    """Beautiful modern soccer field visualization"""
    
    def __init__(self, parent, width=700, height=500):
        super().__init__(parent, width=width, height=height, 
                        bg=COLORS['field_green'], highlightthickness=0)
        self.canvas_width = width
        self.canvas_height = height
        
        # Field dimensions
        self.field_width = 9.0
        self.field_height = 6.0
        
        # Scale factors
        self.scale_x = (width - 60) / self.field_width
        self.scale_y = (height - 60) / self.field_height
        
        self.draw_modern_field()
        
    def draw_modern_field(self):
        """Draw a beautiful modern soccer field"""
        self.delete("all")
        
        # Field margins
        margin = 30
        field_left = margin
        field_right = self.canvas_width - margin
        field_top = margin
        field_bottom = self.canvas_height - margin
        
        # Create gradient effect background
        self.create_rectangle(0, 0, self.canvas_width, self.canvas_height, 
                            fill=COLORS['field_dark'], outline="")
        
        # Main field area with lighter green
        self.create_rectangle(field_left, field_top, field_right, field_bottom, 
                            fill=COLORS['field_green'], outline="")
        
        # Field border with modern styling
        self.create_rectangle(field_left, field_top, field_right, field_bottom, 
                            outline='white', width=3)
        
        # Center line with glow effect
        center_x = self.canvas_width // 2
        # Shadow/glow effect
        self.create_line(center_x+1, field_top+1, center_x+1, field_bottom+1, 
                        fill='#666666', width=4)
        self.create_line(center_x, field_top, center_x, field_bottom, 
                        fill='white', width=3)
        
        # Center circle with modern styling
        center_y = self.canvas_height // 2
        circle_radius = 1.5 * min(self.scale_x, self.scale_y)
        # Shadow
        self.create_oval(center_x - circle_radius + 2, center_y - circle_radius + 2,
                        center_x + circle_radius + 2, center_y + circle_radius + 2,
                        outline='#666666', width=4)
        # Main circle
        self.create_oval(center_x - circle_radius, center_y - circle_radius,
                        center_x + circle_radius, center_y + circle_radius,
                        outline='white', width=3)
        
        # Modern goals with gradient effect
        goal_width = 1.5 * self.scale_y
        goal_depth = 0.5 * self.scale_x
        goal_y_start = center_y - goal_width // 2
        goal_y_end = center_y + goal_width // 2
        
        # Left goal with modern styling
        self.create_rectangle(field_left - goal_depth, goal_y_start,
                            field_left, goal_y_end,
                            fill='#e6f3ff', outline='white', width=3)
        
        # Right goal
        self.create_rectangle(field_right, goal_y_start,
                            field_right + goal_depth, goal_y_end,
                            fill='#ffe6e6', outline='white', width=3)
        
        # Goal areas with subtle styling
        goal_area_width = 3.0 * self.scale_y
        goal_area_depth = 1.5 * self.scale_x
        goal_area_y_start = center_y - goal_area_width // 2
        goal_area_y_end = center_y + goal_area_width // 2
        
        # Left goal area
        self.create_rectangle(field_left, goal_area_y_start,
                            field_left + goal_area_depth, goal_area_y_end,
                            outline='white', width=2)
        
        # Right goal area
        self.create_rectangle(field_right - goal_area_depth, goal_area_y_start,
                            field_right, goal_area_y_end,
                            outline='white', width=2)
        
        # Add corner arcs for extra detail
        corner_radius = 20
        # Top-left corner
        self.create_arc(field_left - corner_radius, field_top - corner_radius,
                       field_left + corner_radius, field_top + corner_radius,
                       start=0, extent=90, outline='white', width=2, style='arc')
        
        # Add field texture lines
        for i in range(1, 8):
            x = field_left + (field_right - field_left) * i / 8
            self.create_line(x, field_top, x, field_bottom, 
                           fill='#228B22', width=1, stipple='gray50')
        
    def field_to_canvas(self, x, y):
        """Convert field coordinates to canvas coordinates"""
        canvas_x = (x + self.field_width/2) * self.scale_x + 30
        canvas_y = (-y + self.field_height/2) * self.scale_y + 30
        return canvas_x, canvas_y
        
    def update_robots(self, robots: Dict[int, RobotData]):
        """Update robots with modern 3D-like visualization"""
        self.delete("robot")
        self.delete("ball")
        
        for robot_id, robot in robots.items():
            if not robot.is_connected:
                continue
                
            canvas_x, canvas_y = self.field_to_canvas(robot.pose_x, robot.pose_y)
            
            # Robot with modern styling and shadow
            robot_size = 12
            
            # Determine robot color
            if robot.has_possession:
                robot_color = COLORS['warning']
                border_color = '#f39c12'
            elif robot.team_id == 1:
                robot_color = COLORS['accent']
                border_color = COLORS['accent_light']
            else:
                robot_color = COLORS['danger']
                border_color = '#ff6b6b'
            
            # Drop shadow
            self.create_oval(canvas_x - robot_size + 2, canvas_y - robot_size + 2,
                           canvas_x + robot_size + 2, canvas_y + robot_size + 2,
                           fill='#333333', outline='', tags="robot")
            
            # Main robot circle
            self.create_oval(canvas_x - robot_size, canvas_y - robot_size,
                           canvas_x + robot_size, canvas_y + robot_size,
                           fill=robot_color, outline=border_color, width=3, tags="robot")
            
            # Robot ID with better visibility
            self.create_text(canvas_x, canvas_y, text=str(robot_id), 
                           fill='white', font=FONTS['subheading'], tags="robot")
            
            # Direction indicator with modern styling
            direction_length = 20
            end_x = canvas_x + direction_length * math.cos(robot.pose_theta)
            end_y = canvas_y - direction_length * math.sin(robot.pose_theta)
            
            # Direction line with gradient effect
            self.create_line(canvas_x, canvas_y, end_x, end_y,
                           fill='white', width=4, tags="robot")
            self.create_line(canvas_x, canvas_y, end_x, end_y,
                           fill=border_color, width=2, tags="robot")
            
            # Ball visualization
            if robot.ball_detected:
                ball_canvas_x, ball_canvas_y = self.field_to_canvas(robot.ball_x, robot.ball_y)
                # Ball shadow
                self.create_oval(ball_canvas_x - 6 + 1, ball_canvas_y - 6 + 1,
                               ball_canvas_x + 6 + 1, ball_canvas_y + 6 + 1,
                               fill='#333333', outline='', tags="ball")
                # Ball
                self.create_oval(ball_canvas_x - 6, ball_canvas_y - 6,
                               ball_canvas_x + 6, ball_canvas_y + 6,
                               fill='#ff8c00', outline='#ff7f00', width=2, tags="ball")


class ModernButton(tk.Button):
    """Modern styled button"""
    def __init__(self, parent, text, command=None, style='primary', width=None, height=None, **kwargs):
        styles = {
            'primary': {'bg': COLORS['accent'], 'fg': COLORS['button_text'], 'activebackground': COLORS['accent_light']},
            'success': {'bg': COLORS['success'], 'fg': COLORS['button_text'], 'activebackground': '#52c993'},
            'warning': {'bg': COLORS['warning'], 'fg': COLORS['button_text'], 'activebackground': '#f8c441'},
            'danger': {'bg': COLORS['danger'], 'fg': COLORS['button_text'], 'activebackground': '#fa6565'},
        }
        
        style_config = styles.get(style, styles['primary'])
        
        # Add size parameters if provided
        if width is not None:
            style_config['width'] = width
        if height is not None:
            style_config['height'] = height
        
        super().__init__(parent, text=text, command=command,
                        font=FONTS['body'], relief='flat', bd=0,
                        cursor='hand2', **style_config, **kwargs)
        
        # Force modern styling after creation (fixes sizing conflicts)
        self.configure(relief='flat', bd=0, highlightthickness=0)


class ControlPanel(ModernFrame):
    """Modern control panel"""
    
    def __init__(self, parent, dashboard_core: DashboardCore):
        super().__init__(parent)
        self.dashboard_core = dashboard_core
        self.setup_widgets()
        
    def setup_widgets(self):
        """Setup modern control panel"""
        # Title
        title = tk.Label(self, text="Robot Control", font=FONTS['heading'], 
                        fg=COLORS['text_primary'], bg=COLORS['bg_tertiary'])
        title.pack(pady=(8, 12))
        
        # Robot selection with modern styling
        select_frame = ModernFrame(self, bg_color=COLORS['bg_secondary'])
        select_frame.pack(fill=tk.X, padx=8, pady=(0, 16))
        
        tk.Label(select_frame, text="Target Robot:", font=FONTS['body'],
                fg=COLORS['text_secondary'], bg=COLORS['bg_secondary']).pack(side=tk.LEFT, padx=8, pady=8)
        
        self.robot_var = tk.StringVar(value="All Robots")
        
        self.robot_combo = ttk.Combobox(select_frame, textvariable=self.robot_var, 
                                       values=["All Robots"], state="readonly")
        self.robot_combo.pack(side=tk.LEFT, padx=8, pady=2, fill=tk.X, expand=True)
        
        # Command buttons with modern styling
        button_frame = ModernFrame(self)
        button_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        buttons = [
            ("Build", self.send_build_command, 'primary'),
            ("Start", self.send_start_command, 'success'),
            ("Stop", self.send_stop_command, 'warning'),
        ]
        
        for text, command, style in buttons:
            btn = ModernButton(button_frame, text=text, command=command, style=style)
            btn.pack(side=tk.LEFT, padx=8, pady=4, fill=tk.X, expand=True)
        
        # Emergency stop - separate and prominent
        emergency_frame = ModernFrame(self, bg_color=COLORS['danger'])
        emergency_frame.pack(fill=tk.X, padx=8, pady=4)
        
        emergency_btn = ModernButton(emergency_frame, text="EMERGENCY STOP", 
                                   command=self.send_emergency_stop, style='danger')
        emergency_btn.pack(fill=tk.X, padx=4, pady=4)
        
    def update_robot_list(self, robots: Dict[int, RobotData]):
        """Update robot dropdown"""
        robot_names = ["All Robots"] + [f"Robot {rid} ({robot.robot_name})" 
                                       for rid, robot in robots.items() if robot.is_connected]
        self.robot_combo['values'] = robot_names
        
    def send_build_command(self):
        target = self.robot_var.get()
        messagebox.showinfo("Command", f"Build command sent to: {target}")
        
    def send_start_command(self):
        target = self.robot_var.get()
        messagebox.showinfo("Command", f"Start command sent to: {target}")
        
    def send_stop_command(self):
        target = self.robot_var.get()
        messagebox.showinfo("Command", f"Stop command sent to: {target}")
        
    def send_emergency_stop(self):
        result = messagebox.askyesno("Emergency Stop", 
                                    "Send EMERGENCY STOP to ALL robots?",
                                    icon="warning")
        if result:
            messagebox.showinfo("Emergency Stop", "Emergency stop sent to all robots!")


class GameStatePanel(ModernFrame):
    """Modern game state panel"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_widgets()
        
    def setup_widgets(self):
        """Setup modern game state display"""
        # Title with better styling
        title_frame = ModernFrame(self, bg_color=COLORS['bg_secondary'])
        title_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        title = tk.Label(title_frame, text="Game State", font=FONTS['heading'], 
                        fg=COLORS['text_primary'], bg=COLORS['bg_secondary'])
        title.pack(pady=8)
        
        # Info grid with modern cards and better spacing
        self.info_frame = ModernFrame(self, bg_color=COLORS['bg_secondary'])
        self.info_frame.pack(fill=tk.X, padx=8, pady=(4, 8))
        
        # Create info items as modern cards with borders
        self.info_items = {}
        items = [
            ('State', 'state', 'UNKNOWN', '🎮'),
            ('Score', 'score', '0', '⚽'),
            ('Connected', 'connected', '0/3', '📡'),
            ('Ball Possession', 'possession', 'None', '🏃‍♂️')
        ]
        
        for i, (label_text, key, default_value, icon) in enumerate(items):
            # Create card with border and shadow effect
            item_frame = ModernFrame(self.info_frame, bg_color=COLORS['bg_tertiary'])
            item_frame.configure(relief='solid', bd=1, highlightbackground=COLORS['border'])
            item_frame.grid(row=i//2, column=i%2, padx=8, pady=6, sticky='ew', ipadx=4, ipady=4)
            
            # Header with icon and label
            header_frame = tk.Frame(item_frame, bg=COLORS['bg_tertiary'])
            header_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
            
            icon_label = tk.Label(header_frame, text=icon, font=('Segoe UI', 12),
                                bg=COLORS['bg_tertiary'])
            icon_label.pack(side=tk.LEFT)
            
            label = tk.Label(header_frame, text=label_text, font=FONTS['caption'],
                           fg=COLORS['text_secondary'], bg=COLORS['bg_tertiary'])
            label.pack(side=tk.LEFT, padx=(4, 0))
            
            # Value with better typography
            value = tk.Label(item_frame, text=default_value, font=FONTS['subheading'],
                           fg=COLORS['text_primary'], bg=COLORS['bg_tertiary'])
            value.pack(anchor='w', padx=8, pady=(0, 8))
            
            self.info_items[key] = value
        
        # Configure grid with better spacing
        self.info_frame.grid_columnconfigure(0, weight=1, minsize=150)
        self.info_frame.grid_columnconfigure(1, weight=1, minsize=150)
        
    def update_game_state(self, robots: Dict[int, RobotData]):
        """Update game state with colors"""
        if not robots:
            return
            
        connected_robots = [robot for robot in robots.values() if robot.is_connected]
        if connected_robots:
            sample_robot = connected_robots[0]
            
            # Update state with color
            state_color = COLORS['text_primary']
            if sample_robot.game_state in ['PLAYING', 'READY']:
                state_color = COLORS['success']
            elif sample_robot.game_state in ['PENALIZED', 'FINISHED', 'SET']:
                state_color = COLORS['danger']
            
            self.info_items['state'].config(text=sample_robot.game_state, fg=state_color)
            self.info_items['score'].config(text=str(sample_robot.score))
        
        # Update connection count
        connected_count = len(connected_robots)
        total_count = 3
        conn_color = COLORS['success'] if connected_count == total_count else COLORS['warning']
        self.info_items['connected'].config(text=f"{connected_count}/{total_count}", fg=conn_color)
        
        # Ball possession
        possession_robot = next((robot for robot in connected_robots if robot.has_possession), None)
        if possession_robot:
            self.info_items['possession'].config(text=f"Robot {possession_robot.robot_id}", fg=COLORS['success'])
        else:
            self.info_items['possession'].config(text="None", fg=COLORS['text_muted'])


class RoboCupDashboard:
    """Beautiful modern RoboCup dashboard"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RoboCup Humanoid Robot Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['bg_primary'])
        
        # Initialize dashboard core
        self.dashboard_core = DashboardCore()
        self.dashboard_core.add_update_callback(self.on_robot_update)
        
        self.robot_frames: Dict[int, RobotStatusFrame] = {}
        
        self.setup_modern_gui()
        self.start_dashboard()
        
    def setup_modern_gui(self):
        """Setup the beautiful modern GUI"""
        # Apply Sun Valley light theme for ttk widgets
        sv_ttk.set_theme("light")
        
        # Title bar
        title_frame = ModernFrame(self.root, bg_color=COLORS['bg_secondary'])
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(title_frame, text="RoboCup Humanoid Dashboard", 
                              font=FONTS['title'], fg=COLORS['text_primary'],
                              bg=COLORS['bg_secondary'])
        title_label.pack(pady=12)
        
        # Main content area
        content_frame = ModernFrame(self.root, bg_color=COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Create horizontal layout
        main_paned = tk.PanedWindow(content_frame, orient=tk.HORIZONTAL, 
                                   bg=COLORS['bg_primary'], sashwidth=8,
                                   sashrelief='flat')
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls and Status
        left_panel = ModernFrame(main_paned, bg_color=COLORS['bg_secondary'])
        main_paned.add(left_panel, width=500, minsize=400)
        
        # Game state
        self.game_panel = GameStatePanel(left_panel)
        self.game_panel.pack(fill=tk.X, padx=8, pady=8)
        
        # Robot status container with scrollbar
        robot_container = ModernFrame(left_panel)
        robot_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        robot_title = tk.Label(robot_container, text="Robot Status", font=FONTS['heading'],
                              fg=COLORS['text_primary'], bg=COLORS['bg_secondary'])
        robot_title.pack(pady=(8, 4))
        
        # Scrollable robot panel
        canvas = tk.Canvas(robot_container, bg=COLORS['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(robot_container, orient="vertical", command=canvas.yview)
        self.robot_panel = ModernFrame(canvas, bg_color=COLORS['bg_secondary'])
        
        self.robot_panel.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.robot_panel, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Control panel
        self.control_panel = ControlPanel(left_panel, self.dashboard_core)
        self.control_panel.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        # Right panel - Field View
        right_panel = ModernFrame(main_paned, bg_color=COLORS['bg_secondary'])
        main_paned.add(right_panel, minsize=600)
        
        field_title = tk.Label(right_panel, text="Field View", font=FONTS['heading'],
                              fg=COLORS['text_primary'], bg=COLORS['bg_secondary'])
        field_title.pack(pady=(12, 8))
        
        # Field canvas with modern styling
        field_container = ModernFrame(right_panel, bg_color=COLORS['bg_tertiary'])
        field_container.pack(padx=12, pady=(0, 12), fill=tk.BOTH, expand=True)
        
        self.field_canvas = ModernFieldCanvas(field_container)
        self.field_canvas.pack(pady=8)
        
        # Modern status bar
        status_frame = ModernFrame(self.root, bg_color=COLORS['bg_secondary'])
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = tk.Label(status_frame, text="Dashboard starting...", 
                                  font=FONTS['caption'], fg=COLORS['text_secondary'],
                                  bg=COLORS['bg_secondary'], anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, padx=8, pady=4)
        
        # Time display
        self.time_label = tk.Label(status_frame, text="", font=FONTS['mono'],
                                  fg=COLORS['text_muted'], bg=COLORS['bg_secondary'])
        self.time_label.pack(side=tk.RIGHT, padx=8, pady=4)
        
    def start_dashboard(self):
        """Start the dashboard"""
        self.dashboard_core.start()
        self.status_bar.config(text="Dashboard running - Waiting for robots...")
        self.update_gui()
        
    def update_gui(self):
        """Update GUI with smooth animations"""
        try:
            robots = self.dashboard_core.get_robots()
            
            # Update robot status frames
            for robot_id, robot_data in robots.items():
                if robot_id not in self.robot_frames:
                    frame = RobotStatusFrame(self.robot_panel, robot_id)
                    frame.pack(fill=tk.X, padx=4, pady=4)
                    self.robot_frames[robot_id] = frame
                    
                self.robot_frames[robot_id].update_data(robot_data)
            
            # Update visualizations
            self.field_canvas.update_robots(robots)
            self.game_panel.update_game_state(robots)
            self.control_panel.update_robot_list(robots)
            
            # Update status
            connected_count = len(self.dashboard_core.get_connected_robots())
            total_count = len(robots)
            status_icon = "🟢" if connected_count > 0 else "🔴"
            self.status_bar.config(text=f"{status_icon} Dashboard running - {connected_count}/{total_count} robots connected")
            
            # Update time
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_label.config(text=current_time)
            
        except Exception as e:
            print(f"GUI update error: {e}")
            
        self.root.after(100, self.update_gui)
        
    def on_robot_update(self, robot_id: int, robot_data: RobotData):
        """Callback for robot updates"""
        pass
        
    def run(self):
        """Run the beautiful dashboard"""
        try:
            self.root.mainloop()
        finally:
            self.dashboard_core.stop()


if __name__ == "__main__":
    dashboard = RoboCupDashboard()
    dashboard.run() 