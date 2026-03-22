"""
LevelLife - Beta 1.4.4
Changes: No restart needed for theme/clear save!

Version History:
- Beta 1.0.0: Initial release
- Beta 1.1.0: Timer countdown
- Beta 1.2.0: Save management  
- Beta 1.3.0: 8 hearts, menu, edit, difficulty
- Beta 1.4.0: Bigger buttons, custom skills
- Beta 1.4.1: Fixed task completion per day
- Beta 1.4.2: Fixed overlapping text, added light mode (broken)
- Beta 1.4.3: FIXED light mode!
- Beta 1.4.4: No restart needed! Instant theme/clear
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
import json
import os
import time
from datetime import datetime

# ==================== DATA MANAGER ====================
class DataManager:
    def __init__(self):
        self.data_file = "levellife_data.json"
        self.data = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return self.default_data()
    
    def default_data(self):
        return {
            "lives": 8,  # Changed from 10 to 8
            "max_lives": 8,
            "skills": {
                "Cooking": {"xp": 0, "level": 1, "max_xp": 100},
                "Programming": {"xp": 0, "level": 1, "max_xp": 100},
                "Social": {"xp": 0, "level": 1, "max_xp": 100},
                "Overall": {"xp": 0, "level": 1, "max_xp": 100}
            },
            "custom_skills": [],  # User-created skills
            "tasks": [],
            "last_day": None,
            "current_day_view": 0,
            "light_mode": False  # Theme setting
        }
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def clear_all_data(self):
        """Delete save file and reset"""
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        self.data = self.default_data()
        self.save_data()
    
    def add_custom_skill(self, skill_name):
        """Add a new custom skill"""
        if skill_name not in self.data["skills"] and skill_name not in self.data["custom_skills"]:
            self.data["custom_skills"].append(skill_name)
            self.data["skills"][skill_name] = {"xp": 0, "level": 1, "max_xp": 100}
            self.save_data()
            return True
        return False
    
    def get_all_skills(self):
        """Get list of all skills (default + custom)"""
        default = ["Cooking", "Programming", "Social"]
        return default + self.data.get("custom_skills", [])
    
    def add_xp(self, skill, amount):
        """Add XP to a skill and level up if needed"""
        if skill not in self.data["skills"]:
            return
        
        skill_data = self.data["skills"][skill]
        skill_data["xp"] += amount
        
        # Level up and add overflow to Overall
        overflow_xp = 0
        while skill_data["xp"] >= skill_data["max_xp"]:
            overflow = skill_data["xp"] - skill_data["max_xp"]
            skill_data["xp"] = 0  # Reset XP on level up
            skill_data["level"] += 1
            skill_data["max_xp"] = int(skill_data["max_xp"] * 1.15)
            
            # Add overflow to next level or Overall if still overflow
            if overflow > 0:
                if overflow < skill_data["max_xp"]:
                    skill_data["xp"] = overflow
                else:
                    # Excess goes to Overall
                    overflow_xp += overflow
        
        # Add overflow to Overall XP
        if overflow_xp > 0 and skill != "Overall":
            self.data["skills"]["Overall"]["xp"] += overflow_xp
        
        self.update_overall_xp()
        self.save_data()
    
    def update_overall_xp(self):
        """Calculate overall level based on current Overall XP"""
        overall = self.data["skills"]["Overall"]
        
        # Recalculate level from XP
        level = 1
        max_xp = 100
        temp_xp = overall["xp"]
        
        while temp_xp >= max_xp:
            temp_xp -= max_xp
            level += 1
            max_xp = int(max_xp * 1.15)
        
        overall["level"] = level
        overall["max_xp"] = max_xp
        overall["xp"] = temp_xp
    
    def check_daily_life_loss(self):
        """Check if we need to lose a life"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.data["last_day"] and self.data["last_day"] != today:
            yesterday = self.data["last_day"]
            yesterday_weekday = (datetime.now().weekday() - 1) % 7
            
            tasks_done_yesterday = any(
                task.get("completed") and 
                task.get("completed_date") == yesterday and
                task.get("completed_day") == yesterday_weekday and
                yesterday_weekday in task.get("days", [])
                for task in self.data["tasks"]
            )
            
            if not tasks_done_yesterday:
                self.data["lives"] = max(0, self.data["lives"] - 1)
            
            # Reset completion status for new day
            # Tasks can be completed again on their scheduled days
            for task in self.data["tasks"]:
                # Only reset if the completion was for a previous day
                if task.get("completed_date") != today:
                    task["completed"] = False
                    if "completed_day" in task:
                        del task["completed_day"]
                    if "timer_started" in task:
                        del task["timer_started"]
        
        self.data["last_day"] = today
        self.save_data()
    
    def delete_task(self, task, day_index):
        """Delete task from specific day"""
        if day_index in task.get("days", []):
            task["days"].remove(day_index)
            
            if not task["days"]:
                self.data["tasks"].remove(task)
            
            self.save_data()
    
    def update_task(self, old_task, new_data):
        """Update an existing task"""
        for i, task in enumerate(self.data["tasks"]):
            if task is old_task:
                self.data["tasks"][i].update(new_data)
                self.save_data()
                return True
        return False
    
    def get_tasks_for_day(self, day_index):
        """Get tasks for specific day"""
        return [t for t in self.data["tasks"] if day_index in t.get("days", [])]

# Difficulty multipliers
DIFFICULTY_MULTIPLIERS = {
    "Easy": 1.0,
    "Medium": 1.5,
    "Hard": 2.0,
    "Extreme": 3.0
}

# ==================== TIMER WIDGET ====================
class TimerWidget(BoxLayout):
    def __init__(self, task, on_complete_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, None)
        self.height = 80  # Increased from 60
        self.task = task
        self.on_complete_callback = on_complete_callback
        
        self.time_label = Label(
            text="",
            size_hint=(1, 0.3),
            font_size='13sp',
            bold=True
        )
        
        self.progress = ProgressBar(max=100, size_hint=(1, 0.25))
        
        btn_box = BoxLayout(size_hint=(1, 0.45), spacing=3)  # Increased from 0.3
        
        self.start_btn = Button(
            text="Start Timer",
            background_color=(0.3, 0.8, 0.3, 1),
            font_size='13sp'  # Increased from 11sp
        )
        self.start_btn.bind(on_press=self.start_timer)
        
        self.complete_btn = Button(
            text="Complete",
            background_color=(0.3, 0.6, 0.9, 1),
            font_size='13sp',  # Increased from 11sp
            disabled=True
        )
        self.complete_btn.bind(on_press=self.complete_task)
        
        btn_box.add_widget(self.start_btn)
        btn_box.add_widget(self.complete_btn)
        
        self.add_widget(self.time_label)
        self.add_widget(self.progress)
        self.add_widget(btn_box)
        
        self.clock_event = None
        self.update_display()
    
    def start_timer(self, instance):
        self.task["timer_started"] = time.time()
        self.start_btn.disabled = True
        self.complete_btn.disabled = False
        self.clock_event = Clock.schedule_interval(self.update_timer, 1.0)
    
    def update_timer(self, dt):
        if not self.task.get("timer_started"):
            return False
        
        elapsed = time.time() - self.task["timer_started"]
        total_seconds = self.task["timer"] * 60
        remaining = max(0, total_seconds - elapsed)
        
        progress_percent = (elapsed / total_seconds) * 100
        self.progress.value = min(100, progress_percent)
        
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        if remaining > 0:
            self.time_label.text = f"{minutes:02d}:{seconds:02d} remaining"
            self.time_label.color = (0.3, 0.9, 0.3, 1) if remaining > 60 else (0.9, 0.6, 0.2, 1)
        else:
            self.time_label.text = "TIME UP!"
            self.time_label.color = (0.9, 0.3, 0.3, 1)
        
        self.update_display()
    
    def update_display(self):
        if not self.task.get("timer"):
            return
        
        if not self.task.get("timer_started"):
            self.time_label.text = f"Timer: {self.task['timer']} min"
            self.time_label.color = (0.7, 0.7, 0.8, 1)
            self.progress.value = 0
    
    def complete_task(self, instance):
        if self.clock_event:
            self.clock_event.cancel()
        self.on_complete_callback(self.task)
    
    def cleanup(self):
        if self.clock_event:
            self.clock_event.cancel()

# ==================== MAIN APP ====================
class LevelLifeApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_mgr = DataManager()
        self.data_mgr.check_daily_life_loss()
        self.current_day = datetime.now().weekday()
        self.timer_widgets = []
        
        # Theme colors
        self.update_theme_colors()
    
    def update_theme_colors(self):
        """Update colors based on light/dark mode"""
        is_light = self.data_mgr.data.get("light_mode", False)
        
        if is_light:
            # Light mode colors
            self.bg_color = (0.95, 0.95, 0.97, 1)
            self.card_color = (1, 1, 1, 1)
            self.text_color = (0.1, 0.1, 0.1, 1)
            self.accent_color = (0.2, 0.4, 0.8, 1)
            self.secondary_bg = (0.9, 0.9, 0.92, 1)
        else:
            # Dark mode colors
            self.bg_color = (0.15, 0.15, 0.2, 1)
            self.card_color = (0.25, 0.25, 0.3, 1)
            self.text_color = (1, 1, 1, 1)
            self.accent_color = (0.3, 0.6, 0.9, 1)
            self.secondary_bg = (0.2, 0.2, 0.25, 1)
    
    def toggle_theme(self):
        """Toggle between light and dark mode - NO RESTART"""
        self.data_mgr.data["light_mode"] = not self.data_mgr.data.get("light_mode", False)
        self.data_mgr.save_data()
        self.update_theme_colors()
        
        # Rebuild UI without restarting app
        self.rebuild_ui()
    
    def rebuild_ui(self):
        """Rebuild entire UI with current theme"""
        # Clear current UI
        self.root.clear_widgets()
        
        # Build fresh UI
        main_layout = BoxLayout(orientation='vertical', padding=5, spacing=5)
        
        # Set background
        with main_layout.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Add sections
        top_bar = self.create_top_bar()
        main_layout.add_widget(top_bar)
        
        char_section = self.create_character_section()
        main_layout.add_widget(char_section)
        
        tasks_section = self.create_tasks_section()
        main_layout.add_widget(tasks_section)
        
        hotbar = self.create_hotbar()
        main_layout.add_widget(hotbar)
        
        # Add to root
        self.root.add_widget(main_layout)
    
    def build(self):
        self.title = "LevelLife"
        
        main_layout = BoxLayout(orientation='vertical', padding=5, spacing=5)
        
        top_bar = self.create_top_bar()
        main_layout.add_widget(top_bar)
        
        char_section = self.create_character_section()
        main_layout.add_widget(char_section)
        
        tasks_section = self.create_tasks_section()
        main_layout.add_widget(tasks_section)
        
        hotbar = self.create_hotbar()
        main_layout.add_widget(hotbar)
        
        with main_layout.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        return main_layout
    
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
        # Update color when rect updates
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(size=instance.size, pos=instance.pos)
    
    def create_top_bar(self):
        """Lives display"""
        layout = BoxLayout(size_hint=(1, 0.08), spacing=10, padding=[10, 5])
        
        title_label = Label(
            text="LEVELLIFE",
            size_hint=(0.5, 1),
            font_size='20sp',
            bold=True,
            color=(1, 0.84, 0, 1)  # Always gold
        )
        
        lives = self.data_mgr.data['lives']
        max_lives = self.data_mgr.data.get('max_lives', 8)
        hearts = "<3 " * lives
        lives_label = Label(
            text=f"Lives: {hearts}({lives}/{max_lives})",
            size_hint=(0.5, 1),
            font_size='14sp',
            color=(1, 0.3, 0.3, 1),  # Always red for hearts
            halign='right'
        )
        lives_label.bind(size=lives_label.setter('text_size'))
        
        layout.add_widget(title_label)
        layout.add_widget(lives_label)
        
        self.lives_label = lives_label
        return layout
    
    def create_character_section(self):
        """Character + XP"""
        layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5, padding=5)
        
        # Character sprite (pixel art)
        char_box = BoxLayout(size_hint=(1, 0.5))
        
        # Create a simple pixel character
        char_canvas = BoxLayout(size_hint=(None, None), size=(100, 100), pos_hint={'center_x': 0.5})
        
        is_light = self.data_mgr.data.get("light_mode", False)
        
        with char_canvas.canvas:
            # Outline in light mode
            if is_light:
                Color(0.2, 0.2, 0.2, 1)
                Rectangle(pos=(char_canvas.x + 28, char_canvas.y + 58), size=(44, 34))
            
            # Skin color (head)
            Color(0.95, 0.76, 0.65, 1)
            Rectangle(pos=(char_canvas.x + 30, char_canvas.y + 60), size=(40, 30))
            
            # Eyes
            Color(0.2, 0.2, 0.2, 1)
            Rectangle(pos=(char_canvas.x + 38, char_canvas.y + 73), size=(8, 8))
            Rectangle(pos=(char_canvas.x + 54, char_canvas.y + 73), size=(8, 8))
            
            # Mouth
            Rectangle(pos=(char_canvas.x + 42, char_canvas.y + 65), size=(16, 3))
            
            # Hair
            Color(0.3, 0.2, 0.1, 1)
            Rectangle(pos=(char_canvas.x + 28, char_canvas.y + 82), size=(44, 12))
            
            # Body outline in light mode
            if is_light:
                Color(0.2, 0.2, 0.2, 1)
                Rectangle(pos=(char_canvas.x + 23, char_canvas.y + 28), size=(54, 34))
            
            # Body (shirt)
            Color(0.3, 0.6, 0.9, 1)
            Rectangle(pos=(char_canvas.x + 25, char_canvas.y + 30), size=(50, 30))
            
            # Arms
            Color(0.95, 0.76, 0.65, 1)
            Rectangle(pos=(char_canvas.x + 15, char_canvas.y + 35), size=(10, 20))
            Rectangle(pos=(char_canvas.x + 75, char_canvas.y + 35), size=(10, 20))
            
            # Legs (pants)
            Color(0.2, 0.2, 0.3, 1)
            Rectangle(pos=(char_canvas.x + 32, char_canvas.y + 5), size=(15, 25))
            Rectangle(pos=(char_canvas.x + 53, char_canvas.y + 5), size=(15, 25))
            
            # Shoes
            Color(0.4, 0.3, 0.2, 1)
            Rectangle(pos=(char_canvas.x + 30, char_canvas.y), size=(18, 8))
            Rectangle(pos=(char_canvas.x + 52, char_canvas.y), size=(18, 8))
        
        char_box.add_widget(char_canvas)
        
        overall_data = self.data_mgr.data["skills"]["Overall"]
        xp_box = BoxLayout(orientation='vertical', size_hint=(1, 0.5), spacing=3)
        
        xp_info = Label(
            text=f"Level {overall_data['level']} | {overall_data['xp']}/{overall_data['max_xp']} XP",
            font_size='14sp',
            size_hint=(1, 0.4),
            color=self.text_color
        )
        
        progress_container = BoxLayout(size_hint=(1, 0.3), padding=[20, 0])
        progress_bg = BoxLayout(size_hint=(1, 1))
        with progress_bg.canvas.before:
            Color(*self.secondary_bg)
            Rectangle(pos=progress_bg.pos, size=progress_bg.size)
        
        progress_bar = BoxLayout(size_hint=(overall_data['xp'] / overall_data['max_xp'], 1))
        with progress_bar.canvas.before:
            Color(0.3, 0.9, 0.3, 1)
            Rectangle(pos=progress_bar.pos, size=progress_bar.size)
        
        progress_bg.add_widget(progress_bar)
        progress_container.add_widget(progress_bg)
        
        skills_btn = Button(
            text="View All Skills",
            size_hint=(1, 0.3),
            background_color=self.accent_color,
            on_press=self.show_skills
        )
        
        xp_box.add_widget(xp_info)
        xp_box.add_widget(progress_container)
        xp_box.add_widget(skills_btn)
        
        layout.add_widget(char_box)
        layout.add_widget(xp_box)
        
        self.overall_xp_info = xp_info
        self.progress_bar = progress_bar
        self.char_canvas = char_canvas
        return layout
    
    def create_tasks_section(self):
        """Task list"""
        layout = BoxLayout(orientation='vertical', size_hint=(1, 0.52), spacing=5, padding=5)
        
        header = BoxLayout(size_hint=(1, 0.12), spacing=5)
        
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        day_label = Label(
            text=f"{days[self.current_day]}'S QUESTS",
            font_size='16sp',
            bold=True,
            color=(1, 0.84, 0, 1)
        )
        
        add_btn = Button(
            text="+",
            size_hint=(0.15, 1),
            background_color=(0.3, 0.9, 0.3, 1),
            font_size='24sp',
            on_press=self.show_add_task
        )
        
        header.add_widget(day_label)
        header.add_widget(add_btn)
        
        scroll = ScrollView(size_hint=(1, 0.88))
        self.task_container = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=5)
        self.task_container.bind(minimum_height=self.task_container.setter('height'))
        scroll.add_widget(self.task_container)
        
        layout.add_widget(header)
        layout.add_widget(scroll)
        
        self.day_label = day_label
        self.refresh_tasks()
        return layout
    
    def create_hotbar(self):
        """Day selector + Menu button"""
        layout = GridLayout(cols=8, size_hint=(1, 0.12), spacing=3, padding=5)
        
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        self.day_buttons = []
        
        for i, day in enumerate(days):
            is_today = (i == datetime.now().weekday())
            is_selected = (i == self.current_day)
            
            btn = Button(
                text=day,
                background_color=(0.9, 0.3, 0.3, 1) if is_today else 
                                (0.5, 0.5, 0.9, 1) if is_selected else 
                                (0.3, 0.3, 0.35, 1),
                font_size='12sp',
                bold=is_today
            )
            btn.day_index = i
            btn.bind(on_press=self.switch_day)
            layout.add_widget(btn)
            self.day_buttons.append(btn)
        
        # Menu button
        menu_btn = Button(
            text="MENU",
            background_color=(0.7, 0.5, 0.2, 1),
            font_size='11sp',
            bold=True
        )
        menu_btn.bind(on_press=self.show_menu)
        layout.add_widget(menu_btn)
        
        return layout
    
    def show_menu(self, instance):
        """Show main menu"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(
            text="MENU",
            font_size='20sp',
            bold=True,
            size_hint=(1, 0.12),
            color=(1, 0.84, 0, 1)
        ))
        
        # Theme toggle button
        is_light = self.data_mgr.data.get("light_mode", False)
        theme_btn = Button(
            text=f"Theme: {'Light' if is_light else 'Dark'} (Tap to switch)",
            size_hint=(1, 0.18),
            background_color=(0.9, 0.7, 0.2, 1),
            font_size='13sp'
        )
        theme_btn.bind(on_press=lambda x: self.toggle_theme_from_menu(popup))
        
        # Manage Skills button
        skills_btn = Button(
            text="Manage Skills",
            size_hint=(1, 0.18),
            background_color=(0.3, 0.7, 0.9, 1),
            font_size='14sp'
        )
        skills_btn.bind(on_press=lambda x: self.show_skill_manager(popup))
        
        # Clear Save button
        clear_btn = Button(
            text="Clear Save",
            size_hint=(1, 0.18),
            background_color=(0.8, 0.3, 0.3, 1),
            font_size='14sp'
        )
        clear_btn.bind(on_press=lambda x: self.clear_save_step1_from_menu(popup))
        
        # Close button
        close_btn = Button(
            text="Close",
            size_hint=(1, 0.18),
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='14sp'
        )
        
        content.add_widget(theme_btn)
        content.add_widget(skills_btn)
        content.add_widget(clear_btn)
        content.add_widget(close_btn)
        
        popup = Popup(title="Main Menu", content=content, size_hint=(0.8, 0.6))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def toggle_theme_from_menu(self, parent_popup):
        """Toggle theme and restart"""
        parent_popup.dismiss()
        self.toggle_theme()
    
    def show_skill_manager(self, parent_popup):
        """Manage custom skills"""
        parent_popup.dismiss()
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(
            text="SKILL MANAGER",
            font_size='18sp',
            bold=True,
            size_hint=(1, 0.1)
        ))
        
        # Current skills
        scroll = ScrollView(size_hint=(1, 0.6))
        skills_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        skills_list.bind(minimum_height=skills_list.setter('height'))
        
        all_skills = self.data_mgr.get_all_skills()
        for skill in all_skills:
            skill_data = self.data_mgr.data["skills"].get(skill, {})
            skill_label = Label(
                text=f"{skill} - Level {skill_data.get('level', 1)}",
                size_hint_y=None,
                height=40,
                font_size='13sp'
            )
            skills_list.add_widget(skill_label)
        
        scroll.add_widget(skills_list)
        content.add_widget(scroll)
        
        # Add new skill
        add_box = BoxLayout(size_hint=(1, 0.15), spacing=5)
        skill_input = TextInput(
            hint_text="New skill name",
            multiline=False,
            font_size='13sp'
        )
        add_skill_btn = Button(
            text="Add",
            size_hint=(0.3, 1),
            background_color=(0.3, 0.8, 0.3, 1)
        )
        
        def add_new_skill(x):
            if skill_input.text.strip():
                if self.data_mgr.add_custom_skill(skill_input.text.strip()):
                    popup.dismiss()
                    self.show_popup("Success", f"Added skill: {skill_input.text}")
                else:
                    self.show_popup("Error", "Skill already exists!")
        
        add_skill_btn.bind(on_press=add_new_skill)
        add_box.add_widget(skill_input)
        add_box.add_widget(add_skill_btn)
        content.add_widget(add_box)
        
        # Close
        close_btn = Button(
            text="Close",
            size_hint=(1, 0.15),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        content.add_widget(close_btn)
        
        popup = Popup(title="Manage Skills", content=content, size_hint=(0.85, 0.7))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def clear_save_step1_from_menu(self, parent_popup):
        """Start clear save from menu"""
        parent_popup.dismiss()
        self.clear_save_step1(None)
    
    def clear_save_step1(self, instance):
        """First confirmation"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text="Do you want to clear your save?\n\nThis will delete ALL progress!",
            font_size='14sp'
        ))
        
        btn_box = BoxLayout(size_hint=(1, 0.3), spacing=5)
        
        yes_btn = Button(
            text="Yes",
            background_color=(0.8, 0.3, 0.3, 1),
            on_press=lambda x: self.proceed_to_step2(popup)
        )
        no_btn = Button(
            text="Cancel",
            background_color=(0.3, 0.7, 0.3, 1),
            on_press=lambda x: popup.dismiss()
        )
        
        btn_box.add_widget(yes_btn)
        btn_box.add_widget(no_btn)
        content.add_widget(btn_box)
        
        popup = Popup(title="Clear Save - Step 1 of 3", content=content, size_hint=(0.85, 0.4))
        popup.open()
    
    def proceed_to_step2(self, prev_popup):
        """Second confirmation"""
        prev_popup.dismiss()
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text="Do you REALLY want to clear your save?\n\nLevels: All reset to 1\nXP: All gone\nTasks: All deleted",
            font_size='13sp'
        ))
        
        btn_box = BoxLayout(size_hint=(1, 0.3), spacing=5)
        
        yes_btn = Button(
            text="Yes, I'm sure",
            background_color=(0.9, 0.2, 0.2, 1),
            on_press=lambda x: self.proceed_to_step3(popup)
        )
        no_btn = Button(
            text="Cancel",
            background_color=(0.3, 0.7, 0.3, 1),
            on_press=lambda x: popup.dismiss()
        )
        
        btn_box.add_widget(yes_btn)
        btn_box.add_widget(no_btn)
        content.add_widget(btn_box)
        
        popup = Popup(title="Clear Save - Step 2 of 3", content=content, size_hint=(0.85, 0.45))
        popup.open()
    
    def proceed_to_step3(self, prev_popup):
        """Final confirmation"""
        prev_popup.dismiss()
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text="FINAL WARNING!\n\nDo you REALLY REALLY want to\nclear your save?\n\nTHIS CANNOT BE UNDONE!",
            font_size='13sp',
            color=(1, 0.3, 0.3, 1),
            bold=True
        ))
        
        btn_box = BoxLayout(size_hint=(1, 0.3), spacing=5)
        
        yes_btn = Button(
            text="YES, DELETE EVERYTHING",
            background_color=(1, 0, 0, 1),
            on_press=lambda x: self.do_clear_save(popup)
        )
        no_btn = Button(
            text="Cancel (Keep Save)",
            background_color=(0.3, 0.8, 0.3, 1),
            on_press=lambda x: popup.dismiss()
        )
        
        btn_box.add_widget(yes_btn)
        btn_box.add_widget(no_btn)
        content.add_widget(btn_box)
        
        popup = Popup(title="Clear Save - FINAL STEP 3 of 3", content=content, size_hint=(0.85, 0.5))
        popup.open()
    
    def do_clear_save(self, popup):
        """Actually clear the save"""
        popup.dismiss()
        self.data_mgr.clear_all_data()
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="Save cleared!\n\nRestarting app...", font_size='14sp'))
        
        success_popup = Popup(title="Success", content=content, size_hint=(0.7, 0.3), auto_dismiss=False)
        success_popup.open()
        
        Clock.schedule_once(lambda dt: self.reload_after_clear(success_popup), 2)
    
    def reload_after_clear(self, popup):
        """Reload UI after clearing save - NO RESTART"""
        if popup:
            popup.dismiss()
        
        # Reset day tracking
        self.current_day = datetime.now().weekday()
        
        # Rebuild UI with fresh data
        self.rebuild_ui()
    
    def switch_day(self, button):
        """Switch day"""
        for widget in self.timer_widgets:
            widget.cleanup()
        self.timer_widgets = []
        
        self.current_day = button.day_index
        
        for i, btn in enumerate(self.day_buttons):
            is_today = (i == datetime.now().weekday())
            is_selected = (i == self.current_day)
            btn.background_color = (0.9, 0.3, 0.3, 1) if is_today else \
                                  (0.5, 0.5, 0.9, 1) if is_selected else \
                                  (0.3, 0.3, 0.35, 1)
        
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        self.day_label.text = f"{days[self.current_day]}'S QUESTS"
        self.refresh_tasks()
    
    def refresh_tasks(self):
        """Refresh task list"""
        for widget in self.timer_widgets:
            widget.cleanup()
        self.timer_widgets = []
        
        self.task_container.clear_widgets()
        
        tasks = self.data_mgr.get_tasks_for_day(self.current_day)
        
        if not tasks:
            empty_label = Label(
                text="No quests for this day\nTap + to add one!",
                font_size='14sp',
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=100
            )
            self.task_container.add_widget(empty_label)
        else:
            for task in tasks:
                task_widget = self.create_task_widget(task)
                self.task_container.add_widget(task_widget)
    
    def create_task_widget(self, task):
        """Create task widget"""
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5, padding=5)
        
        # Top: info + buttons
        top_box = BoxLayout(size_hint=(1, None), height=70, spacing=5)
        
        info_box = BoxLayout(orientation='vertical', size_hint=(0.6, 1), spacing=2)
        
        name_label = Label(
            text=task["name"],
            font_size='14sp',
            bold=True,
            size_hint=(1, 0.6),
            halign='left',
            valign='middle',
            color=self.text_color
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        # Show difficulty
        difficulty = task.get("difficulty", "Medium")
        diff_mult = DIFFICULTY_MULTIPLIERS[difficulty]
        skills_text = " | ".join(task["skills"])
        info_text = f"{skills_text}\n{difficulty} (x{diff_mult})"
        
        skills_label = Label(
            text=info_text,
            font_size='10sp',
            size_hint=(1, 0.4),
            color=(0.7, 0.7, 0.8, 1),
            halign='left',
            valign='top'
        )
        skills_label.bind(size=skills_label.setter('text_size'))
        
        info_box.add_widget(name_label)
        info_box.add_widget(skills_label)
        
        # Buttons
        btn_box = BoxLayout(orientation='vertical', size_hint=(0.4, 1), spacing=3)
        
        edit_btn = Button(
            text="Edit",
            background_color=(0.5, 0.7, 0.9, 1),
            font_size='11sp'
        )
        edit_btn.bind(on_press=lambda x: self.show_edit_task(task))
        
        delete_btn = Button(
            text="Remove",
            background_color=(0.8, 0.3, 0.3, 1),
            font_size='11sp'
        )
        delete_btn.bind(on_press=lambda x: self.confirm_delete_task(task))
        
        btn_box.add_widget(edit_btn)
        btn_box.add_widget(delete_btn)
        
        top_box.add_widget(info_box)
        top_box.add_widget(btn_box)
        
        layout.add_widget(top_box)
        
        # Timer if exists
        if task.get("timer") and not task.get("completed"):
            can_start = (self.current_day == datetime.now().weekday())
            if can_start:
                timer_widget = TimerWidget(task, self.complete_task_with_timer)
                self.timer_widgets.append(timer_widget)
                layout.add_widget(timer_widget)
            else:
                timer_info = Label(
                    text=f"Timer: {task['timer']} min (available on task day)",
                    size_hint=(1, None),
                    height=30,
                    font_size='11sp',
                    color=(0.6, 0.6, 0.7, 1)
                )
                layout.add_widget(timer_info)
        
        # Complete button (BIGGER!)
        if not task.get("timer") or task.get("completed"):
            # Check if completed on THIS specific day
            is_completed = (task.get("completed") and 
                          task.get("completed_day") == self.current_day and
                          task.get("completed_date") == datetime.now().strftime("%Y-%m-%d"))
            can_complete = self.current_day == datetime.now().weekday() and not is_completed
            
            complete_btn = Button(
                text="DONE!" if is_completed else "COMPLETE QUEST",
                background_color=(0.2, 0.7, 0.2, 1) if is_completed else (0.3, 0.6, 0.9, 1),
                disabled=not can_complete,
                size_hint=(1, None),
                height=80,  # Even BIGGER! (was 60)
                font_size='16sp',
                bold=True
            )
            complete_btn.bind(on_press=lambda x: self.complete_task_simple(task))
            layout.add_widget(complete_btn)
        
        # Calculate height
        total_height = 70
        if task.get("timer") and not task.get("completed"):
            total_height += 80 if self.current_day == datetime.now().weekday() else 30  # Updated from 60
        if not task.get("timer") or task.get("completed"):
            total_height += 80  # Updated from 60
        total_height += 10
        
        layout.height = total_height
        
        # Background
        with layout.canvas.before:
            if task.get("completed"):
                Color(0.2, 0.4, 0.2, 0.3)
            else:
                Color(*self.card_color)
            RoundedRectangle(pos=layout.pos, size=layout.size, radius=[10])
        layout.bind(pos=self._update_task_bg, size=self._update_task_bg)
        
        return layout
    
    def _update_task_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*self.card_color)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[10])
    
    def complete_task_with_timer(self, task):
        """Complete task with timer"""
        # Only allow completion on current day
        if self.current_day != datetime.now().weekday():
            self.show_popup("Error", "Can only complete tasks on their scheduled day!")
            return
        
        base_xp = 50
        difficulty_mult = DIFFICULTY_MULTIPLIERS.get(task.get("difficulty", "Medium"), 1.5)
        bonus_xp = 0
        
        if task.get("timer_started"):
            elapsed = time.time() - task["timer_started"]
            timer_seconds = task["timer"] * 60
            
            if elapsed <= timer_seconds:
                bonus_xp = int(base_xp * 0.3)
        
        total_xp = int((base_xp + bonus_xp) * difficulty_mult)
        
        for skill in task["skills"]:
            self.data_mgr.add_xp(skill, total_xp)
        
        # Mark complete with specific day
        task["completed"] = True
        task["completed_date"] = datetime.now().strftime("%Y-%m-%d")
        task["completed_day"] = self.current_day  # Track which day it was completed on
        if "timer_started" in task:
            del task["timer_started"]
        
        self.data_mgr.save_data()
        self.refresh_ui()
        
        skills_text = ", ".join(task["skills"])
        difficulty = task.get("difficulty", "Medium")
        
        if bonus_xp > 0:
            msg = f"+{total_xp} XP to:\n{skills_text}\n\n{difficulty}: x{difficulty_mult}\nSPEED BONUS: +{bonus_xp} base XP!"
        else:
            msg = f"+{total_xp} XP to:\n{skills_text}\n\n{difficulty}: x{difficulty_mult}\n(Timer not beaten, but that's OK!)"
        
        self.show_popup("Quest Complete!", msg)
    
    def complete_task_simple(self, task):
        """Complete task without timer"""
        # Only allow completion on current day
        if self.current_day != datetime.now().weekday():
            self.show_popup("Error", "Can only complete tasks on their scheduled day!")
            return
        
        if task.get("completed") and task.get("completed_day") == self.current_day:
            return
        
        base_xp = 50
        difficulty_mult = DIFFICULTY_MULTIPLIERS.get(task.get("difficulty", "Medium"), 1.5)
        total_xp = int(base_xp * difficulty_mult)
        
        for skill in task["skills"]:
            self.data_mgr.add_xp(skill, total_xp)
        
        # Mark complete with specific day
        task["completed"] = True
        task["completed_date"] = datetime.now().strftime("%Y-%m-%d")
        task["completed_day"] = self.current_day
        
        self.data_mgr.save_data()
        self.refresh_ui()
        
        skills_text = ", ".join(task["skills"])
        difficulty = task.get("difficulty", "Medium")
        
        msg = f"+{total_xp} XP to:\n{skills_text}\n\n{difficulty} difficulty: x{difficulty_mult}"
        self.show_popup("Quest Complete!", msg)
    
    def show_edit_task(self, task):
        """Edit existing task"""
        content = BoxLayout(orientation='vertical', spacing=8, padding=10)
        
        name_input = TextInput(
            text=task["name"],
            multiline=False,
            size_hint=(1, 0.1),
            font_size='14sp'
        )
        
        days_label = Label(text="Select Days:", size_hint=(1, 0.08), font_size='13sp')
        
        days_grid = GridLayout(cols=7, size_hint=(1, 0.12), spacing=3)
        day_checkboxes = {}
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        
        for i, day in enumerate(days):
            btn = Button(text=day, background_color=(0.3, 0.3, 0.3, 1), font_size='10sp')
            btn.selected = (i in task.get("days", []))
            btn.day_index = i
            btn.bind(on_press=self.toggle_day_button)
            
            if btn.selected:
                btn.background_color = (0.3, 0.7, 0.3, 1)
            
            days_grid.add_widget(btn)
            day_checkboxes[i] = btn
        
        skills_label = Label(text="Select Skills:", size_hint=(1, 0.08), font_size='13sp')
        
        scroll = ScrollView(size_hint=(1, 0.2))
        skills_grid = GridLayout(cols=1, spacing=3, size_hint_y=None)
        skills_grid.bind(minimum_height=skills_grid.setter('height'))
        
        skill_checkboxes = {}
        all_skills = self.data_mgr.get_all_skills()
        
        for skill in all_skills:
            btn = Button(
                text=f"[ ] {skill}",
                background_color=(0.3, 0.3, 0.3, 1),
                font_size='12sp',
                size_hint_y=None,
                height=35
            )
            btn.skill = skill
            btn.selected = (skill in task.get("skills", []))
            btn.bind(on_press=self.toggle_skill_button)
            
            if btn.selected:
                btn.text = f"[X] {skill}"
                btn.background_color = (0.3, 0.6, 0.9, 1)
            
            skills_grid.add_widget(btn)
            skill_checkboxes[skill] = btn
        
        scroll.add_widget(skills_grid)
        
        # Difficulty selector
        diff_label = Label(text="Difficulty:", size_hint=(1, 0.08), font_size='13sp')
        diff_spinner = Spinner(
            text=task.get("difficulty", "Medium"),
            values=["Easy", "Medium", "Hard", "Extreme"],
            size_hint=(1, 0.1),
            font_size='13sp'
        )
        
        timer_input = TextInput(
            text=str(task.get("timer", "")),
            hint_text="Timer (minutes, optional)",
            multiline=False,
            size_hint=(1, 0.1),
            font_size='14sp',
            input_filter='int'
        )
        
        btn_layout = BoxLayout(size_hint=(1, 0.12), spacing=5)
        
        def save_changes(x):
            selected_days = [i for i, btn in day_checkboxes.items() if btn.selected]
            selected_skills = [s for s, btn in skill_checkboxes.items() if btn.selected]
            
            if not name_input.text:
                self.show_popup("Error", "Please enter a quest name")
                return
            
            if not selected_days:
                self.show_popup("Error", "Please select at least one day")
                return
            
            if not selected_skills:
                self.show_popup("Error", "Please select at least one skill")
                return
            
            timer = None
            if timer_input.text and timer_input.text.isdigit():
                timer = int(timer_input.text)
            
            new_data = {
                "name": name_input.text,
                "skills": selected_skills,
                "days": selected_days,
                "difficulty": diff_spinner.text,
                "timer": timer,
                "completed": task.get("completed", False),
                "completed_date": task.get("completed_date")
            }
            
            self.data_mgr.update_task(task, new_data)
            self.refresh_tasks()
            popup.dismiss()
        
        save_btn = Button(text="Save Changes", background_color=(0.3, 0.8, 0.3, 1), on_press=save_changes)
        cancel_btn = Button(text="Cancel", background_color=(0.5, 0.5, 0.5, 1), on_press=lambda x: popup.dismiss())
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(name_input)
        content.add_widget(days_label)
        content.add_widget(days_grid)
        content.add_widget(skills_label)
        content.add_widget(scroll)
        content.add_widget(diff_label)
        content.add_widget(diff_spinner)
        content.add_widget(timer_input)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Edit Quest", content=content, size_hint=(0.95, 0.9))
        popup.open()
    
    def show_add_task(self, instance):
        """Add new task"""
        content = BoxLayout(orientation='vertical', spacing=8, padding=10)
        
        name_input = TextInput(hint_text="Quest name", multiline=False, size_hint=(1, 0.1), font_size='14sp')
        
        days_label = Label(text="Select Days:", size_hint=(1, 0.08), font_size='13sp')
        
        days_grid = GridLayout(cols=7, size_hint=(1, 0.12), spacing=3)
        day_checkboxes = {}
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        
        for i, day in enumerate(days):
            btn = Button(text=day, background_color=(0.3, 0.3, 0.3, 1), font_size='10sp')
            btn.selected = (i == self.current_day)
            btn.day_index = i
            btn.bind(on_press=self.toggle_day_button)
            
            if btn.selected:
                btn.background_color = (0.3, 0.7, 0.3, 1)
            
            days_grid.add_widget(btn)
            day_checkboxes[i] = btn
        
        skills_label = Label(text="Select Skills:", size_hint=(1, 0.08), font_size='13sp')
        
        scroll = ScrollView(size_hint=(1, 0.2))
        skills_grid = GridLayout(cols=1, spacing=3, size_hint_y=None)
        skills_grid.bind(minimum_height=skills_grid.setter('height'))
        
        skill_checkboxes = {}
        all_skills = self.data_mgr.get_all_skills()
        
        for skill in all_skills:
            btn = Button(
                text=f"[ ] {skill}",
                background_color=(0.3, 0.3, 0.3, 1),
                font_size='12sp',
                size_hint_y=None,
                height=35
            )
            btn.skill = skill
            btn.selected = False
            btn.bind(on_press=self.toggle_skill_button)
            skills_grid.add_widget(btn)
            skill_checkboxes[skill] = btn
        
        scroll.add_widget(skills_grid)
        
        # Difficulty selector
        diff_label = Label(text="Difficulty:", size_hint=(1, 0.08), font_size='13sp')
        diff_spinner = Spinner(
            text="Medium",
            values=["Easy", "Medium", "Hard", "Extreme"],
            size_hint=(1, 0.1),
            font_size='13sp'
        )
        
        timer_input = TextInput(
            hint_text="Timer (minutes, optional)",
            multiline=False,
            size_hint=(1, 0.1),
            font_size='14sp',
            input_filter='int'
        )
        
        btn_layout = BoxLayout(size_hint=(1, 0.12), spacing=5)
        
        def add_task(x):
            selected_days = [i for i, btn in day_checkboxes.items() if btn.selected]
            selected_skills = [s for s, btn in skill_checkboxes.items() if btn.selected]
            
            if not name_input.text:
                self.show_popup("Error", "Please enter a quest name")
                return
            
            if not selected_days:
                self.show_popup("Error", "Please select at least one day")
                return
            
            if not selected_skills:
                self.show_popup("Error", "Please select at least one skill")
                return
            
            timer = None
            if timer_input.text:
                timer = int(timer_input.text)
            
            new_task = {
                "name": name_input.text,
                "skills": selected_skills,
                "days": selected_days,
                "difficulty": diff_spinner.text,
                "timer": timer,
                "completed": False
            }
            
            self.data_mgr.data["tasks"].append(new_task)
            self.data_mgr.save_data()
            self.refresh_tasks()
            popup.dismiss()
        
        add_btn = Button(text="Add Quest", background_color=(0.3, 0.8, 0.3, 1), on_press=add_task)
        cancel_btn = Button(text="Cancel", background_color=(0.5, 0.5, 0.5, 1), on_press=lambda x: popup.dismiss())
        
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(name_input)
        content.add_widget(days_label)
        content.add_widget(days_grid)
        content.add_widget(skills_label)
        content.add_widget(scroll)
        content.add_widget(diff_label)
        content.add_widget(diff_spinner)
        content.add_widget(timer_input)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Create New Quest", content=content, size_hint=(0.95, 0.9))
        popup.open()
    
    def toggle_day_button(self, button):
        button.selected = not button.selected
        button.background_color = (0.3, 0.7, 0.3, 1) if button.selected else (0.3, 0.3, 0.3, 1)
    
    def toggle_skill_button(self, button):
        button.selected = not button.selected
        if button.selected:
            button.text = f"[X] {button.skill}"
            button.background_color = (0.3, 0.6, 0.9, 1)
        else:
            button.text = f"[ ] {button.skill}"
            button.background_color = (0.3, 0.3, 0.3, 1)
    
    def confirm_delete_task(self, task):
        """Confirm delete"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_day_name = days[self.current_day]
        
        num_days = len(task.get("days", []))
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        if num_days > 1:
            msg = f"Remove '{task['name']}' from {current_day_name}?\n\n(Task will still appear on {num_days-1} other day(s))"
        else:
            msg = f"Delete '{task['name']}' completely?\n\n(This is the only day it's scheduled)"
        
        content.add_widget(Label(text=msg, font_size='13sp'))
        
        btn_box = BoxLayout(size_hint=(1, 0.3), spacing=5)
        
        def do_delete(x):
            self.data_mgr.delete_task(task, self.current_day)
            self.refresh_tasks()
            popup.dismiss()
        
        yes_btn = Button(text="Yes", background_color=(0.8, 0.3, 0.3, 1), on_press=do_delete)
        no_btn = Button(text="No", background_color=(0.3, 0.3, 0.3, 1), on_press=lambda x: popup.dismiss())
        
        btn_box.add_widget(yes_btn)
        btn_box.add_widget(no_btn)
        content.add_widget(btn_box)
        
        popup = Popup(title="Confirm Remove", content=content, size_hint=(0.8, 0.4))
        popup.open()
    
    def show_skills(self, instance):
        """Show all skills"""
        content = BoxLayout(orientation='vertical', spacing=8, padding=10)
        
        scroll = ScrollView(size_hint=(1, 0.88))
        skills_box = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        skills_box.bind(minimum_height=skills_box.setter('height'))
        
        for skill_name, skill_data in self.data_mgr.data["skills"].items():
            skill_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=110, spacing=8, padding=[5, 8])
            
            title = Label(
                text=f"{skill_name} - Level {skill_data['level']}",
                font_size='14sp',
                bold=True,
                size_hint=(1, None),
                height=25,
                color=self.text_color
            )
            
            xp_text = f"{skill_data['xp']} / {skill_data['max_xp']} XP"
            xp_label = Label(
                text=xp_text,
                size_hint=(1, None),
                height=20,
                font_size='12sp',
                color=self.text_color
            )
            
            progress_container = BoxLayout(size_hint=(1, None), height=30)
            with progress_container.canvas.before:
                Color(*self.secondary_bg)
                Rectangle(pos=progress_container.pos, size=progress_container.size)
            
            progress = skill_data['xp'] / skill_data['max_xp']
            progress_fill = BoxLayout(size_hint=(progress, 1))
            
            color = (0.3, 0.9, 0.3, 1) if skill_name == "Overall" else (0.3, 0.6, 0.9, 1)
            with progress_fill.canvas.before:
                Color(*color)
                Rectangle(pos=progress_fill.pos, size=progress_fill.size)
            
            progress_container.add_widget(progress_fill)
            
            skill_container.add_widget(title)
            skill_container.add_widget(xp_label)
            skill_container.add_widget(progress_container)
            
            skills_box.add_widget(skill_container)
        
        scroll.add_widget(skills_box)
        content.add_widget(scroll)
        
        close_btn = Button(text="Close", size_hint=(1, 0.12), background_color=(0.5, 0.5, 0.5, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title="All Skills", content=content, size_hint=(0.9, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        msg_label = Label(text=message, font_size='14sp')
        content.add_widget(msg_label)
        
        close_btn = Button(text="OK", size_hint=(1, 0.3), background_color=(0.3, 0.8, 0.3, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.75, 0.45))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def refresh_ui(self):
        lives = self.data_mgr.data['lives']
        max_lives = self.data_mgr.data.get('max_lives', 8)
        hearts = "<3 " * lives
        self.lives_label.text = f"Lives: {hearts}({lives}/{max_lives})"
        
        overall = self.data_mgr.data["skills"]["Overall"]
        self.overall_xp_info.text = f"Level {overall['level']} | {overall['xp']}/{overall['max_xp']} XP"
        self.overall_xp_info.color = self.text_color
        
        self.progress_bar.size_hint = (overall['xp'] / overall['max_xp'], 1)
        
        self.refresh_tasks()

if __name__ == '__main__':
    LevelLifeApp().run()
