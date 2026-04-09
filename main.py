from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
import json
import os
import hashlib
from datetime import datetime, timedelta

# Set window background color
Window.clearcolor = (0.95, 0.95, 0.97, 1)


class SignupScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 20
        
        # Title
        title = Label(
            text='🎮 Welcome to LevelLife!',
            font_size=32,
            bold=True,
            size_hint_y=None,
            height=80
        )
        self.add_widget(title)
        
        subtitle = Label(
            text='Create your account to start your journey',
            font_size=18,
            color=self.hex_to_rgb(self.app.colors['gray']),
            size_hint_y=None,
            height=40
        )
        self.add_widget(subtitle)
        
        # Form
        form = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=300)
        
        # Username
        self.username_input = TextInput(
            hint_text='Username',
            font_size=18,
            multiline=False,
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.username_input)
        
        # Password
        self.password_input = TextInput(
            hint_text='Password',
            font_size=18,
            multiline=False,
            password=True,
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.password_input)
        
        # Confirm Password
        self.confirm_password_input = TextInput(
            hint_text='Confirm Password',
            font_size=18,
            multiline=False,
            password=True,
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.confirm_password_input)
        
        # Bio
        self.bio_input = TextInput(
            hint_text='Bio (optional - tell us about yourself!)',
            font_size=16,
            size_hint_y=None,
            height=100
        )
        form.add_widget(self.bio_input)
        
        self.add_widget(form)
        
        # Error label
        self.error_label = Label(
            text='',
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30,
            font_size=14
        )
        self.add_widget(self.error_label)
        
        # Create Account button
        create_btn = Button(
            text='Create Account & Customize Avatar',
            font_size=18,
            size_hint_y=None,
            height=60,
            background_color=self.app.colors['purple']
        )
        create_btn.bind(on_press=self.create_account)
        self.add_widget(create_btn)
        
        self.add_widget(Widget())  # Spacer
    
    def hex_to_rgb(self, hex_color):
        if isinstance(hex_color, (list, tuple)):
            return hex_color
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def create_account(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text
        confirm = self.confirm_password_input.text
        bio = self.bio_input.text.strip()
        
        # Validation
        if not username:
            self.error_label.text = '❌ Please enter a username'
            return
        
        if len(username) < 3:
            self.error_label.text = '❌ Username must be at least 3 characters'
            return
        
        if not password:
            self.error_label.text = '❌ Please enter a password'
            return
        
        if len(password) < 4:
            self.error_label.text = '❌ Password must be at least 4 characters'
            return
        
        if password != confirm:
            self.error_label.text = '❌ Passwords do not match'
            return
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create profile
        self.app.data = {
            'username': username,
            'password': password_hash,
            'bio': bio,
            'level': 1,
            'xp': 0,
            'hearts': 8,
            'coins': 100,  # Starting bonus!
            'tasks': [],
            'skills': ['Work', 'Personal', 'Health', 'Learning'],
            'avatar': {
                'body': 'body_medium',
                'hair': 'short_brown',
                'eyes': 'blue',
                'mouth': 'smile',
                'accessories': []
            },
            'inventory': {
                'unlocked_hair': ['short_brown', 'short_black', 'short_blonde'],
                'unlocked_eyes': ['blue', 'brown'],
                'unlocked_mouth': ['smile', 'neutral'],
                'unlocked_accessories': []
            },
            'created_at': datetime.now().isoformat()
        }
        
        self.app.save_data()
        
        # Go to avatar customization
        self.app.screen_manager.current = 'welcome_customization'


class LoginScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 20
        
        self.add_widget(Widget())  # Spacer
        
        # Title
        title = Label(
            text='🎮 Welcome Back!',
            font_size=32,
            bold=True,
            size_hint_y=None,
            height=80
        )
        self.add_widget(title)
        
        # Form
        form = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=150)
        
        # Username
        self.username_input = TextInput(
            hint_text='Username',
            font_size=18,
            multiline=False,
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.username_input)
        
        # Password
        self.password_input = TextInput(
            hint_text='Password',
            font_size=18,
            multiline=False,
            password=True,
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.password_input)
        
        self.add_widget(form)
        
        # Error label
        self.error_label = Label(
            text='',
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30,
            font_size=14
        )
        self.add_widget(self.error_label)
        
        # Login button
        login_btn = Button(
            text='Login',
            font_size=18,
            size_hint_y=None,
            height=60,
            background_color=self.app.colors['purple']
        )
        login_btn.bind(on_press=self.login)
        self.add_widget(login_btn)
        
        # Create account link
        create_box = BoxLayout(size_hint_y=None, height=40)
        create_box.add_widget(Label(text="Don't have an account?", font_size=14))
        create_btn = Button(
            text='Sign Up',
            font_size=14,
            size_hint=(None, None),
            size=(100, 40),
            background_color=self.app.colors['green']
        )
        create_btn.bind(on_press=lambda x: setattr(self.app.screen_manager, 'current', 'signup'))
        create_box.add_widget(create_btn)
        self.add_widget(create_box)
        
        self.add_widget(Widget())  # Spacer
    
    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text
        
        if not username or not password:
            self.error_label.text = '❌ Please enter username and password'
            return
        
        # Check if username matches
        if username != self.app.data.get('username', ''):
            self.error_label.text = '❌ Invalid username or password'
            return
        
        # Check password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != self.app.data.get('password', ''):
            self.error_label.text = '❌ Invalid username or password'
            return
        
        # Login successful
        self.app.logged_in = True
        self.app.screen_manager.current = 'main'


class WelcomeCustomizationScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Welcome message
        welcome = Label(
            text=f"Welcome, {self.app.data.get('username', 'Player')}! 🎉",
            font_size=26,
            bold=True,
            size_hint_y=None,
            height=60
        )
        self.add_widget(welcome)
        
        instruction = Label(
            text="You've received 100 bonus coins!\nCustomize your avatar to get started!",
            font_size=18,
            color=self.hex_to_rgb(self.app.colors['gray']),
            size_hint_y=None,
            height=60
        )
        self.add_widget(instruction)
        
        # Avatar preview
        self.avatar_preview = BoxLayout(size_hint=(1, None), height=180, padding=20)
        preview_widget = Widget()
        with preview_widget.canvas:
            Color(*self.hex_to_rgb(self.app.colors['light_gray']))
            Rectangle(pos=preview_widget.pos, size=preview_widget.size)
        self.avatar_preview.add_widget(preview_widget)
        self.add_widget(self.avatar_preview)
        
        # Category tabs
        tabs = BoxLayout(size_hint_y=None, height=50, spacing=5)
        categories = ['Hair', 'Eyes', 'Mouth']
        for cat in categories:
            btn = Button(
                text=cat,
                background_color=self.app.colors['purple']
            )
            btn.bind(on_press=lambda x, c=cat: self.show_category(c))
            tabs.add_widget(btn)
        self.add_widget(tabs)
        
        # Options scroll
        self.options_scroll = ScrollView(size_hint=(1, 1))
        self.options_grid = GridLayout(cols=3, spacing=10, size_hint_y=None, padding=10)
        self.options_grid.bind(minimum_height=self.options_grid.setter('height'))
        self.options_scroll.add_widget(self.options_grid)
        self.add_widget(self.options_scroll)
        
        # Continue button
        continue_btn = Button(
            text='Start My Journey! →',
            font_size=18,
            size_hint_y=None,
            height=60,
            background_color=self.app.colors['green']
        )
        continue_btn.bind(on_press=self.finish_setup)
        self.add_widget(continue_btn)
        
        # Show hair by default
        self.show_category('Hair')
    
    def hex_to_rgb(self, hex_color):
        if isinstance(hex_color, (list, tuple)):
            return hex_color
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def show_category(self, category):
        self.options_grid.clear_widgets()
        
        # Available options (all unlocked for new users!)
        if category == 'Hair':
            options = ['short_brown', 'short_black', 'short_blonde']
            unlocked = self.app.data['inventory']['unlocked_hair']
            current = self.app.data['avatar']['hair']
        elif category == 'Eyes':
            options = ['blue', 'brown']
            unlocked = self.app.data['inventory']['unlocked_eyes']
            current = self.app.data['avatar']['eyes']
        else:  # Mouth
            options = ['smile', 'neutral']
            unlocked = self.app.data['inventory']['unlocked_mouth']
            current = self.app.data['avatar']['mouth']
        
        for option in options:
            btn_box = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=5, spacing=5)
            
            is_selected = option == current
            
            btn = Button(
                text=option.replace('_', ' ').title(),
                size_hint=(1, None),
                height=80,
                background_color=self.app.colors['green'] if is_selected else self.app.colors['purple']
            )
            btn.bind(on_press=lambda x, opt=option, cat=category.lower(): self.select_option(opt, cat))
            
            btn_box.add_widget(btn)
            
            if is_selected:
                btn_box.add_widget(Label(text='✓ Selected', size_hint=(1, None), height=30, font_size=14))
            else:
                btn_box.add_widget(Widget(size_hint=(1, None), height=30))
            
            self.options_grid.add_widget(btn_box)
    
    def select_option(self, option, category):
        if category == 'hair':
            self.app.data['avatar']['hair'] = option
        elif category == 'eyes':
            self.app.data['avatar']['eyes'] = option
        elif category == 'mouth':
            self.app.data['avatar']['mouth'] = option
        
        self.app.save_data()
        self.show_category(category.capitalize())
    
    def finish_setup(self, instance):
        self.app.logged_in = True
        self.app.screen_manager.current = 'main'


class TaskItem(BoxLayout):
    def __init__(self, task, app, **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.app = app
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 80
        self.padding = 10
        self.spacing = 10

        # Background
        with self.canvas.before:
            self.bg_color = Color(*self.hex_to_rgb(self.app.colors['white']))
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Left section - Task info
        left_box = BoxLayout(orientation='vertical', size_hint_x=0.6)
        
        title_label = Label(
            text=task['title'],
            font_size=18,
            bold=True,
            halign='left',
            valign='middle',
            color=self.hex_to_rgb(self.app.colors['dark_text'])
        )
        title_label.bind(size=title_label.setter('text_size'))
        left_box.add_widget(title_label)

        info_box = BoxLayout(size_hint_y=0.4)
        difficulty_colors = {'Easy': self.app.colors['green'], 'Medium': self.app.colors['yellow'], 'Hard': self.app.colors['red']}
        difficulty_label = Label(
            text=f"{task['difficulty']} • {task['skill']}",
            font_size=14,
            color=self.hex_to_rgb(difficulty_colors.get(task['difficulty'], self.app.colors['gray'])),
            halign='left',
            valign='middle'
        )
        difficulty_label.bind(size=difficulty_label.setter('text_size'))
        info_box.add_widget(difficulty_label)
        left_box.add_widget(info_box)

        self.add_widget(left_box)

        # Right section - XP and Complete button
        right_box = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=5)
        
        xp_label = Label(
            text=f"+{task['xp']} XP",
            font_size=16,
            bold=True,
            color=self.hex_to_rgb(self.app.colors['purple'])
        )
        right_box.add_widget(xp_label)

        if task['completed']:
            complete_btn = Button(
                text='✓ Done',
                background_color=self.app.colors['green'],
                disabled=True
            )
        else:
            complete_btn = Button(
                text='Complete',
                background_color=self.app.colors['purple']
            )
            complete_btn.bind(on_press=self.complete_task)
        
        right_box.add_widget(complete_btn)
        self.add_widget(right_box)

    def hex_to_rgb(self, hex_color):
        if isinstance(hex_color, (list, tuple)):
            return hex_color
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def complete_task(self, instance):
        self.app.complete_task(self.task)


class ProfileScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        back_btn = Button(
            text='← Back',
            size_hint=(None, None),
            size=(100, 50),
            background_color=self.app.colors['purple']
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label(text='Profile', font_size=28, bold=True))
        
        # Logout button
        logout_btn = Button(
            text='Logout',
            size_hint=(None, None),
            size=(100, 50),
            background_color=self.app.colors['red']
        )
        logout_btn.bind(on_press=self.logout)
        header.add_widget(logout_btn)
        
        self.add_widget(header)
        
        # Avatar display
        avatar_container = BoxLayout(size_hint_y=None, height=250, padding=10)
        avatar_box = BoxLayout(orientation='vertical', size_hint=(None, 1), width=200, pos_hint={'center_x': 0.5})
        
        # Avatar preview
        self.avatar_widget = Widget(size_hint=(1, None), height=180)
        with self.avatar_widget.canvas:
            Color(*self.hex_to_rgb(self.app.colors['light_gray']))
            Rectangle(pos=self.avatar_widget.pos, size=self.avatar_widget.size)
        avatar_box.add_widget(self.avatar_widget)
        
        # Customize button
        customize_btn = Button(
            text='Customize',
            size_hint=(1, None),
            height=50,
            background_color=self.app.colors['purple']
        )
        customize_btn.bind(on_press=self.open_customization)
        avatar_box.add_widget(customize_btn)
        
        avatar_container.add_widget(Widget())
        avatar_container.add_widget(avatar_box)
        avatar_container.add_widget(Widget())
        self.add_widget(avatar_container)
        
        # Username and bio
        info_box = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=10)
        
        username_label = Label(
            text=f"@{self.app.data.get('username', 'Player')}",
            font_size=24,
            bold=True,
            size_hint=(1, None),
            height=40
        )
        info_box.add_widget(username_label)
        
        self.bio_input = TextInput(
            text=self.app.data.get('bio', ''),
            font_size=16,
            size_hint=(1, None),
            height=70,
            hint_text='Bio (tell us about yourself!)',
            background_color=(*self.hex_to_rgb(self.app.colors['light_gray']), 1)
        )
        self.bio_input.bind(text=self.save_bio)
        info_box.add_widget(self.bio_input)
        
        self.add_widget(info_box)
        
        # Stats
        stats_label = Label(text='Stats', font_size=22, bold=True, size_hint_y=None, height=40)
        self.add_widget(stats_label)
        
        stats_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=200, padding=10)
        
        # Calculate stats
        total_xp = self.app.data.get('xp', 0)
        tasks = self.app.data.get('tasks', [])
        tasks_completed = len([t for t in tasks if t.get('completed', False)])
        coins = self.app.data.get('coins', 0)
        
        stats = [
            ('Level', str(self.app.data.get('level', 1))),
            ('Total XP', str(total_xp)),
            ('Coins', str(coins)),
            ('Tasks Done', str(tasks_completed)),
            ('Current Hearts', f"{self.app.data.get('hearts', 8)}/8"),
            ('Skills', str(len(self.app.data.get('skills', []))))
        ]
        
        for stat_name, stat_value in stats:
            stat_box = BoxLayout(orientation='vertical', padding=10)
            with stat_box.canvas.before:
                Color(*self.hex_to_rgb(self.app.colors['light_gray']))
                stat_box.rect = Rectangle(pos=stat_box.pos, size=stat_box.size)
            stat_box.bind(pos=self.update_rect, size=self.update_rect)
            
            stat_box.add_widget(Label(text=stat_name, font_size=14, color=self.hex_to_rgb(self.app.colors['gray'])))
            stat_box.add_widget(Label(text=stat_value, font_size=24, bold=True))
            stats_grid.add_widget(stat_box)
        
        self.add_widget(stats_grid)
        
        self.add_widget(Widget())  # Spacer
    
    def hex_to_rgb(self, hex_color):
        if isinstance(hex_color, (list, tuple)):
            return hex_color
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def save_bio(self, instance, value):
        self.app.data['bio'] = value
        self.app.save_data()
    
    def open_customization(self, instance):
        self.app.screen_manager.current = 'customization'
    
    def logout(self, instance):
        # Show confirmation popup
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text='Are you sure you want to logout?', font_size=18))
        
        buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        cancel_btn = Button(
            text='Cancel',
            background_color=self.app.colors['gray']
        )
        
        logout_btn = Button(
            text='Logout',
            background_color=self.app.colors['red']
        )
        
        popup = Popup(
            title='Logout',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        logout_btn.bind(on_press=lambda x: self.confirm_logout(popup))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(logout_btn)
        content.add_widget(buttons)
        
        popup.open()
    
    def confirm_logout(self, popup):
        popup.dismiss()
        self.app.logged_in = False
        self.app.screen_manager.current = 'login'
    
    def go_back(self, instance):
        self.app.screen_manager.current = 'main'


class AvatarCustomizationScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60, spacing=10)
        back_btn = Button(
            text='← Back',
            size_hint=(None, None),
            size=(100, 50),
            background_color=self.app.colors['purple']
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label(text='Customize Avatar', font_size=24, bold=True))
        
        # Coins display
        self.coins_label = Label(
            text=f"💰 {self.app.data.get('coins', 0)}",
            font_size=20,
            bold=True,
            size_hint=(None, None),
            size=(150, 50)
        )
        header.add_widget(self.coins_label)
        self.add_widget(header)
        
        # Avatar preview
        self.avatar_preview = BoxLayout(size_hint=(1, None), height=200, padding=20)
        preview_widget = Widget()
        with preview_widget.canvas:
            Color(*self.hex_to_rgb(self.app.colors['light_gray']))
            Rectangle(pos=preview_widget.pos, size=preview_widget.size)
        self.avatar_preview.add_widget(preview_widget)
        self.add_widget(self.avatar_preview)
        
        # Category tabs
        tabs = BoxLayout(size_hint_y=None, height=50, spacing=5)
        categories = ['Hair', 'Eyes', 'Mouth', 'Accessories']
        for cat in categories:
            btn = Button(
                text=cat,
                background_color=self.app.colors['purple']
            )
            btn.bind(on_press=lambda x, c=cat: self.show_category(c))
            tabs.add_widget(btn)
        self.add_widget(tabs)
        
        # Options scroll
        self.options_scroll = ScrollView(size_hint=(1, 1))
        self.options_grid = GridLayout(cols=3, spacing=10, size_hint_y=None, padding=10)
        self.options_grid.bind(minimum_height=self.options_grid.setter('height'))
        self.options_scroll.add_widget(self.options_grid)
        self.add_widget(self.options_scroll)
        
        # Show hair by default
        self.show_category('Hair')
    
    def hex_to_rgb(self, hex_color):
        if isinstance(hex_color, (list, tuple)):
            return hex_color
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def show_category(self, category):
        self.options_grid.clear_widgets()
        
        # Available options
        if category == 'Hair':
            options = [
                ('short_brown', 30), ('short_black', 30), ('short_blonde', 30),
                ('long_brown', 50), ('long_black', 50), ('long_blonde', 50),
                ('curly_brown', 70), ('curly_black', 70)
            ]
            unlocked = self.app.data['inventory']['unlocked_hair']
            current = self.app.data['avatar']['hair']
        elif category == 'Eyes':
            options = [
                ('blue', 20), ('brown', 20), ('green', 30),
                ('gray', 30), ('purple', 50), ('amber', 50)
            ]
            unlocked = self.app.data['inventory']['unlocked_eyes']
            current = self.app.data['avatar']['eyes']
        elif category == 'Mouth':
            options = [
                ('smile', 0), ('neutral', 20), ('serious', 20),
                ('laugh', 40), ('smirk', 40)
            ]
            unlocked = self.app.data['inventory']['unlocked_mouth']
            current = self.app.data['avatar']['mouth']
        else:  # Accessories
            options = [
                ('glasses_round', 100), ('glasses_square', 100),
                ('hat_cap', 80), ('hat_beanie', 80),
                ('earrings', 60), ('necklace', 70)
            ]
            unlocked = self.app.data['inventory'].get('unlocked_accessories', [])
            current = None
        
        for option, price in options:
            btn_box = BoxLayout(orientation='vertical', size_hint_y=None, height=140, padding=5, spacing=5)
            
            is_unlocked = option in unlocked
            is_selected = option == current or (category == 'Accessories' and option in self.app.data['avatar']['accessories'])
            
            btn = Button(
                text=option.replace('_', ' ').title(),
                size_hint=(1, None),
                height=80,
                background_color=self.app.colors['green'] if is_selected else (self.app.colors['purple'] if is_unlocked else self.app.colors['gray'])
            )
            
            if is_unlocked:
                btn.bind(on_press=lambda x, opt=option, cat=category.lower(): self.select_option(opt, cat))
            else:
                btn.text = f"🔒 {btn.text}"
                btn.bind(on_press=lambda x, opt=option, cat=category.lower(), p=price: self.buy_option(opt, cat, p))
            
            btn_box.add_widget(btn)
            
            # Price/Status label
            if not is_unlocked:
                price_btn = Button(
                    text=f'Buy: {price} coins',
                    size_hint=(1, None),
                    height=40,
                    font_size=14,
                    background_color=self.app.colors['yellow']
                )
                price_btn.bind(on_press=lambda x, opt=option, cat=category.lower(), p=price: self.buy_option(opt, cat, p))
                btn_box.add_widget(price_btn)
            elif is_selected:
                btn_box.add_widget(Label(text='✓ Equipped', size_hint=(1, None), height=40, font_size=14, color=self.hex_to_rgb(self.app.colors['green'])))
            else:
                btn_box.add_widget(Widget(size_hint=(1, None), height=40))
            
            self.options_grid.add_widget(btn_box)
    
    def select_option(self, option, category):
        if category == 'hair':
            self.app.data['avatar']['hair'] = option
        elif category == 'eyes':
            self.app.data['avatar']['eyes'] = option
        elif category == 'mouth':
            self.app.data['avatar']['mouth'] = option
        elif category == 'accessories':
            if option in self.app.data['avatar']['accessories']:
                self.app.data['avatar']['accessories'].remove(option)
            else:
                self.app.data['avatar']['accessories'].append(option)
        
        self.app.save_data()
        self.show_category(category.capitalize())
    
    def buy_option(self, option, category, price):
        coins = self.app.data.get('coins', 0)
        
        if coins >= price:
            self.app.data['coins'] = coins - price
            
            if category == 'hair':
                self.app.data['inventory']['unlocked_hair'].append(option)
            elif category == 'eyes':
                self.app.data['inventory']['unlocked_eyes'].append(option)
            elif category == 'mouth':
                self.app.data['inventory']['unlocked_mouth'].append(option)
            elif category == 'accessories':
                self.app.data['inventory']['unlocked_accessories'].append(option)
            
            self.app.save_data()
            
            self.show_popup('Purchase Successful!', f'You bought {option.replace("_", " ").title()} for {price} coins!')
            self.show_category(category.capitalize())
            self.coins_label.text = f"💰 {self.app.data.get('coins', 0)}"
        else:
            self.show_popup('Not Enough Coins!', f'You need {price} coins but only have {coins} coins.\n\nComplete more tasks to earn coins!')
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=message, font_size=16))
        
        close_btn = Button(
            text='OK',
            size_hint=(1, None),
            height=50,
            background_color=self.app.colors['purple']
        )
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def go_back(self, instance):
        self.app.screen_manager.current = 'profile'


class LevelLifeApp(App):
    def build(self):
        self.data_file = 'levellife_data.json'
        self.logged_in = False
        
        # Color scheme
        self.colors = {
            'purple': [0.6, 0.4, 0.8, 1],
            'dark_purple': [0.5, 0.3, 0.7, 1],
            'light_purple': [0.7, 0.5, 0.9, 1],
            'white': [1, 1, 1, 1],
            'light_gray': [0.95, 0.95, 0.97, 1],
            'gray': [0.5, 0.5, 0.5, 1],
            'dark_text': [0.2, 0.2, 0.2, 1],
            'green': [0.3, 0.8, 0.4, 1],
            'yellow': [1, 0.8, 0.2, 1],
            'red': [0.9, 0.3, 0.3, 1]
        }
        
        self.load_data()
        
        # Screen Manager
        self.screen_manager = ScreenManager()
        
        # Signup Screen
        signup_screen = Screen(name='signup')
        signup_screen.add_widget(SignupScreen(self))
        self.screen_manager.add_widget(signup_screen)
        
        # Login Screen
        login_screen = Screen(name='login')
        login_screen.add_widget(LoginScreen(self))
        self.screen_manager.add_widget(login_screen)
        
        # Welcome Customization Screen
        welcome_customization_screen = Screen(name='welcome_customization')
        welcome_customization_screen.add_widget(WelcomeCustomizationScreen(self))
        self.screen_manager.add_widget(welcome_customization_screen)
        
        # Main Screen
        main_screen = Screen(name='main')
        main_screen.add_widget(self.create_main_screen())
        self.screen_manager.add_widget(main_screen)
        
        # Profile Screen
        profile_screen = Screen(name='profile')
        self.profile_widget = ProfileScreen(self)
        profile_screen.add_widget(self.profile_widget)
        self.screen_manager.add_widget(profile_screen)
        
        # Customization Screen
        customization_screen = Screen(name='customization')
        self.customization_widget = AvatarCustomizationScreen(self)
        customization_screen.add_widget(self.customization_widget)
        self.screen_manager.add_widget(customization_screen)
        
        # Check if user exists
        if 'username' in self.data and 'password' in self.data:
            self.screen_manager.current = 'login'
        else:
            self.screen_manager.current = 'signup'
        
        return self.screen_manager

    def create_main_screen(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Top bar - Hearts, Level, XP, Profile
        top_bar = BoxLayout(size_hint_y=None, height=80, spacing=10)
        
        # Hearts
        hearts_box = BoxLayout(size_hint_x=0.3)
        hearts = self.data.get('hearts', 8)
        hearts_text = '❤️ ' * hearts + '🖤 ' * (8 - hearts)
        hearts_label = Label(text=hearts_text, font_size=16)
        hearts_box.add_widget(hearts_label)
        top_bar.add_widget(hearts_box)
        
        # Level and XP
        level_box = BoxLayout(orientation='vertical', size_hint_x=0.5)
        level = self.data.get('level', 1)
        xp = self.data.get('xp', 0)
        level_label = Label(text=f'Level {level}', font_size=22, bold=True)
        xp_label = Label(text=f'XP: {xp}/{level * 100}', font_size=16)
        level_box.add_widget(level_label)
        level_box.add_widget(xp_label)
        top_bar.add_widget(level_box)
        
        # Profile button
        profile_btn = Button(
            text='👤',
            size_hint=(None, None),
            size=(60, 60),
            background_color=self.colors['purple'],
            font_size=24
        )
        profile_btn.bind(on_press=lambda x: setattr(self.screen_manager, 'current', 'profile'))
        top_bar.add_widget(profile_btn)
        
        layout.add_widget(top_bar)
        
        # Tasks title and add button
        title_box = BoxLayout(size_hint_y=None, height=60, spacing=10)
        title_label = Label(text='Tasks', font_size=28, bold=True, size_hint_x=0.7, halign='left')
        title_label.bind(size=title_label.setter('text_size'))
        title_box.add_widget(title_label)
        
        add_task_btn = Button(
            text='+ Add Task',
            size_hint_x=0.3,
            background_color=self.colors['purple']
        )
        add_task_btn.bind(on_press=self.show_add_task_popup)
        title_box.add_widget(add_task_btn)
        layout.add_widget(title_box)
        
        # Tasks list
        self.tasks_scroll = ScrollView()
        self.tasks_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=[0, 0, 0, 10])
        self.tasks_layout.bind(minimum_height=self.tasks_layout.setter('height'))
        
        self.update_tasks_list()
        
        self.tasks_scroll.add_widget(self.tasks_layout)
        layout.add_widget(self.tasks_scroll)
        
        return layout

    def update_tasks_list(self):
        self.tasks_layout.clear_widgets()
        
        tasks = self.data.get('tasks', [])
        incomplete_tasks = [t for t in tasks if not t.get('completed', False)]
        
        if not incomplete_tasks:
            no_tasks_label = Label(
                text='No tasks yet! Add one to get started 🎯',
                font_size=18,
                color=self.hex_to_rgb(self.colors['gray'])
            )
            self.tasks_layout.add_widget(no_tasks_label)
        else:
            for task in incomplete_tasks:
                task_item = TaskItem(task, self)
                self.tasks_layout.add_widget(task_item)

    def show_add_task_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        title_input = TextInput(hint_text='Task name', multiline=False, size_hint_y=None, height=40)
        content.add_widget(title_input)
        
        difficulty_label = Label(text='Difficulty:', size_hint_y=None, height=30, halign='left')
        difficulty_label.bind(size=difficulty_label.setter('text_size'))
        content.add_widget(difficulty_label)
        
        difficulty_spinner = Spinner(
            text='Medium',
            values=('Easy', 'Medium', 'Hard'),
            size_hint_y=None,
            height=40
        )
        content.add_widget(difficulty_spinner)
        
        skill_label = Label(text='Skill:', size_hint_y=None, height=30, halign='left')
        skill_label.bind(size=skill_label.setter('text_size'))
        content.add_widget(skill_label)
        
        skills = self.data.get('skills', ['General'])
        skill_spinner = Spinner(
            text=skills[0] if skills else 'General',
            values=tuple(skills) if skills else ('General',),
            size_hint_y=None,
            height=40
        )
        content.add_widget(skill_spinner)
        
        button_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        cancel_btn = Button(text='Cancel', background_color=self.colors['gray'])
        add_btn = Button(text='Add Task', background_color=self.colors['purple'])
        
        button_box.add_widget(cancel_btn)
        button_box.add_widget(add_btn)
        content.add_widget(button_box)
        
        popup = Popup(title='Add New Task', content=content, size_hint=(0.9, 0.7))
        
        def add_task(instance):
            if title_input.text.strip():
                difficulty = difficulty_spinner.text
                xp_values = {'Easy': 10, 'Medium': 20, 'Hard': 30}
                
                new_task = {
                    'title': title_input.text.strip(),
                    'difficulty': difficulty,
                    'skill': skill_spinner.text,
                    'xp': xp_values[difficulty],
                    'completed': False,
                    'created_at': datetime.now().isoformat()
                }
                
                if 'tasks' not in self.data:
                    self.data['tasks'] = []
                self.data['tasks'].append(new_task)
                self.save_data()
                self.update_tasks_list()
                popup.dismiss()
        
        cancel_btn.bind(on_press=popup.dismiss)
        add_btn.bind(on_press=add_task)
        
        popup.open()

    def complete_task(self, task):
        task['completed'] = True
        task['completed_at'] = datetime.now().isoformat()
        
        self.data['xp'] = self.data.get('xp', 0) + task['xp']
        
        coins_earned = task['xp'] // 10
        self.data['coins'] = self.data.get('coins', 0) + coins_earned
        
        xp_needed = self.data.get('level', 1) * 100
        if self.data.get('xp', 0) >= xp_needed:
            self.data['level'] = self.data.get('level', 1) + 1
            self.data['xp'] -= xp_needed
            self.show_level_up_popup()
        
        self.save_data()
        self.update_tasks_list()
        self.update_top_bar()
        
        self.show_task_complete_popup(task, coins_earned)

    def show_task_complete_popup(self, task, coins_earned):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        congrats = Label(text='🎉 Task Complete!', font_size=24, bold=True)
        content.add_widget(congrats)
        
        rewards = Label(text=f'+ {task["xp"]} XP\n+ {coins_earned} Coins', font_size=20)
        content.add_widget(rewards)
        
        close_btn = Button(
            text='Awesome!',
            size_hint=(1, None),
            height=50,
            background_color=self.colors['purple']
        )
        
        popup = Popup(
            title='Success',
            content=content,
            size_hint=(0.8, 0.5)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def show_level_up_popup(self):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        congrats = Label(text=f'🎊 Level Up!\n\nYou are now Level {self.data.get("level", 1)}', font_size=24, bold=True)
        content.add_widget(congrats)
        
        close_btn = Button(
            text='Continue',
            size_hint=(1, None),
            height=50,
            background_color=self.colors['purple']
        )
        
        popup = Popup(
            title='Level Up!',
            content=content,
            size_hint=(0.8, 0.5)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def update_top_bar(self):
        main_screen = self.screen_manager.get_screen('main')
        main_screen.clear_widgets()
        main_screen.add_widget(self.create_main_screen())

    def hex_to_rgb(self, hex_color):
        if isinstance(hex_color, (list, tuple)):
            return hex_color
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)


if __name__ == '__main__':
    LevelLifeApp().run()
