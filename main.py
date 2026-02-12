import pygame
import pandas as pd
import random
import math
import sys
import os

pygame.init()

pygame.mixer.init()

print("Đang sử dụng font:", pygame.font.get_default_font())

WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))

DATA_TABLE_BG = (40, 45, 60)
TEXT_COLOR = (255, 255, 255)
UI_BG = (30, 35, 45)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)
BUTTON_TEXT_COLOR = (255, 255, 255)

FONT_FILE = "SVN-Coder's Crux.ttf"

BUTTON_WIDTH = 320
BUTTON_HEIGHT = 90
BUTTON_SPACING = 110

def get_font(size, bold=False):
    font = pygame.font.Font(FONT_FILE, size)
    if bold:
        font.set_bold(True)
    return font

font_xlarge = get_font(48, bold=True)
font_large = get_font(36, bold=True)
font_medium = get_font(28)
font_small = get_font(24)
font_tiny = get_font(20)

def load_image(filename, size=None):
    image = pygame.image.load(filename)
    if size:
        image = pygame.transform.scale(image, size)
    return image.convert_alpha()

def load_and_resize_image(filename, target_width=BUTTON_WIDTH, target_height=BUTTON_HEIGHT):
    image = pygame.image.load(filename)
    
    original_width, original_height = image.get_size()
    
    width_ratio = target_width / original_width
    height_ratio = target_height / original_height
    
    scale_ratio = min(width_ratio, height_ratio)
    
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)
    
    image = pygame.transform.scale(image, (new_width, new_height))
    print(f"Đã load và resize ảnh: {filename} từ {original_width}x{original_height} thành {new_width}x{new_height}")
    return image.convert_alpha()

intro_image = load_image('intro.png', (WIDTH, HEIGHT))
story_image = load_image('story.png', (WIDTH, HEIGHT))

instructions_image = load_image('instructions.png', (WIDTH - 100, HEIGHT - 150))

bubble_images = {
    'correct': load_image('bubble_correct.png', (70, 70)),
    'wrong': load_image('bubble_wrong.png', (70, 70)),
}

bullet_image = load_image('bullet.png', (30, 30))
cannon_base_image = load_image('cannon_base.png', (280, 300))

background_images = {}
for level in range(1, 5):
    bg_file = f'background_level{level}.png'
    bg_image = load_image(bg_file, (WIDTH-10, HEIGHT-10))
    background_images[level] = bg_image
    print(f"Đã load hình nền cho level {level}: {bg_file}")

menu_background = load_image('background_menu.png', (WIDTH, HEIGHT))

game_complete_background = load_image('background_complete.png', (WIDTH, HEIGHT))
congrats_background = load_image('congratulations_background.png', (WIDTH, HEIGHT))
reward_background = load_image('reward_background.png', (WIDTH, HEIGHT))

logo_image = load_image('logo.png', (30, 30))
powerup_good_image = load_image('powerup_good.png', (50, 50))
powerup_bad_image = load_image('powerup_bad.png', (50, 50))
rock_image = load_image('rock.png', (80, 80))
sound_on_image = load_image('sound_on.png', (40, 40))
sound_off_image = load_image('sound_off.png', (40, 40))
menu_logo_image = load_image('logo_nullout.png', (400, 400))

start_button_image = load_and_resize_image('start_button.png', BUTTON_WIDTH, BUTTON_HEIGHT)
continue_button_image = load_and_resize_image('continue_button.png', BUTTON_WIDTH, BUTTON_HEIGHT)
back_button_image = load_and_resize_image('back_button.png', BUTTON_WIDTH, BUTTON_HEIGHT)
reward_button_image = load_and_resize_image('reward_button.png', BUTTON_WIDTH, BUTTON_HEIGHT)

STATE_INTRO = "INTRO"
STATE_STORY = "STORY"
STATE_MENU = "MENU"
STATE_LEVEL_START = "LEVEL_START"
STATE_PLAYING = "PLAYING"
STATE_LEVEL_COMPLETE = "LEVEL_COMPLETE"
STATE_GAME_OVER = "GAME_OVER"
STATE_GAME_WIN = "GAME_WIN"
STATE_GAME_COMPLETE = "GAME_COMPLETE"
STATE_INSTRUCTIONS = "INSTRUCTIONS"
STATE_REWARD = "REWARD"

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.sound_enabled = True
        
    def load_sound(self, name, filename):
        self.sounds[name] = pygame.mixer.Sound(filename)
        print(f"Đã load âm thanh: {name}")
            
    def play_sound(self, name, volume=0.5):
        if not self.sound_enabled:
            return
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
            self.sounds[name].play()
            
    def play_music(self, filename, volume=0.3, loops=-1):
        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(volume)
        if self.sound_enabled:
            pygame.mixer.music.play(loops)
        self.music_playing = True
        print(f"Đang phát nhạc nền: {filename}")
            
    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False
        
    def pause_music(self):
        pygame.mixer.music.pause()
        
    def unpause_music(self):
        pygame.mixer.music.unpause()
        
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            if self.music_playing:
                self.unpause_music()
            print("Âm thanh: BẬT")
        else:
            self.pause_music()
            print("Âm thanh: TẮT")
    
    def is_sound_enabled(self):
        return self.sound_enabled

sound_manager = SoundManager()

sound_manager.load_sound('shoot', 'shoot.wav')
sound_manager.load_sound('pop', 'pop.wav')
sound_manager.load_sound('correct', 'correct.wav')
sound_manager.load_sound('win', 'win.wav')
sound_manager.load_sound('lose', 'lose.wav')
sound_manager.load_sound('powerup', 'powerup.wav')
sound_manager.load_sound('explosion', 'explosion.wav')
sound_manager.load_sound('click', 'click.wav')

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, font_size=38):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        self.clicked = False
        self.font = get_font(font_size)
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
        return self.is_hovered
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3, border_radius=15)
        
        if self.is_hovered:
            glow_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 5, 
                                  self.rect.width + 10, self.rect.height + 10)
            pygame.draw.rect(screen, (255, 255, 255, 100), glow_rect, border_radius=20)
        
        text_surface = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_click(self, mouse_pos, mouse_click):
        if self.rect.collidepoint(mouse_pos) and mouse_click:
            sound_manager.play_sound('click')
            self.clicked = True
            return True
        return False

class ImageButton:
    def __init__(self, x, y, image_normal, image_hover=None, scale=1.0, hover_scale=1.1):
        self.x = x
        self.y = y
        self.original_image = image_normal
        self.image_normal = image_normal
        self.image_hover = image_hover if image_hover else image_normal
        self.scale = scale
        self.hover_scale = hover_scale
        self.current_scale = scale
        
        self.current_image = self.image_normal
        self.rect = self.image_normal.get_rect(center=(x, y))
        self.is_hovered = False
        self.clicked = False
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_image = self.image_hover if self.is_hovered else self.image_normal
        self.current_scale = self.hover_scale if self.is_hovered else self.scale
        
        if self.is_hovered and self.current_scale != self.scale:
            width = int(self.original_image.get_width() * self.current_scale)
            height = int(self.original_image.get_height() * self.current_scale)
            scaled_image = pygame.transform.scale(self.original_image, (width, height))
            self.rect = scaled_image.get_rect(center=(self.x, self.y))
        elif not self.is_hovered:
            self.rect = self.image_normal.get_rect(center=(self.x, self.y))
            
        return self.is_hovered
        
    def draw(self, screen):
        if self.current_image:
            if self.is_hovered and self.current_scale != self.scale:
                width = int(self.original_image.get_width() * self.current_scale)
                height = int(self.original_image.get_height() * self.current_scale)
                scaled_image = pygame.transform.scale(self.original_image, (width, height))
                img_rect = scaled_image.get_rect(center=(self.x, self.y))
                screen.blit(scaled_image, img_rect)
                
                glow_surf = pygame.Surface((img_rect.width + 10, img_rect.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (255, 255, 255, 50), 
                               (0, 0, img_rect.width + 10, img_rect.height + 10), 
                               border_radius=15)
                screen.blit(glow_surf, (img_rect.x - 5, img_rect.y - 5))
            else:
                screen.blit(self.current_image, self.rect)
        
    def check_click(self, mouse_pos, mouse_click):
        if self.rect.collidepoint(mouse_pos) and mouse_click:
            sound_manager.play_sound('click')
            self.clicked = True
            return True
        return False

class SoundImageButton:
    def __init__(self, x, y, width=60, height=60):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.clicked = False
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def draw(self, screen):
        if self.is_hovered:
            color = BUTTON_HOVER_COLOR
            border_color = (255, 255, 255)
            glow_rect = pygame.Rect(self.rect.x - 3, self.rect.y - 3, 
                                  self.rect.width + 6, self.rect.height + 6)
            pygame.draw.rect(screen, (255, 255, 255, 100), glow_rect, border_radius=12)
        else:
            color = BUTTON_COLOR
            border_color = (200, 200, 200)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=10)
        
        if sound_manager.is_sound_enabled(): 
            image = sound_on_image
        else: 
            image = sound_off_image
            
        img_rect = image.get_rect(center=self.rect.center)
        screen.blit(image, img_rect)
                
    def check_click(self, mouse_pos, mouse_click):
        if self.rect.collidepoint(mouse_pos) and mouse_click:
            sound_manager.play_sound('click')
            sound_manager.toggle_sound()
            self.clicked = True
            return True
        return False

class Menu:
    def __init__(self):
        self.buttons = []
        self.instructions_scroll_offset = 0
        self.sound_button = None
        self.create_buttons()
        
    def create_buttons(self):
        button_width = 400
        button_height = 80
        center_x = WIDTH // 2 - button_width // 2
        
        self.play_button = Button(center_x, 350, button_width, button_height, "BẮT ĐẦU CHƠI")
        self.instructions_button = Button(center_x, 450, button_width, button_height, "HƯỚNG DẪN")
        self.quit_button = Button(center_x, 550, button_width, button_height, "THOÁT GAME")
        
        self.back_button = Button(50, 50, 200, 60, "QUAY LẠI")
        
        self.sound_button = SoundImageButton(WIDTH - 80, 20)
        
        self.buttons = [self.play_button, self.instructions_button, self.quit_button]
    
    def update(self, mouse_pos):
        for button in self.buttons:
            button.update(mouse_pos)
        self.back_button.update(mouse_pos)
        self.sound_button.update(mouse_pos)
    
    def draw_main_menu(self, screen):
        screen.blit(menu_background, (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        logo_rect = menu_logo_image.get_rect(center=(WIDTH//2, 180))
        screen.blit(menu_logo_image, logo_rect)
        
        for button in self.buttons:
            button.draw(screen)
        
        self.sound_button.draw(screen)
    
    def draw_instructions(self, screen):
        screen.blit(menu_background, (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        image_rect = instructions_image.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(instructions_image, image_rect)
            
        pygame.draw.rect(screen, (255, 215, 0), 
                        (image_rect.x - 5, image_rect.y - 5, 
                         image_rect.width + 10, image_rect.height + 10), 3)
        self.back_button.draw(screen)
        self.sound_button.draw(screen)
    
    def handle_click(self, mouse_pos):
        if self.play_button.check_click(mouse_pos, True): return "PLAY"
        elif self.instructions_button.check_click(mouse_pos, True): return "INSTRUCTIONS"
        elif self.quit_button.check_click(mouse_pos, True): return "QUIT"
        elif self.back_button.check_click(mouse_pos, True): return "BACK"
        elif self.sound_button.check_click(mouse_pos, True): return "SOUND_TOGGLE"
        return None

class DatasetGenerator:
    @staticmethod
    def generate_level(level):
        if level == 1:
            data = {
                'ID': list(range(1, 7)),
                'Name': [f'P{i}' for i in range(1, 7)],
                'Age': [25, 32, None, 28, 45, 56],
                'Income': [50000, 65000, 72000, 48000, 85000, 92000]
            }
            df = pd.DataFrame(data)
            age_values = [x for x in df['Age'] if pd.notna(x)]
            correct_value = int(sum(age_values) / len(age_values)) if age_values else 0
            
            missing_cells = [(2, 'Age')]
            correct_values = [correct_value]
            hint = f"Tìm số trung bình tuổi"
            distractors = [correct_value + 5, correct_value - 3, correct_value + 2, 30, 40, 50]
            
        elif level == 2:
            data = {
                'Time': ['9:00', '10:00', '11:00', '12:00', '13:00', '14:00'],
                'Temp': [22.5, None, 24.1, 25.3, 36.0, 24.7]
            }
            df = pd.DataFrame(data)
            correct_value = round((22.5 + 24.1) / 2, 1)
            
            missing_cells = [(1, 'Temp')]
            correct_values = [correct_value]
            hint = f"Tìm số trung bình nhiệt độ"
            distractors = [correct_value + 0.2, correct_value - 0.3, correct_value + 0.5, 23.0, 24.5, 25.0]
            
        elif level == 3:
            data = {
                'Product': ['A', 'B', 'C', 'D', 'E', 'F'],
                'Sales': [150, 200, None, 180, 220, 336],
                'Rating': [4.5, 4.2, 4.7, 3.6, 4.8, 4.6],
                'Category': ['E', 'E', 'B', 'C', 'C', 'E']
            }
            df = pd.DataFrame(data)
            sales_values = [x for x in df['Sales'] if pd.notna(x)]
            correct_value = int(sum(sales_values) / len(sales_values)) if sales_values else 0
            
            missing_cells = [(2, 'Sales')]
            correct_values = [correct_value]
            hint = f"Tìm số trung bình sales"
            distractors = [correct_value + 10, correct_value - 5, correct_value + 15, 170, 210, 230]
            
        else:
            data = {
                'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                'Price': [105.2, 106.5, None, 103.6, 108.9, 106.3],
                'Volume': [1000, 1200, 1100, 1036, 1300, 1400]
            }
            df = pd.DataFrame(data)
            correct_value = 106.5
            
            missing_cells = [(2, 'Price')]
            correct_values = [correct_value]
            hint = f"Tìm số forward fill"
            distractors = [correct_value + 0.5, correct_value - 0.2, correct_value + 0.3, 105.0, 107.0, 110.0]
        
        return df, missing_cells, correct_values, hint, distractors

class Rock:
    def __init__(self, x, y, level=3, image=None):
        self.x = x
        self.y = y
        self.radius = random.randint(30, 45)
        self.active = True
        self.level = level
        
        self.speed_x = random.choice([-1, 1]) * random.uniform(0.3, 0.8)
        self.speed_y = random.uniform(-0.2, 0.2)
        
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-1, 1)
        self.image = image
        if self.image:
            new_size = int(self.radius * 2)
            self.image = pygame.transform.scale(self.image, (new_size, new_size))
    
    def update(self):
        if not self.active:
            return False
            
        self.x += self.speed_x
        self.y += self.speed_y
        
        self.rotation += self.rotation_speed
        if self.rotation > 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360
        
        if self.x < self.radius:
            self.x = self.radius
            self.speed_x = abs(self.speed_x)
        elif self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.speed_x = -abs(self.speed_x)
            
        if self.y < 80:
            self.y = 80
            self.speed_y = abs(self.speed_y)
        elif self.y > HEIGHT * 0.6:
            self.y = HEIGHT * 0.6
            self.speed_y = -abs(self.speed_y)
        
        return True
    
    def draw(self, screen):
        if not self.active:
            return
        
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        img_rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_image, img_rect)
    
    def check_collision(self, bullet_x, bullet_y, bullet_radius):
        if not self.active:
            return False
        
        distance = math.sqrt((bullet_x - self.x)**2 + (bullet_y - self.y)**2)
        return distance < (bullet_radius + self.radius * 0.8)
    
    def destroy(self):
        self.active = False

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.radius = 25
        self.speed_y = random.uniform(1.5, 3.0)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.float_value = random.random() * math.pi * 2
        self.active = True
        self.collected = False
        self.rotation = 0
        self.spawn_time = pygame.time.get_ticks()
        
        self.good_types = ['three_way', 'explosive']
        self.bad_types = ['lose_ammo', 'speedup_cannon']
        
        if power_type == 'good':
            self.specific_type = random.choice(self.good_types)
            self.glow_color = (0, 200, 255)
        else:
            self.specific_type = random.choice(self.bad_types)
            self.glow_color = (255, 150, 0)
    
    def update(self):
        if not self.collected:
            self.float_value += 0.05
            float_offset = math.sin(self.float_value) * 2
            
            self.rotation += 3
            
            self.y += self.speed_y
            self.x += self.speed_x
            
            if self.y > HEIGHT + self.radius:
                self.active = False
                return
            
            if self.x < self.radius:
                self.x = self.radius
                self.speed_x *= -0.5
            elif self.x > WIDTH - self.radius:
                self.x = WIDTH - self.radius
                self.speed_x *= -0.5
    
    def draw(self, screen):
        if self.collected or not self.active:
            return
            
        float_offset = math.sin(self.float_value) * 2
        
        for i in range(3):
            glow_radius = self.radius + i * 3
            alpha = 100 - i * 20
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.glow_color, alpha), 
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, 
                       (self.x - glow_radius, 
                        self.y - glow_radius + float_offset))
        
        if self.type == 'good':
            image = powerup_good_image
        elif self.type == 'bad':
            image = powerup_bad_image
            
        rotated_image = pygame.transform.rotate(image, self.rotation)
        img_rect = rotated_image.get_rect(center=(int(self.x), int(self.y + float_offset)))
        screen.blit(rotated_image, img_rect)
    
    def check_collision(self, bullet_x, bullet_y, bullet_radius):
        if self.collected or not self.active:
            return False
        distance = math.sqrt((bullet_x - self.x)**2 + (bullet_y - self.y)**2)
        return distance < (bullet_radius + self.radius)

class NumberBubble:
    def __init__(self, value, x, y, correct_value=None, is_moving=True, speed_factor=1.0, level=1):
        self.value = value
        self.x = x
        self.y = y
        self.radius = 35
        self.is_moving = is_moving
        self.speed_factor = speed_factor
        self.original_y = y  
        self.level = level
        self.is_correct = False
        
        if not self.is_correct:
            self.speed_x = random.choice([-1, 1]) * random.uniform(1.5, 2) * speed_factor
            self.speed_y = 0  
    
        if correct_value is not None:
            if isinstance(correct_value, float):
                self.is_correct = abs(float(value) - correct_value) < 0.01
            else:
                self.is_correct = str(value) == str(correct_value)
        
        self.collected = False
        self.float_value = random.random() * math.pi * 2

    def update(self):
        if not self.collected and self.is_moving:
            self.float_value += 0.03 * self.speed_factor
            float_offset = math.sin(self.float_value) * 2
            
            if not self.is_correct:
                self.x += self.speed_x
                self.y = self.original_y + float_offset * 2
            else:
                self.x += self.speed_x
            
            if self.x < self.radius:
                self.x = self.radius
                self.speed_x = abs(self.speed_x)
            elif self.x > WIDTH - self.radius:
                self.x = WIDTH - self.radius
                self.speed_x = -abs(self.speed_x)
            
        elif not self.collected:
            self.float_value += 0.03
    
    def draw(self, screen):
        if self.collected:
            return
            
        if self.is_correct:
            image = bubble_images['correct']
        else:
            image = bubble_images['wrong']
        
        float_offset = math.sin(self.float_value) * 3
        screen.blit(image, (int(self.x - image.get_width() // 2), 
                          int(self.y - image.get_height() // 2 + float_offset)))
        
        if isinstance(self.value, float):
            value_text = f"{self.value:.1f}"
        else:
            value_text = str(self.value)
            
        text_color = (255, 255, 255)
        text_surface = font_medium.render(value_text, True, text_color)
        
        outline_color = (0, 0, 0)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    outline_surface = font_medium.render(value_text, True, outline_color)
                    outline_rect = outline_surface.get_rect(center=(int(self.x) + dx, int(self.y) + dy))
                    screen.blit(outline_surface, outline_rect)
        
        text_rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text_surface, text_rect)

    def check_collision(self, bullet_x, bullet_y, bullet_radius):
        if self.collected:
            return False
        distance = math.sqrt((bullet_x - self.x)**2 + (bullet_y - self.y)**2)
        return distance < (bullet_radius + self.radius)

class Explosion:
    def __init__(self, x, y, radius=80):
        self.x = x
        self.y = y
        self.max_radius = radius
        self.current_radius = 10
        self.growth_rate = 8
        self.active = True
    
    def update(self):
        if self.current_radius < self.max_radius:
            self.current_radius += self.growth_rate
        else:
            self.current_radius = self.max_radius
        
        if self.current_radius >= self.max_radius:
            self.active = False
    
    def draw(self, screen):
        for i in range(3):
            radius = int(self.current_radius * (0.7 + i * 0.15))
            alpha = 150 - i * 50
            color = (255, 200, 0, alpha)
            
            explosion_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, color, (radius, radius), radius)
            screen.blit(explosion_surface, (self.x - radius, self.y - radius))
        
        for i in range(12):
            angle = i * math.pi / 6
            length = self.current_radius * 0.8
            end_x = self.x + math.cos(angle) * length
            end_y = self.y + math.sin(angle) * length
            
            for j in range(3):
                sub_length = length * (0.6 + j * 0.2)
                sub_end_x = self.x + math.cos(angle) * sub_length
                sub_end_y = self.y + math.sin(angle) * sub_length
                color = (255, 150 - j * 30, 0)
                pygame.draw.line(screen, color, 
                               (int(self.x), int(self.y)), 
                               (int(sub_end_x), int(sub_end_y)), 
                               max(1, 5 - j * 2))
    
    def check_collision(self, x, y, radius=0):
        distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return distance < (self.current_radius + radius)

class Bullet:
    def __init__(self, x, y, angle, bullet_type='normal'):
        self.x = x
        self.y = y
        self.radius = 15
        self.speed = 15
        self.angle = angle
        self.vx = math.cos(angle) * self.speed
        self.vy = -math.sin(angle) * self.speed
        self.active = True
        self.bullet_type = bullet_type
        
        if bullet_type == 'explosive':
            self.explosion_radius = 80

    def update(self):
        if not self.active:
            return False
            
        self.x += self.vx
        self.y += self.vy
        
        if (self.x < -100 or self.x > WIDTH + 100 or 
            self.y < -100 or self.y > HEIGHT + 100):
            self.active = False
            return True
        return False
    
    def draw(self, screen):
        if not self.active:
            return    
        rotated_bullet = pygame.transform.rotate(bullet_image, math.degrees(self.angle))
        screen.blit(rotated_bullet, 
                   (int(self.x - rotated_bullet.get_width() // 2),
                    int(self.y - rotated_bullet.get_height() // 2)))

class Cannon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.laser_angle= math.pi / 2
        self.base_rotation_speed = 0.02
        self.laser_rotation_speed = self.base_rotation_speed
        self.rotating_right = True
        
        self.min_angle = 0
        self.max_angle = math.pi
        
        self.laser_length = 180
        
        self.speed_timer = 0
        
        self.base_image = cannon_base_image
        self.logo_image = logo_image
    
    def update(self):
        if self.speed_timer > 0:
            self.speed_timer -= 1
            self.laser_rotation_speed = self.base_rotation_speed * 2.0
        else:
            self.laser_rotation_speed = self.base_rotation_speed
        
        if self.rotating_right:
            self.laser_angle += self.laser_rotation_speed
            if self.laser_angle > self.max_angle:
                self.laser_angle = self.max_angle
                self.rotating_right = False
        else:
            self.laser_angle -= self.laser_rotation_speed
            if self.laser_angle < self.min_angle:
                self.laser_angle = self.min_angle
                self.rotating_right = True
    
    def draw_laser(self, screen):
        laser_end_x = self.x + math.cos(self.laser_angle) * self.laser_length
        laser_end_y = self.y - math.sin(self.laser_angle) * self.laser_length
        
        laser_width = 4
        
        color = (255, 50, 50, 200)
        laser_surface = pygame.Surface((HEIGHT,WIDTH), pygame.SRCALPHA)
        pygame.draw.line(laser_surface, color, 
                       (int(self.x), int(self.y)), 
                       (int(laser_end_x), int(laser_end_y)), 
                       laser_width)
        screen.blit(laser_surface, (0, 0))
        
        arrow_length = 20
        arrow_angle = math.pi / 6
        
        angle1 = self.laser_angle + arrow_angle
        angle2 = self.laser_angle - arrow_angle
        
        arrow_x1 = laser_end_x - arrow_length * math.cos(angle1)
        arrow_y1 = laser_end_y + arrow_length * math.sin(angle1)
        
        arrow_x2 = laser_end_x - arrow_length * math.cos(angle2)
        arrow_y2 = laser_end_y + arrow_length * math.sin(angle2)
        
        arrow_points = [
            (int(laser_end_x), int(laser_end_y)),
            (int(arrow_x1), int(arrow_y1)),
            (int(arrow_x2), int(arrow_y2))
        ]
        arrow_color = (255, 100, 100)
        pygame.draw.polygon(screen, arrow_color, arrow_points)
    
    def draw(self, screen):
        self.draw_laser(screen)
        
        base_rect = self.base_image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.base_image, base_rect)
            
        arrow_rect = self.logo_image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.logo_image, arrow_rect)
            
        if self.speed_timer > 0:
            for i in range(2):
                radius = 60 + i * 8
                alpha = 150 - i * 50
                glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 200, 0, alpha), 
                                 (radius, radius), radius)
                screen.blit(glow_surface, (self.x - radius, self.y - radius))
            
            fast_text = font_tiny.render("TĂNG TỐC!", True, (255, 200, 0))
            fast_rect = fast_text.get_rect(center=(self.x, self.y - 80))
            screen.blit(fast_text, fast_rect)
    
    def shoot(self, bullet_type='normal'):
        sound_manager.play_sound('shoot')
        
        laser_end_x = self.x + math.cos(self.laser_angle) * (self.laser_length * 0.8)
        laser_end_y = self.y - math.sin(self.laser_angle) * (self.laser_length * 0.8)
        
        return Bullet(laser_end_x, laser_end_y, self.laser_angle, bullet_type)
    
    def apply_speed_effect(self, duration=300):
        self.speed_timer = duration

class TargetCell:
    def __init__(self, x, y, row_idx, col_name, correct_value=None, width=None, height=None):
        self.x = x
        self.y = y
        self.width = width if width is not None else 150
        self.height = height if height is not None else 60
        self.row_idx = row_idx
        self.col_name = col_name
        self.correct_value = correct_value
        self.filled = False
        self.filled_value = None
        
    def draw(self, screen):
        color = (255, 100, 100) if not self.filled else (100, 255, 100)
        border_color = (255, 200, 200) if not self.filled else (200, 255, 200) 
        border_radius = max(5, min(10, self.height // 6))
        
        pygame.draw.rect(screen, color, 
                        (self.x - self.width//2, self.y - self.height//2, 
                         self.width, self.height), 
                        border_radius=border_radius)
        pygame.draw.rect(screen, border_color, 
                        (self.x - self.width//2, self.y - self.height//2, 
                         self.width, self.height), 
                        3, border_radius=border_radius)   
        if not self.filled:
            if self.height > 40: font_size = get_font(36, bold=True)
            elif self.height > 30: font_size = get_font(28)
            else: font_size = get_font(24)
                
            question_mark = "NULL"
            color_text = (255, 255, 200)
            
            question_surface = font_size.render(question_mark, True, color_text)
            question_rect = question_surface.get_rect(center=(self.x, self.y))
            screen.blit(question_surface, question_rect)
            
        else:
            if self.height > 40: font_size = get_font(28)
            elif self.height > 30: font_size = get_font(24)
            else: font_size = get_font(20)
                
            if self.filled_value is not None:
                value_text = str(self.filled_value)
                if isinstance(self.filled_value, float):
                    value_text = f"{self.filled_value:.1f}"
                
                value_surface = font_size.render(value_text, True, (240, 255, 240))
                value_rect = value_surface.get_rect(center=(self.x, self.y))
                screen.blit(value_surface, value_rect)
        

class DataTable:
    def __init__(self, df, missing_cells, correct_values):
        self.df = df.copy()
        self.missing_cells = missing_cells
        self.correct_values = correct_values
        
        self.cell_width = 100
        self.cell_height = 40
        self.header_height = 35
        self.row_height = 40
        self.table_x = 50
        self.table_y = HEIGHT - 380
        
        self.targets = []
        
        cols = list(df.columns)
        for idx, (row_idx, col_name) in enumerate(missing_cells):
            col_idx = cols.index(col_name)
            x = self.table_x + col_idx * self.cell_width + self.cell_width//2
            y = self.table_y + self.header_height + (row_idx + 0.5) * self.row_height
            
            correct_val = correct_values[idx] if idx < len(correct_values) else None
            
            target_width = self.cell_width - 8
            target_height = self.row_height - 8
            target = TargetCell(x, y, row_idx, col_name, correct_val, target_width, target_height)
            self.targets.append(target)
            break
    
    
    def draw(self, screen):
        table_width = len(self.df.columns) * self.cell_width
        table_height = self.header_height + len(self.df) * self.row_height
        
        table_surface = pygame.Surface((table_width, table_height), pygame.SRCALPHA)
        
        bg_color = (*DATA_TABLE_BG, 180)
        pygame.draw.rect(table_surface, bg_color, 
                        (0, 0, table_width, table_height),
                        border_radius=10)
        
        border_color = (200, 200, 200, 150)
        pygame.draw.rect(table_surface, border_color, 
                        (0, 0, table_width, table_height),
                        2, border_radius=10)
        
        cols = list(self.df.columns)
        for i, col in enumerate(cols):
            x = i * self.cell_width
            
            header_color = (60, 65, 80, 200)
            pygame.draw.rect(table_surface, header_color, 
                           (x, 0, self.cell_width, self.header_height))
            
            col_text = col 
            text_surface = font_tiny.render(col_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x + self.cell_width//2, 
                                                    self.header_height//2))
            table_surface.blit(text_surface, text_rect)
        
        for i in range(len(self.df)):
            row_y = self.header_height + i * self.row_height
            
            for j, col in enumerate(cols):
                cell_x = j * self.cell_width
                is_missing = (i, col) in self.missing_cells
                
                if is_missing:
                    cell_color = (150, 50, 50, 200)
                else:
                    cell_color = (70, 75, 90, 200)
                    
                pygame.draw.rect(table_surface, cell_color, 
                               (cell_x, row_y, self.cell_width, self.row_height))
                
                value = self.df.iloc[i][col]
                if pd.isna(value) or value is None:
                        continue
                else:
                    if isinstance(value, float):
                        value_text = f"{value:.1f}"
                    else:
                        value_text = str(value)
                    
                    color = (255, 255, 255) 
                
                text_surface = font_tiny.render(value_text, True, color)
                text_rect = text_surface.get_rect(center=(cell_x + self.cell_width//2, 
                                                        row_y + self.row_height//2))
                table_surface.blit(text_surface, text_rect)
        
        screen.blit(table_surface, (self.table_x, self.table_y))
        
        if self.targets:
            self.targets[0].draw(screen)

class Game:
    def __init__(self):
        self.cannon = Cannon(WIDTH // 2, HEIGHT - 150)
        self.bullets = []
        self.max_bullets = 10
        self.bullets_fired = 0
        
        self.powerups = []
        self.explosions = []
        self.rocks = []
        self.next_shot_effect = None
        
        self.last_powerup_spawn = 0
        self.powerup_spawn_delay = 2000
        
        self.menu_button = Button(WIDTH - 120, 20, 100, 40, "Menu")
        self.help_button = Button(WIDTH - 230, 20, 100, 40, "?")
        self.sound_button = SoundImageButton(WIDTH - 340, 20)
        
        button_x = WIDTH // 2
        button_y_start = HEIGHT - 180
        
        self.intro_start_button = ImageButton(
            button_x, button_y_start, 
            start_button_image, 
            scale=1.0, 
            hover_scale=1.05
        )
        
        story_button_y = HEIGHT - 180
        
        self.story_continue_button = ImageButton(
            button_x - 180,
            story_button_y, 
            continue_button_image,
            scale=1.0,
            hover_scale=1.05
        )
        
        self.story_back_button = ImageButton(
            button_x + 180,
            story_button_y,
            back_button_image,
            scale=1.0,
            hover_scale=1.05
        )
        
        self.reward_button = ImageButton(
            WIDTH // 2, HEIGHT - 230,
            reward_button_image,
            scale=1.0,
            hover_scale=1.05
        )
        
        self.reward_back_button = ImageButton(
            WIDTH // 2, HEIGHT - 90,
            back_button_image,
            scale=1.0,
            hover_scale=1.05
        )
        
        self.continue_button = None
        self.menu_complete_button = None
        self.restart_button = None
        self.menu_win_button = None
        
        self.reset()
    
    def reset(self):
        self.level = 1
        self.bullets_fired = 0
        self.max_levels = 4
        self.game_state = STATE_INTRO
        self.hint = ""
        self.selected_target = None
        self.distractors = []
        self.previous_state = None
        self.next_shot_effect = None
        self.rocks = []
        
        self.generate_level()
        
    def generate_level(self):
        self.df, self.missing_cells, self.correct_values, self.hint, self.distractors = DatasetGenerator.generate_level(self.level)
        
        self.data_table = DataTable(self.df, self.missing_cells, self.correct_values)
        self.create_number_bubbles()
        
        self.bullets = []
        self.explosions = []
        self.powerups = []
        self.rocks = []
        self.bullets_fired = 0
        self.selected_target = None
        self.show_tutorial = True
        self.tutorial_timer = 180
        
        self.next_shot_effect = None
        
        if self.level >= 2:
            self.cannon.base_rotation_speed = 0.03 + (self.level - 2) * 0.005
            self.cannon.laser_rotation_speed = self.cannon.laser_rotation_speed
            self.cannon.laser_length = max(100, 150 - (self.level - 1) * 15)
        else:
            self.cannon.base_rotation_speed = 0.02
            self.cannon.laser_rotation_speed = self.cannon.laser_rotation_speed
            self.cannon.laser_length = 150
        
        self.cannon.speed_timer = 0
        
        self.last_powerup_spawn = pygame.time.get_ticks()
        
        if self.level >= 3:
            self.create_rocks()
    
    def create_rocks(self):
        self.rocks = []
        
        num_rocks = 2 + (self.level - 3)
        
        for _ in range(num_rocks):
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT // 2)
            rock = Rock(x, y, level=self.level, image=rock_image)
            self.rocks.append(rock)
    
    def create_number_bubbles(self):
        self.number_bubbles = []
        correct_value = self.correct_values[0]
        
        table_y = self.data_table.table_y
        forbidden_zone_top = table_y - 50
        forbidden_zone_bottom = HEIGHT
        
        if self.level == 1:
            safe_y = min(250, forbidden_zone_top - 80)
            correct_x, correct_y = WIDTH // 2, safe_y
            correct_bubble = NumberBubble(correct_value, correct_x, correct_y, correct_value, is_moving=False, level=self.level)
            self.number_bubbles.append(correct_bubble)
            
            safe_positions = []
            base_positions = [
                (correct_x - 120, correct_y - 80), (correct_x + 120, correct_y - 80),
                (correct_x + 220, correct_y - 80), (correct_x - 220, correct_y - 80),
                (correct_x - 120, correct_y + 80), (correct_x + 120, correct_y + 80),
                (correct_x, correct_y - 80), (correct_x + 90, correct_y),
                (correct_x - 90, correct_y), (correct_x + 180, correct_y),
                (correct_x - 180, correct_y), (correct_x, correct_y + 80),
                (correct_x, correct_y + 150)
            ]
            
            for x, y in base_positions:
                if y < forbidden_zone_top - 30:
                    safe_positions.append((x, y))
            
            while len(safe_positions) < 12:
                x = random.randint(100, WIDTH - 100)
                y = random.randint(100, forbidden_zone_top - 80)
                safe_positions.append((x, y))
            
            for i, (x, y) in enumerate(safe_positions):
                if i < len(self.distractors):
                    value = self.distractors[i]
                else:
                    value = random.randint(10, 100)
                
                while str(value) == str(correct_value):
                    value = random.randint(10, 100)
                
                bubble = NumberBubble(value, x, y, correct_value=None, is_moving=False, level=self.level)
                self.number_bubbles.append(bubble)
                
        else:
            difficulty_factor = 1.0 + (self.level - 2) * 0.5
            
            max_safe_y = forbidden_zone_top - 80
            
            y_min = 130
            y_max = max(130, max_safe_y // 3)
            
            correct_y = random.randint(y_min, y_max)
            correct_x = random.randint(200, WIDTH - 200)
            
            bubble = NumberBubble(correct_value, correct_x, correct_y, correct_value, is_moving=True, 
                                speed_factor=difficulty_factor, level=self.level)
            self.number_bubbles.append(bubble)
            
            n_distractors = min(12 + (self.level - 2) * 4, 25)
            
            extended_distractors = self.distractors.copy()
            while len(extended_distractors) < n_distractors:
                if random.random() < 0.5:
                    new_value = random.randint(10, 100)
                    while any(str(new_value) == str(d) for d in extended_distractors) or str(new_value) == str(correct_value):
                        new_value = random.randint(10, 100)
                    extended_distractors.append(new_value)
                else:
                    new_value = round(random.uniform(10, 100), 1)
                    while any(abs(new_value - float(d)) < 0.1 for d in extended_distractors if isinstance(d, (int, float))) or abs(new_value - float(correct_value)) < 0.1:
                        new_value = round(random.uniform(10, 100), 1)
                    extended_distractors.append(new_value)
            
            rows = 4
            row_height = max(20, (forbidden_zone_top - 200) // rows)
            
            y_offset = correct_y + 60
            
            for i in range(n_distractors):
                if i < len(extended_distractors):
                    value = extended_distractors[i]
                else:
                    if random.random() < 0.3:
                        value = random.choice(['X', 'Y', 'Z'])
                    else:
                        value = random.randint(10, 100)
                
                while str(value) == str(correct_value):
                    value = random.randint(10, 100)
                
                row = (i % rows) + 1
                x = random.randint(100, WIDTH - 100)
                y = y_offset + row * row_height
                
                if y > forbidden_zone_top - 50:
                    y = forbidden_zone_top - 50 - random.randint(10, 30)
                
                speed_multiplier = random.uniform(0.8, 1.5)
                
                bubble = NumberBubble(value, x, y, correct_value=None, is_moving=True, 
                                    speed_factor=difficulty_factor * speed_multiplier, level=self.level)
                
                if random.random() < 0.5:
                    bubble.speed_x *= -1
                
                self.number_bubbles.append(bubble)
    
    def spawn_powerup(self):
        current_time = pygame.time.get_ticks()
        
        if self.level >= 2:
            spawn_delay = max(1000, 3000 - (self.level - 2) * 500)
        
        if current_time - self.last_powerup_spawn > spawn_delay:
            self.last_powerup_spawn = current_time
            
            if self.level >= 2:
                power_type = 'good' if random.random() < 0.5 else 'bad'
            
            x = random.randint(50, WIDTH - 50)
            y = -50
            
            powerup = PowerUp(x, y, power_type)
            self.powerups.append(powerup)
    
    def update(self):
        if self.game_state == STATE_PLAYING:
            if self.tutorial_timer > 0:
                self.tutorial_timer -= 1
            
            if self.level >= 2:
                self.spawn_powerup()
            
            mouse_pos = pygame.mouse.get_pos()
            
            self.menu_button.update(mouse_pos)
            self.help_button.update(mouse_pos)
            self.sound_button.update(mouse_pos)
            
            self.cannon.update()
            
            for bubble in self.number_bubbles:
                bubble.update()
            
            if self.level >= 2:
                for powerup in self.powerups[:]:
                    powerup.update()
                    if not powerup.active:
                        self.powerups.remove(powerup)
            
            for rock in self.rocks[:]:
                if not rock.update():
                    self.rocks.remove(rock)
            
            for explosion in self.explosions[:]:
                explosion.update()
                if not explosion.active:
                    self.explosions.remove(explosion)
            
            bullets_to_remove = []
            
            for i, bullet in enumerate(self.bullets):
                if bullet.active:
                    stopped = bullet.update()
                    
                    if stopped:
                        bullets_to_remove.append(i)
                        continue
                    
                    rock_hit = None
                    for rock in self.rocks:
                        if rock.check_collision(bullet.x, bullet.y, bullet.radius):
                            rock_hit = rock
                            break
                    
                    if rock_hit:
                        if bullet.bullet_type == 'explosive':
                            rock_hit.destroy()
                            explosion = Explosion(bullet.x, bullet.y, radius=60)
                            self.explosions.append(explosion)
                            sound_manager.play_sound('explosion')
                        
                        bullet.active = False
                        continue
                    
                    if bullet.bullet_type == 'explosive':
                        for bubble in self.number_bubbles:
                            if not bubble.collected and bubble.check_collision(bullet.x, bullet.y, bullet.radius):
                                explosion = Explosion(bullet.x, bullet.y)
                                self.explosions.append(explosion)
                                sound_manager.play_sound('explosion')
                                bullet.active = False
                                break
                        
                        for powerup in self.powerups:
                            if not powerup.collected and powerup.check_collision(bullet.x, bullet.y, bullet.radius):
                                explosion = Explosion(bullet.x, bullet.y)
                                self.explosions.append(explosion)
                                sound_manager.play_sound('explosion')
                                bullet.active = False
                                break
                    
                    closest_bubble = None
                    min_distance = float('inf')
                    
                    for bubble in self.number_bubbles:
                        if not bubble.collected and bubble.check_collision(bullet.x, bullet.y, bullet.radius):
                            distance = math.sqrt((bullet.x - bubble.x)**2 + (bullet.y - bubble.y)**2)
                            if distance < min_distance:
                                min_distance = distance
                                closest_bubble = bubble
                    
                    if closest_bubble:
                        bullet.active = False
                        closest_bubble.collected = True
                        
                        if closest_bubble.is_correct:
                            sound_manager.play_sound('correct')
                            
                            if self.data_table.targets:
                                target = self.data_table.targets[0]
                                if not target.filled:
                                    target.filled = True
                                    target.filled_value = closest_bubble.value                          
                            
                            if self.level < self.max_levels:
                                self.game_state = STATE_LEVEL_COMPLETE
                            else:
                                sound_manager.play_sound('win')
                                self.game_state = STATE_GAME_COMPLETE
                            
                            return
                        else:
                            sound_manager.play_sound('pop')
                        
                        continue
                    
                    if self.level >= 2:
                        powerup_collided = None
                        for powerup in self.powerups:
                            if not powerup.collected and powerup.check_collision(bullet.x, bullet.y, bullet.radius):
                                powerup_collided = powerup
                                break
                        
                        if powerup_collided:
                            bullet.active = False
                            powerup_collided.collected = True
                            
                            self.apply_powerup_effect(powerup_collided)
                            
                            continue
            
            for explosion in self.explosions:
                for rock in self.rocks[:]:
                    if explosion.check_collision(rock.x, rock.y, rock.radius):
                        rock.destroy()
                
                for bubble in self.number_bubbles:
                    if not bubble.collected and explosion.check_collision(bubble.x, bubble.y, bubble.radius):
                        bubble.collected = True
                        
                        if bubble.is_correct:
                            sound_manager.play_sound('correct')
                            
                            if self.data_table.targets:
                                target = self.data_table.targets[0]
                                if not target.filled:
                                    target.filled = True
                                    target.filled_value = bubble.value
                            
                            if self.level < self.max_levels:
                                self.game_state = STATE_LEVEL_COMPLETE
                            else:
                                sound_manager.play_sound('win')
                                self.game_state = STATE_GAME_COMPLETE
                            
                            return
                        else:
                            sound_manager.play_sound('pop')
                
                for powerup in self.powerups:
                    if not powerup.collected and explosion.check_collision(powerup.x, powerup.y, powerup.radius):
                        powerup.collected = True
                        self.apply_powerup_effect(powerup)
            
            for i in sorted(bullets_to_remove, reverse=True):
                if i < len(self.bullets):
                    del self.bullets[i]
            
            if self.game_state == STATE_PLAYING:
                active_bullets = sum(1 for b in self.bullets if b.active)
                
                if self.bullets_fired >= self.max_bullets and active_bullets == 0:
                    if not self.selected_target or not self.selected_target.filled:
                        sound_manager.play_sound('lose')
                        self.game_state = STATE_GAME_OVER
    
    def apply_powerup_effect(self, powerup):
        if powerup.type == 'good':
            sound_manager.play_sound('powerup')
            
            if powerup.specific_type == 'three_way':
                self.next_shot_effect = 'three_way'
                self.show_powerup_message("LẦN BẮN TIẾP: 3 tia đạn!")
                
            elif powerup.specific_type == 'explosive':
                self.next_shot_effect = 'explosive'
                self.show_powerup_message("LẦN BẮN TIẾP: Đạn nổ!")
                
        else:
            sound_manager.play_sound('powerup')
            
            if powerup.specific_type == 'lose_ammo':
                self.bullets_fired = min(self.max_bullets, self.bullets_fired + 2)
                self.show_powerup_message("MẤT ĐẠN! -2 viên đạn", is_bad=True)
                
            elif powerup.specific_type == 'speedup_cannon':
                self.cannon.apply_speed_effect(300)
                self.show_powerup_message("SÚNG NHANH! Tốc độ quay tăng", is_bad=True)
    
    def show_powerup_message(self, message, is_bad=False):
        self.powerup_message = message
        self.powerup_message_timer = 120
        self.powerup_message_is_bad = is_bad
    
    def shoot_bullet(self):
        if self.game_state == STATE_PLAYING and self.bullets_fired < self.max_bullets:
            bullet_type = 'normal'
            
            if self.next_shot_effect:
                bullet_type = self.next_shot_effect
                self.next_shot_effect = None
            
            if bullet_type == 'three_way':
                bullets = []
                for i in range(3):
                    angle_offset = (i - 1) * 0.3
                    bullet = Bullet(
                        self.cannon.x + math.cos(self.cannon.laser_angle + angle_offset) * (self.cannon.laser_length + 10),
                        self.cannon.y - math.sin(self.cannon.laser_angle + angle_offset) * (self.cannon.laser_length + 10),
                        self.cannon.laser_angle + angle_offset,
                        'three_way'
                    )
                    bullets.append(bullet)
                
                self.bullets.extend(bullets)
                self.bullets_fired += 1
                return True
                
            else:
                bullet = self.cannon.shoot(bullet_type)
                self.bullets.append(bullet)
                self.bullets_fired += 1
                return True
        return False
    
    def draw_intro(self, screen, mouse_pos):
        screen.blit(intro_image, (0, 0))
        
        self.intro_start_button.update(mouse_pos)
        self.intro_start_button.draw(screen)
    
    def draw_story(self, screen, mouse_pos):
        screen.blit(story_image, (0, 0))
        
        self.story_continue_button.update(mouse_pos)
        self.story_continue_button.draw(screen)
        
        self.story_back_button.update(mouse_pos)
        self.story_back_button.draw(screen)
    
    def draw_ui(self, screen):
        ui_top_height = 100
        ui_top = pygame.Surface((WIDTH, ui_top_height), pygame.SRCALPHA)
        ui_top.fill((*UI_BG, 180))
        
        level_text = font_medium.render(f"Cấp độ: {self.level}/{self.max_levels}", True, (255, 255, 255))
        ui_top.blit(level_text, (20, 15))
        
        remaining_bullets = self.max_bullets - self.bullets_fired
        bullets_text = font_medium.render(f"Đạn: {remaining_bullets}/{self.max_bullets}", True, 
                                         (255, 200, 200) if remaining_bullets <= 3 else (255, 255, 255))
        bullets_x = WIDTH // 2 - bullets_text.get_width() // 2
        ui_top.blit(bullets_text, (bullets_x, 15))
        
        y_line2 = 55
        
        hint_text = font_small.render(f"{self.hint}", True, (255, 255, 200))
        if hint_text.get_width() > 400:
            hint_text = font_small.render(f"{self.hint[:40]}...", True, (255, 255, 200))
        ui_top.blit(hint_text, (20, y_line2))
        
        shoot_text = font_small.render("SPACE: BẮN", True, (255, 220, 150))
        shoot_x = WIDTH // 2 - shoot_text.get_width() // 2
        ui_top.blit(shoot_text, (shoot_x, y_line2))
        
        pygame.draw.rect(ui_top, (0, 0, 0, 100), (0, ui_top_height - 2, WIDTH, 2))
        
        screen.blit(ui_top, (0, 0))
        
        ui_bottom = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        ui_bottom.fill((*UI_BG, 180))
        pygame.draw.rect(ui_bottom, (0, 0, 0, 100), (0, 0, WIDTH, 2))
        screen.blit(ui_bottom, (0, HEIGHT - 100))
        
        self.cannon.draw(screen)
        
        if self.game_state == STATE_PLAYING:
            self.menu_button.draw(screen)
            self.help_button.draw(screen)
            self.sound_button.draw(screen)
        
        if self.show_tutorial and self.tutorial_timer > 0:
            self.draw_tutorial(screen)
        
        if hasattr(self, 'powerup_message_timer') and self.powerup_message_timer > 0:
            self.draw_powerup_message(screen)
    
    def draw_tutorial(self, screen):
        correct_value = self.correct_values[0] if self.correct_values else "?"
        
        if self.level == 1:
            title = f"LEVEL {self.level} - HỌC CÁCH CHƠI"
            target = f"TÌM SỐ TRUNG BÌNH"
            instructions = [
                "1. BẮN tập tin SAI để mở đường",
                "2. Bắn trúng tập tin ĐÚNG để thắng ngay"
            ]
            title_font = get_font(34, bold=True)
            target_font = get_font(32, bold=True)
            content_font = get_font(30)
        elif self.level == 2:
            title = f"LEVEL {self.level} - VẬT PHẨM RƠI"
            target = f"TÌM SỐ TRUNG BÌNH"
            instructions = [
                "1. Quà là vật phẩm có lợi",
                "2. Virus là vật phẩm bất lợi"
            ]
            title_font = get_font(34, bold=True)
            target_font = get_font(32, bold=True)
            content_font = get_font(30)
        elif self.level == 3:
            title = f"LEVEL {self.level} - ĐÁ LỞ!"
            target = f"TÌM SỐ!"
            instructions = [
                " CẢNH BÁO: Đá xuất hiện!",
                "• Đá chỉ có thể bị phá bởi ĐẠN NỔ",
            ]
            title_font = get_font(34, bold=True)
            target_font = get_font(32, bold=True)
            content_font = get_font(28)
        else:
            title = f" LEVEL {self.level} - TRÙM CUỐI!"
            target = f"TÌM SỐ ĐI NÀO!"
            instructions = []
            title_font = get_font(34, bold=True)
            target_font = get_font(32, bold=True)
            content_font = get_font(30)
        
        title_surf = title_font.render(title, True, (255, 215, 0))
        target_surf = target_font.render(target, True, (100, 255, 100))
        
        max_width = max(
            title_surf.get_width(),
            target_surf.get_width(),
            500
        )
        
        line_height = 38
        title_height = 49
        target_height = 47
        
        instruction_height = 0
        instruction_surfaces = []
        for instruction in instructions:
            words = instruction.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surf = content_font.render(test_line, True, (255, 255, 200))
                
                if test_surf.get_width() <= max_width - 40:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for line in lines:
                surf = content_font.render(line, True, (255, 255, 200))
                instruction_surfaces.append(surf)
                instruction_height += line_height
        
        total_height = (title_height + target_height + instruction_height + 40)
        
        box_width = max_width + 40
        box_height = total_height + 20
        
        tutorial_box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        tutorial_box.fill((0, 0, 0, 200))
        pygame.draw.rect(tutorial_box, (255, 215, 0), 
                    (0, 0, box_width, box_height), 3, border_radius=10)
        
        title_x = (box_width - title_surf.get_width()) // 2
        tutorial_box.blit(title_surf, (title_x, 20))
        
        target_x = (box_width - target_surf.get_width()) // 2
        tutorial_box.blit(target_surf, (target_x, 20 + title_height))
        
        y_pos = 20 + title_height + target_height
        
        for surf in instruction_surfaces:
            x_pos = (box_width - surf.get_width()) // 2
            tutorial_box.blit(surf, (x_pos, y_pos))
            y_pos += line_height
        
        screen.blit(tutorial_box, (WIDTH//2 - box_width//2, 100))
    
    def draw_powerup_message(self, screen):
        message_box = pygame.Surface((400, 60), pygame.SRCALPHA)
        
        if self.powerup_message_is_bad:
            message_box.fill((255, 50, 50, 200))
            border_color = (255, 150, 150)
            text_color = (255, 255, 200)
        else:
            message_box.fill((50, 200, 255, 200))
            border_color = (150, 255, 255)
            text_color = (255, 255, 200)
        
        pygame.draw.rect(message_box, border_color, 
                        (0, 0, 400, 60), 3, border_radius=10)
        
        screen.blit(message_box, (WIDTH//2 - 200, HEIGHT - 400))
        
        message_surf = font_medium.render(self.powerup_message, True, text_color)
        screen.blit(message_surf, (WIDTH//2 - message_surf.get_width()//2, HEIGHT - 380))
        
        self.powerup_message_timer -= 1
    
    def draw_sky_numbers(self, screen):
        for rock in self.rocks:
            rock.draw(screen)
            
        for bubble in sorted(self.number_bubbles, key=lambda b: b.y, reverse=True):
            bubble.draw(screen)
        
        for powerup in self.powerups:
            powerup.draw(screen)
        
        for explosion in self.explosions:
            explosion.draw(screen)
    
    def draw_level_start(self, screen):
        screen.blit(background_images[self.level], (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        title = font_xlarge.render(f"CÁCH CHƠI", True, (255, 255, 200))
        subtitle = font_large.render("NHẤN SPACE ĐỂ BẮN", True, (200, 200, 255))
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 + 10))
        
        start_text = font_medium.render("Nhấn SPACE để bắt đầu", True, (255, 255, 100))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 80))
            
    def draw_level_complete(self, screen):
        screen.blit(background_images[self.level], (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        title = font_xlarge.render("CHIẾN THẮNG!", True, (100, 255, 100))
        shots_text = font_medium.render(f"Số đạn đã dùng: {self.bullets_fired}/{self.max_bullets}", True, TEXT_COLOR)
        
        if self.level < self.max_levels:
            next_text = font_medium.render("Chuyển sang Level " + str(self.level + 1), True, (200, 200, 255))
        else:
            next_text = font_medium.render("Hoàn thành level cuối cùng!", True, (200, 200, 255))
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
        screen.blit(shots_text, (WIDTH//2 - shots_text.get_width()//2, HEIGHT//2 - 40))
        screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 10))
        
        mouse_pos = pygame.mouse.get_pos()
        
        self.continue_button = Button(WIDTH//2 - 160, HEIGHT//2 + 80, 150, 50, "TIẾP TỤC")
        self.continue_button.update(mouse_pos)
        self.continue_button.draw(screen)
        
        self.menu_complete_button = Button(WIDTH//2 + 10, HEIGHT//2 + 80, 150, 50, "MENU")
        self.menu_complete_button.update(mouse_pos)
        self.menu_complete_button.draw(screen)
        
    def draw_game_over(self, screen):
        screen.blit(background_images[self.level], (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        title = font_xlarge.render("HẾT ĐẠN!", True, (255, 100, 100))
        shots_text = font_medium.render(f"Đã dùng: {self.bullets_fired} viên đạn", True, TEXT_COLOR)
        
        if self.data_table.targets and not self.data_table.targets[0].filled:
            target = self.data_table.targets[0]
            correct_info = font_medium.render(f"Giá trị đúng: {target.correct_value}", True, (200, 255, 200))
            screen.blit(correct_info, (WIDTH//2 - correct_info.get_width()//2, HEIGHT//2 + 60))
        
        restart_text = font_medium.render("Nhấn SPACE để về Menu", True, (200, 200, 255))
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 80))
        screen.blit(shots_text, (WIDTH//2 - shots_text.get_width()//2, HEIGHT//2 - 20))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
        
    def draw_game_complete(self, screen):
        screen.blit(congrats_background, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        self.reward_button.update(mouse_pos)
        self.reward_button.draw(screen)
    
    def draw_reward_screen(self, screen):
        screen.blit(reward_background, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        self.reward_back_button.update(mouse_pos)
        self.reward_back_button.draw(screen)
    
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.game_state == STATE_LEVEL_START:
                    self.game_state = STATE_PLAYING
                elif self.game_state == STATE_PLAYING:
                    self.shoot_bullet()
                elif self.game_state == STATE_GAME_OVER:
                    self.game_state = STATE_MENU
                    
            elif event.key == pygame.K_r:
                self.reset()
                
            elif event.key == pygame.K_ESCAPE:
                if self.game_state == STATE_PLAYING:
                    self.game_state = STATE_MENU
                else:
                    pygame.quit()
                    sys.exit()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                
                if self.game_state == STATE_INTRO:
                    if self.intro_start_button.check_click((mouse_x, mouse_y), True):
                        self.game_state = STATE_STORY
                    return
                    
                elif self.game_state == STATE_STORY:
                    if self.story_continue_button.check_click((mouse_x, mouse_y), True):
                        self.game_state = STATE_MENU
                        return
                    
                    if self.story_back_button.check_click((mouse_x, mouse_y), True):
                        self.game_state = STATE_INTRO
                        return
                
                elif self.game_state == STATE_PLAYING:
                    if self.menu_button.rect.collidepoint(mouse_x, mouse_y):
                        self.game_state = STATE_MENU
                        return
                    
                    if self.help_button.rect.collidepoint(mouse_x, mouse_y):
                        self.previous_state = self.game_state
                        self.game_state = STATE_INSTRUCTIONS
                        return
                    
                    if self.sound_button.check_click((mouse_x, mouse_y), True):
                        return
                
                elif self.game_state == STATE_LEVEL_COMPLETE:
                    if self.continue_button and self.continue_button.rect.collidepoint(mouse_x, mouse_y):
                        self.level += 1
                        self.generate_level()
                        self.game_state = STATE_PLAYING
                        return
                    
                    if self.menu_complete_button and self.menu_complete_button.rect.collidepoint(mouse_x, mouse_y):
                        self.game_state = STATE_MENU
                        return
                
                elif self.game_state == STATE_GAME_COMPLETE:
                    if self.reward_button.check_click((mouse_x, mouse_y), True):
                        self.game_state = STATE_REWARD
                        return
                
                elif self.game_state == STATE_REWARD:
                    if self.reward_back_button.check_click((mouse_x, mouse_y), True):
                        self.game_state = STATE_MENU
                        return

def main():
    clock = pygame.time.Clock()
    game = Game()
    menu = Menu()
    
    sound_manager.play_music('background_music.mp3', volume=0.3)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game.game_state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = menu.handle_click(mouse_pos)
                    if action == "PLAY":
                        game.reset()
                        game.game_state = STATE_LEVEL_START
                        menu.instructions_scroll_offset = 0
                    elif action == "INSTRUCTIONS":
                        game.game_state = STATE_INSTRUCTIONS
                        menu.instructions_scroll_offset = 0
                    elif action == "QUIT":
                        running = False
                    elif action == "SOUND_TOGGLE":
                        pass
            
            elif game.game_state == STATE_INSTRUCTIONS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = menu.handle_click(mouse_pos)
                    if action == "BACK":
                        if game.previous_state:
                            game.game_state = game.previous_state
                            game.previous_state = None
                        else:
                            game.game_state = STATE_MENU
                    elif action == "SOUND_TOGGLE":
                        pass
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        menu.instructions_scroll_offset += 30
                    elif event.key == pygame.K_UP:
                        menu.instructions_scroll_offset -= 30
                    
                    menu.instructions_scroll_offset = max(0, menu.instructions_scroll_offset)
            
            else:
                game.handle_event(event)
        
        if game.game_state == STATE_PLAYING:
            game.update()
        elif game.game_state in [STATE_MENU, STATE_INSTRUCTIONS]:
            menu.update(mouse_pos)
        
        if game.game_state == STATE_INTRO:
            game.draw_intro(screen, mouse_pos)
        elif game.game_state == STATE_STORY:
            game.draw_story(screen, mouse_pos)
        elif game.game_state == STATE_REWARD:
            game.draw_reward_screen(screen)
        elif game.game_state in [STATE_PLAYING, STATE_LEVEL_START, STATE_LEVEL_COMPLETE, STATE_GAME_OVER]:
            screen.blit(background_images[game.level], (0, 0))
        
        if game.game_state not in [STATE_MENU, STATE_INSTRUCTIONS, STATE_INTRO, STATE_STORY, STATE_REWARD]:
            game.draw_sky_numbers(screen)
            
            for bullet in game.bullets:
                bullet.draw(screen)
                
            game.data_table.draw(screen)
            game.draw_ui(screen)
            
            if game.game_state == STATE_LEVEL_START:
                game.draw_level_start(screen)
            elif game.game_state == STATE_LEVEL_COMPLETE:
                game.draw_level_complete(screen)
            elif game.game_state == STATE_GAME_OVER:
                game.draw_game_over(screen)
            elif game.game_state == STATE_GAME_COMPLETE:
                game.draw_game_complete(screen)
        
        if game.game_state == STATE_MENU:
            menu.draw_main_menu(screen)
        elif game.game_state == STATE_INSTRUCTIONS:
            menu.draw_instructions(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
