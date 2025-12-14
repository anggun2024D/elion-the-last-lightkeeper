"""
ELION – The Last Lightkeeper 
"""

import pygame
import os
import sys
import math
import random
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum

# Initialize Pygame dengan pengaturan yang lebih baik
pygame.init()
pygame.mixer.init()

# ==================== ENHANCED VISUAL SETTINGS ====================
try:
    # Coba set OpenGL untuk rendering yang lebih baik
    from pygame import gl
    USE_OPENGL = False  # Nonaktifkan untuk kompatibilitas
except ImportError:
    USE_OPENGL = False

# Enable anti-aliasing
pygame.display.set_mode((0, 0), pygame.HWSURFACE | pygame.DOUBLEBUF)

# ==================== CONSTANTS ====================
class GameState(Enum):
    MENU = "menu"
    WORLD_MAP = "world_map"
    CUTSCENE = "cutscene"
    PLAYING = "playing"
    PAUSE = "pause"
    WIN = "win"
    GAMEOVER = "gameover"
    ENDING = "ending"
    CODEX_VIEW = "codex_view"

class Level(Enum):
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3

# Screen settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
RENDER_WIDTH = 640
RENDER_HEIGHT = 360
FPS = 60

# Enhanced Colors dengan gradien yang lebih smooth
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_SPIRIT_CYAN = (120, 240, 255)
COLOR_WHISPER_GREEN = (180, 220, 180)
COLOR_ANCIENT_TEAL = (74, 166, 166)
COLOR_HONEY_BROWN = (190, 150, 100)
COLOR_SHADOW_PURPLE = (170, 120, 240)
COLOR_GEM_GREEN = (120, 240, 120)
COLOR_GEM_BLUE = (100, 180, 240)
COLOR_GEM_YELLOW = (255, 240, 120)
COLOR_SUNSET_ORANGE = (255, 127, 40)
COLOR_SUNSET_RED = (159, 40, 40)
COLOR_BURNT_BROWN = (72, 41, 25)
COLOR_EMBER_ORANGE = (255, 89, 40)
COLOR_FLARE_WOLF = (255, 89, 40)
COLOR_MARBLE_CYAN = (156, 255, 255)
COLOR_PILLAR_WHITE = (250, 255, 255)
COLOR_MIST_WHITE = (255, 255, 255)
COLOR_ALTAR_CRYSTAL = (220, 255, 255)
COLOR_SPIRIT_TREE = (120, 255, 220)
COLOR_MAP_BG = (20, 25, 40)
COLOR_MAP_LINE = (120, 170, 255, 120)
COLOR_MAP_LINE_ACTIVE = (120, 255, 220, 220)
COLOR_LOCATION_INACTIVE = (120, 120, 120)
COLOR_LOCATION_ACTIVE = (255, 255, 255)
COLOR_SPIRIT_FOREST = (120, 255, 170)
COLOR_CRIMSON_MOUNTAIN = (255, 120, 120)
COLOR_LIGHTKEEPER_CASTLE = (255, 255, 120)
COLOR_BUTTON_DISABLED = (100, 100, 100)
COLOR_BUTTON_ENABLED = (120, 255, 220)
COLOR_CODEX_BG = (30, 35, 50, 240)
COLOR_MENTOR_AURA = (255, 255, 220, 120)

# Entity sizes dengan variasi yang lebih baik
PLAYER_SIZE = 32
COMPANION_SIZE = 30
ENEMY_SIZE = 30
GEM_SIZE = 22
PORTAL_SIZE = 52
TILE_SIZE = 34
MINI_BOSS_SIZE = 44
FLARE_WOLF_SIZE = 30

# Game tuning
PLAYER_SPEED = 150
COMPANION_FOLLOW_SPEED = 0.08
ENEMY_PATROL_SPEED = 80
ENEMY_CHASE_SPEED = 120
PARTICLE_POOL_SIZE = 300

# Level-specific
LEVEL2_WORLD_WIDTH = 2560
LEVEL2_WORLD_HEIGHT = 1080
LEVEL3_WORLD_WIDTH = 1920
LEVEL3_WORLD_HEIGHT = 1440

# Attack system
PLAYER_ATTACK_COOLDOWN = 0.5
SPIRIT_BURST_SPEED = 280.0
SPIRIT_BURST_LIFETIME = 1.2
SPIRIT_BURST_SIZE = 12
ATTACK_RANGE = 400


# ==================== ENHANCED PARTICLE SYSTEM ====================
@dataclass
class ParticleData:
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    life: float = 0.0
    max_life: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 255)
    size: int = 3
    active: bool = False
    particle_type: str = "default"
    rotation: float = 0.0
    rotation_speed: float = 0.0

class ParticleSystem:
    def __init__(self, max_particles: int = PARTICLE_POOL_SIZE):
        self.particles: List[ParticleData] = [ParticleData() for _ in range(max_particles)]
        self.max_particles = max_particles
        self.glow_cache = {}
    
    def create_glow_surface(self, size: int, color: Tuple[int, int, int], alpha: int) -> pygame.Surface:
        """Cache glow surfaces untuk performa lebih baik"""
        key = (size, color, alpha)
        if key not in self.glow_cache:
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            # Multi-layer glow untuk efek lebih halus
            for i in range(3, 0, -1):
                layer_size = size - i * 2
                layer_alpha = alpha // (i + 1)
                pygame.draw.circle(surf, (*color, layer_alpha), 
                                 (size, size), layer_size)
            self.glow_cache[key] = surf
        return self.glow_cache[key]
    
    def emit(self, x: float, y: float, color: Tuple[int, int, int], 
             count: int = 10, spread: float = 50.0, life: float = 1.0,
             particle_type: str = "default", gravity: float = 50.0,
             rotation_speed: float = 0.0) -> None:
        emitted = 0
        for particle in self.particles:
            if not particle.active and emitted < count:
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(20, spread)
                particle.x = x
                particle.y = y
                particle.vx = math.cos(angle) * speed
                
                if particle_type == "ember":
                    particle.vy = random.uniform(-70, -30)
                    particle.rotation_speed = random.uniform(-2, 2)
                elif particle_type == "mist":
                    particle.vx = random.uniform(-12, 12)
                    particle.vy = random.uniform(-8, 8)
                    particle.rotation_speed = random.uniform(-0.5, 0.5)
                elif particle_type == "light_flower":
                    particle.vx = random.uniform(-20, 20)
                    particle.vy = random.uniform(-50, -30)
                    particle.rotation_speed = random.uniform(-1, 1)
                elif particle_type == "sparkle":
                    particle.vx = random.uniform(-15, 15)
                    particle.vy = random.uniform(-15, 15)
                    particle.rotation_speed = random.uniform(-3, 3)
                else:
                    particle.vy = math.sin(angle) * speed - 40
                
                particle.life = life
                particle.max_life = life
                particle.color = color
                particle.size = random.randint(2, 5)
                particle.active = True
                particle.particle_type = particle_type
                particle.rotation = random.uniform(0, math.pi * 2)
                particle.rotation_speed = rotation_speed or random.uniform(-2, 2)
                emitted += 1
    
    def update(self, dt: float) -> None:
        for particle in self.particles:
            if particle.active:
                particle.x += particle.vx * dt
                particle.y += particle.vy * dt
                particle.rotation += particle.rotation_speed * dt
                
                if particle.particle_type == "ember":
                    particle.vy += 45 * dt
                    if random.random() < 0.1:
                        particle.vx += random.uniform(-12, 12)
                elif particle.particle_type == "mist":
                    particle.vy += 6 * dt
                    particle.vx += math.sin(particle.life * 3) * 0.8
                elif particle.particle_type == "light_flower":
                    particle.vy += 12 * dt
                elif particle.particle_type == "sparkle":
                    particle.vy += 30 * dt
                    particle.vx += math.sin(particle.life * 5) * 2
                else:
                    particle.vy += 60 * dt
                
                particle.life -= dt
                if particle.life <= 0:
                    particle.active = False
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        for particle in self.particles:
            if particle.active:
                alpha_ratio = particle.life / particle.max_life
                if alpha_ratio > 0:
                    x = int(particle.x - camera_offset[0])
                    y = int(particle.y - camera_offset[1])
                    
                    if particle.particle_type == "mist":
                        mist_size = int(particle.size * 2.5)
                        mist_surf = pygame.Surface((mist_size * 2, mist_size * 2), pygame.SRCALPHA)
                        mist_alpha = int(100 * alpha_ratio)
                        
                        # Mist dengan gradien
                        for i in range(3, 0, -1):
                            layer_size = mist_size - i * 4
                            layer_alpha = mist_alpha // (i + 2)
                            pygame.draw.circle(mist_surf, (*particle.color, layer_alpha), 
                                             (mist_size, mist_size), layer_size)
                        
                        surface.blit(mist_surf, (x - mist_size, y - mist_size), 
                                   special_flags=pygame.BLEND_ALPHA_SDL2)
                        
                    elif particle.particle_type == "light_flower":
                        glow_surf = pygame.Surface((particle.size * 8, particle.size * 8), pygame.SRCALPHA)
                        glow_alpha = int(180 * alpha_ratio)
                        
                        # Outer glow
                        pygame.draw.circle(glow_surf, (*particle.color, glow_alpha // 2), 
                                         (particle.size * 4, particle.size * 4), particle.size * 4)
                        # Inner glow
                        pygame.draw.circle(glow_surf, (*particle.color, glow_alpha), 
                                         (particle.size * 4, particle.size * 4), particle.size * 2)
                        # Core
                        core_alpha = int(220 * alpha_ratio)
                        pygame.draw.circle(glow_surf, (255, 255, 255, core_alpha),
                                         (particle.size * 4, particle.size * 4), particle.size)
                        
                        surface.blit(glow_surf, (x - particle.size * 4, y - particle.size * 4),
                                   special_flags=pygame.BLEND_ADD)
                        
                    elif particle.particle_type == "sparkle":
                        # Sparkle dengan rotasi
                        sparkle_size = particle.size * 2
                        sparkle_surf = pygame.Surface((sparkle_size * 2, sparkle_size * 2), pygame.SRCALPHA)
                        sparkle_alpha = int(200 * alpha_ratio)
                        
                        # Bintang berujung 4
                        points = []
                        for i in range(4):
                            angle = particle.rotation + i * math.pi / 2
                            outer_x = sparkle_size + math.cos(angle) * sparkle_size
                            outer_y = sparkle_size + math.sin(angle) * sparkle_size
                            inner_x = sparkle_size + math.cos(angle + math.pi/4) * (sparkle_size * 0.4)
                            inner_y = sparkle_size + math.sin(angle + math.pi/4) * (sparkle_size * 0.4)
                            points.append((outer_x, outer_y))
                            points.append((inner_x, inner_y))
                        
                        pygame.draw.polygon(sparkle_surf, (*particle.color, sparkle_alpha), points)
                        surface.blit(sparkle_surf, (x - sparkle_size, y - sparkle_size),
                                   special_flags=pygame.BLEND_ADD)
                        
                    else:
                        # Particle biasa dengan glow
                        particle_size = int(particle.size * (0.8 + 0.4 * math.sin(particle.life * 5)))
                        pygame.draw.circle(surface, particle.color, (x, y), particle_size)
                        
                        if particle_size > 2:
                            glow_surf = self.create_glow_surface(particle_size, particle.color, 
                                                               int(120 * alpha_ratio))
                            surface.blit(glow_surf, (x - particle_size, y - particle_size),
                                       special_flags=pygame.BLEND_ALPHA_SDL2)


# ==================== ENHANCED CAMERA ====================
class Camera:
    def __init__(self, width: int, height: int, world_width: int, world_height: int):
        self.width = width
        self.height = height
        self.world_width = world_width
        self.world_height = world_height
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.smoothing = 0.08  # Lebih smooth
        self.shake_timer = 0.0
        self.shake_intensity = 0.0
        self.shake_decay = 0.9
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_smoothing = 0.03
    
    def set_target(self, x: float, y: float) -> None:
        self.target_x = x - self.width // 2
        self.target_y = y - self.height // 2
    
    def set_zoom(self, zoom: float) -> None:
        self.target_zoom = zoom
    
    def shake(self, intensity: float = 5.0, duration: float = 0.3) -> None:
        self.shake_timer = duration
        self.shake_intensity = intensity
    
    def update(self, dt: float) -> None:
        # Smooth camera movement
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
        
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_smoothing
        
        effective_width = self.width / self.zoom
        effective_height = self.height / self.zoom
        
        self.x = max(0, min(self.x, self.world_width - effective_width))
        self.y = max(0, min(self.y, self.world_height - effective_height))
        
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.shake_intensity *= self.shake_decay
    
    def get_offset(self) -> Tuple[int, int]:
        offset_x = int(self.x)
        offset_y = int(self.y)
        
        if self.shake_timer > 0:
            # Shake dengan easing
            intensity = self.shake_intensity * (self.shake_timer / 0.3)
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, intensity)
            offset_x += int(math.cos(angle) * distance)
            offset_y += int(math.sin(angle) * distance)
        
        return (offset_x, offset_y)

# ==================== ENHANCED WORLD MAP ====================
class Location:
    def __init__(self, name: str, pos: Tuple[int, int], color: Tuple[int, int, int], 
                 level: Level, radius: int = 44):
        self.name = name
        self.pos = pos
        self.color = color
        self.level = level
        self.radius = radius
        self.unlocked = False
        self.codex_read = False
        self.hovered = False
        self.pulse_timer = 0.0
        self.glow_surface = None
        self.create_glow_surface()
        
    def create_glow_surface(self):
        """Create cached glow surface untuk performa"""
        glow_size = self.radius + 20
        self.glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Multi-layer glow
        for i in range(4, 0, -1):
            layer_size = glow_size - i * 4
            layer_alpha = 60 // (i + 1)
            pygame.draw.circle(self.glow_surface, (*self.color, layer_alpha), 
                             (glow_size, glow_size), layer_size)
        
    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        distance = math.sqrt((mouse_pos[0] - self.pos[0])**2 + (mouse_pos[1] - self.pos[1])**2)
        return distance <= self.radius
        
    def update(self, dt: float):
        self.pulse_timer += dt
        
    def draw(self, surface: pygame.Surface) -> None:
        pulse = (math.sin(self.pulse_timer * 2) + 1) * 0.1 + 0.9
        
        # Outer glow if unlocked
        if self.unlocked:
            glow_alpha = 120 if self.hovered else 60
            temp_glow = self.glow_surface.copy()
            temp_glow.fill((255, 255, 255, glow_alpha), None, pygame.BLEND_RGBA_MULT)
            surface.blit(temp_glow, (self.pos[0] - (self.radius + 20), 
                                   self.pos[1] - (self.radius + 20)))
        
        # Main circle dengan efek 3D
        color = self.color if self.unlocked else COLOR_LOCATION_INACTIVE
        current_radius = int(self.radius * pulse)
        
        # Shadow
        shadow_offset = 3
        pygame.draw.circle(surface, (0, 0, 0, 100), 
                         (self.pos[0] + shadow_offset, self.pos[1] + shadow_offset), 
                         current_radius)
        
        # Main circle
        pygame.draw.circle(surface, color, self.pos, current_radius)
        
        # Highlight
        highlight_size = current_radius - 2
        highlight_surf = pygame.Surface((highlight_size * 2, highlight_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(highlight_surf, (255, 255, 255, 60), 
                         (highlight_size, highlight_size), highlight_size)
        surface.blit(highlight_surf, (self.pos[0] - highlight_size, 
                                     self.pos[1] - highlight_size))
        
        # Inner circle
        inner_color = (255, 255, 255) if self.unlocked else (170, 170, 170)
        inner_radius = int(current_radius * 0.7)
        pygame.draw.circle(surface, inner_color, self.pos, inner_radius)
        
        # Icon dengan detail lebih baik
        if "Forest" in self.name:
            self.draw_tree_icon(surface)
        elif "Mountain" in self.name:
            self.draw_mountain_icon(surface)
        elif "Castle" in self.name:
            self.draw_castle_icon(surface)
        
        # Checkmark dengan glow
        if self.codex_read:
            check_size = 14
            check_pos = (self.pos[0] + 28, self.pos[1] - 28)
            
            # Checkmark glow
            check_glow = pygame.Surface((check_size * 4, check_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(check_glow, (100, 255, 100, 100), 
                             (check_size * 2, check_size * 2), check_size * 2)
            surface.blit(check_glow, (check_pos[0] - check_size * 2, 
                                    check_pos[1] - check_size * 2))
            
            # Checkmark
            pygame.draw.circle(surface, (80, 220, 80), check_pos, check_size)
            font = pygame.font.Font(None, 22)
            check = font.render("✓", True, (255, 255, 255))
            surface.blit(check, (check_pos[0] - 7, check_pos[1] - 9))
    
    def draw_tree_icon(self, surface: pygame.Surface):
        """Draw enhanced tree icon"""
        # Trunk
        trunk_width = 16
        trunk_height = 24
        trunk_x = self.pos[0] - trunk_width // 2
        trunk_y = self.pos[1] - trunk_height // 2
        pygame.draw.rect(surface, (70, 140, 70), 
                       (trunk_x, trunk_y, trunk_width, trunk_height), 
                       border_radius=4)
        
        # Canopy layers
        canopy_colors = [(90, 200, 90), (110, 210, 110), (130, 220, 130)]
        for i, color in enumerate(canopy_colors):
            canopy_y = self.pos[1] - 20 - i * 8
            canopy_radius = 20 - i * 4
            pygame.draw.circle(surface, color, (self.pos[0], canopy_y), canopy_radius)
            
            # Highlight
            highlight_surf = pygame.Surface((canopy_radius * 2, canopy_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(highlight_surf, (255, 255, 255, 40), 
                             (canopy_radius, canopy_radius), canopy_radius)
            surface.blit(highlight_surf, (self.pos[0] - canopy_radius, canopy_y - canopy_radius))
    
    def draw_mountain_icon(self, surface: pygame.Surface):
        """Draw enhanced mountain icon"""
        # Mountain base
        base_points = [
            (self.pos[0] - 24, self.pos[1] + 12),
            (self.pos[0], self.pos[1] - 28),
            (self.pos[0] + 24, self.pos[1] + 12)
        ]
        pygame.draw.polygon(surface, (170, 100, 100), base_points)
        
        # Snow cap
        snow_points = [
            (self.pos[0] - 12, self.pos[1] - 8),
            (self.pos[0], self.pos[1] - 28),
            (self.pos[0] + 12, self.pos[1] - 8)
        ]
        pygame.draw.polygon(surface, (240, 240, 255), snow_points)
        
        # Volcano crater dengan lava glow
        crater_glow = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(crater_glow, (255, 140, 60, 150), (12, 12), 12)
        surface.blit(crater_glow, (self.pos[0] - 12, self.pos[1] - 12))
        
        pygame.draw.circle(surface, (255, 100, 60), self.pos, 10)
        pygame.draw.circle(surface, (255, 180, 80), self.pos, 6)
    
    def draw_castle_icon(self, surface: pygame.Surface):
        """Draw enhanced castle icon"""
        # Main castle body
        castle_width = 36
        castle_height = 24
        castle_x = self.pos[0] - castle_width // 2
        castle_y = self.pos[1] - castle_height // 2
        
        # Castle base dengan shading
        pygame.draw.rect(surface, (220, 200, 120), 
                       (castle_x, castle_y, castle_width, castle_height),
                       border_radius=6)
        
        # Shadow effect
        pygame.draw.rect(surface, (200, 180, 100), 
                       (castle_x, castle_y, castle_width, castle_height),
                       width=2, border_radius=6)
        
        # Towers
        tower_width = 12
        tower_height = 16
        left_tower_x = castle_x - 4
        right_tower_x = castle_x + castle_width - tower_width + 4
        
        for tx in [left_tower_x, right_tower_x]:
            pygame.draw.rect(surface, (200, 180, 100), 
                           (tx, castle_y - 8, tower_width, tower_height),
                           border_radius=4)
            
            # Tower roofs
            roof_points = [
                (tx, castle_y - 8),
                (tx + tower_width // 2, castle_y - 16),
                (tx + tower_width, castle_y - 8)
            ]
            pygame.draw.polygon(surface, (180, 160, 90), roof_points)
        
        # Flag dengan animasi sederhana
        flag_y = castle_y - 20 + math.sin(self.pulse_timer) * 2
        pygame.draw.line(surface, (120, 100, 60), 
                       (self.pos[0], castle_y - 8), 
                       (self.pos[0], flag_y), 3)
        
        flag_points = [
            (self.pos[0], flag_y),
            (self.pos[0] + 14, flag_y - 6),
            (self.pos[0], flag_y - 12)
        ]
        pygame.draw.polygon(surface, (200, 60, 60), flag_points)


class CodexPanel:
    def __init__(self, location: Location):
        self.location = location
        self.visible = False
        self.scroll_offset = 0
        self.scroll_speed = 0
        self.max_scroll = 0
        
        # Enhanced content dengan formatting
        if location.name == "Spirit Forest":
            self.title = "🌲 Spirit Forest – Menjaga Kekuatan Dalam"
            self.image_color = COLOR_SPIRIT_FOREST
            self.content = [
                "Sejak zaman kuno, Lightkeeper menyimpan cahaya di dalam dirinya.",
                "Tidak semua orang boleh mengakses kekuatan tersebut.",
                "Hanya ritual tertentu yang dapat membuka rahasia ini.",
                "",
                "Di hutan ini, ELION belajar:",
                "• Menyimpan atribut dengan aman (_x, _inventory)",
                "• Mengakses melalui method khusus (get_position())",
                "• Melindungi data dari perubahan sembarangan",
                "",
                "════════════════════════════════════════",
                "ENCAPSULATION:",
                "Menjaga kekuatan dari dunia luar."
            ]
            self.oop_concept = "ENCAPSULATION"
            
        elif location.name == "Crimson Mountain":
            self.title = "⛰️ Crimson Mountain – Warisan Kekuatan"
            self.image_color = COLOR_CRIMSON_MOUNTAIN
            self.content = [
                "Makhluk bayangan berasal dari sumber yang sama,",
                "namun berkembang menjadi wujud berbeda.",
                "",
                "Di gunung berapi ini, ELION menemukan:",
                "• Enemy sebagai kelas dasar",
                "• GlimpEnemy & UmbraEnemy sebagai turunan",
                "• Masing-masing mewarisi atribut dasar",
                "• Namun memiliki perilaku yang unik",
                "",
                "════════════════════════════════════════",
                "INHERITANCE:",
                "Warisan kemampuan dengan variasi bentuk."
            ]
            self.oop_concept = "INHERITANCE"
            
        else:  # Lightkeeper Castle
            self.title = "🏰 Lightkeeper Castle – Satu Panggilan, Banyak Bentuk"
            self.image_color = COLOR_LIGHTKEEPER_CASTLE
            self.content = [
                "Satu perintah dapat menghasilkan tindakan berbeda",
                "tergantung siapa yang menerimanya.",
                "",
                "Di kastil akhir, ELION menyadari:",
                "• Method take_action() dipanggil sama",
                "• Hasil berbeda untuk tiap enemy",
                "• Fleksibilitas dalam merespon",
                "• Konsistensi dalam antarmuka",
                "",
                "════════════════════════════════════════",
                "POLYMORPHISM:",
                "Banyak bentuk dari satu antarmuka."
            ]
            self.oop_concept = "POLYMORPHISM"
        
        # Create decorative elements
        self.create_decorative_elements()
    
    def create_decorative_elements(self):
        """Create cached decorative surfaces"""
        self.panel_bg = None
        self.concept_badge = None
        self.illustration = None
    
    def update_scroll(self, mouse_wheel: int):
        """Update scroll offset based on mouse wheel"""
        if self.max_scroll > 0:
            self.scroll_offset += mouse_wheel * 30
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
    
    def draw(self, surface: pygame.Surface) -> pygame.Rect:
        """Draw enhanced codex panel with improved layout"""
        if not self.visible:
            return pygame.Rect(0, 0, 0, 0)
            
        # Background overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        surface.blit(overlay, (0, 0))
        
        # Panel dimensions
        panel_width = 900
        panel_height = 650
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        # Create panel surface
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Glass effect background
        pygame.draw.rect(panel_surf, (*COLOR_CODEX_BG[:3], 220), 
                        (0, 0, panel_width, panel_height), border_radius=25)
        
        # Border with gradient
        border_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, (120, 200, 255, 80), 
                        (0, 0, panel_width, panel_height), 5, border_radius=25)
        panel_surf.blit(border_surf, (0, 0))
        
        # Inner glow
        inner_glow = pygame.Surface((panel_width - 30, panel_height - 30), pygame.SRCALPHA)
        pygame.draw.rect(inner_glow, (255, 255, 255, 30), 
                        (0, 0, panel_width - 30, panel_height - 30), border_radius=20)
        panel_surf.blit(inner_glow, (15, 15))
        
        # Title
        font_title = pygame.font.Font(None, 48)
        title_text = font_title.render(self.title, True, (255, 255, 220))
        title_shadow = font_title.render(self.title, True, (0, 0, 0, 120))
        panel_surf.blit(title_shadow, (panel_width//2 - title_shadow.get_width()//2 + 2, 42))
        panel_surf.blit(title_text, (panel_width//2 - title_text.get_width()//2, 40))
        
        # Decorative separator
        sep_surf = pygame.Surface((panel_width - 100, 3), pygame.SRCALPHA)
        for i in range(sep_surf.get_width()):
            alpha = int(200 * (1 - abs(i - sep_surf.get_width()//2) / (sep_surf.get_width()//2)))
            sep_surf.set_at((i, 0), (*self.image_color, alpha))
            sep_surf.set_at((i, 1), (*self.image_color, alpha//2))
        panel_surf.blit(sep_surf, (50, 100))
        
        # Illustration
        ill_size = 140
        ill_x = panel_width//2 - ill_size//2
        ill_y = 120
        
        # Glow around illustration
        glow_surf = pygame.Surface((ill_size + 60, ill_size + 60), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.image_color, 100), 
                         ((ill_size + 60)//2, (ill_size + 60)//2), (ill_size + 60)//2)
        panel_surf.blit(glow_surf, (ill_x - 30, ill_y - 30))
        
        # Draw illustration based on location
        ill_surf = pygame.Surface((ill_size, ill_size), pygame.SRCALPHA)
        if "Forest" in self.location.name:
            # Tree
            pygame.draw.circle(ill_surf, (*self.image_color, 180), 
                             (ill_size//2, ill_size//3), ill_size//3)
            pygame.draw.rect(ill_surf, (160, 130, 90, 200), 
                           (ill_size//2 - 12, ill_size//2, 24, ill_size//2))
        elif "Mountain" in self.location.name:
            # Mountain
            points = [(ill_size//2, 25), (25, ill_size - 25), (ill_size - 25, ill_size - 25)]
            pygame.draw.polygon(ill_surf, (*self.image_color, 180), points)
            # Snow cap
            snow_points = [(ill_size//2, 25), (ill_size//2 - 15, 45), (ill_size//2 + 15, 45)]
            pygame.draw.polygon(ill_surf, (255, 255, 255, 200), snow_points)
        else:  # Castle
            pygame.draw.rect(ill_surf, (*self.image_color, 180), 
                           (35, 45, ill_size - 70, ill_size - 90), border_radius=10)
            # Towers
            pygame.draw.rect(ill_surf, (180, 160, 120, 200), 
                           (20, 25, 20, 40), border_radius=5)
            pygame.draw.rect(ill_surf, (180, 160, 120, 200), 
                           (ill_size - 40, 25, 20, 40), border_radius=5)
        
        panel_surf.blit(ill_surf, (ill_x, ill_y))
        
        # Concept badge
        font_concept = pygame.font.Font(None, 40)
        concept_text = font_concept.render(self.oop_concept, True, (255, 255, 180))
        concept_shadow = font_concept.render(self.oop_concept, True, (0, 0, 0, 120))
        badge_y = 290
        panel_surf.blit(concept_shadow, (panel_width//2 - concept_shadow.get_width()//2 + 2, badge_y + 2))
        panel_surf.blit(concept_text, (panel_width//2 - concept_text.get_width()//2, badge_y))
        
        # Content area with scroll
        content_font = pygame.font.Font(None, 24)
        y_offset = 350 - self.scroll_offset
        content_width = panel_width - 100
        
        for line in self.content:
            if not line.strip():
                y_offset += 20
                continue
                
            if line.startswith("════"):
                # Decorative separator
                sep_width = content_width - 50
                sep_x = 50 + (content_width - sep_width)//2
                for i in range(sep_width):
                    alpha = int(120 * (1 - abs(i - sep_width//2) / (sep_width//2)))
                    pygame.draw.line(panel_surf, (*self.image_color, alpha),
                                   (sep_x + i, y_offset), (sep_x + i, y_offset + 2))
                y_offset += 25
            elif line.startswith("•"):
                # Bullet point
                bullet_x = 70
                pygame.draw.circle(panel_surf, self.image_color, (bullet_x, y_offset + 10), 5)
                text = content_font.render(line[2:], True, (230, 245, 255))
                panel_surf.blit(text, (bullet_x + 20, y_offset))
                y_offset += 28
            elif line.endswith(":") and ":" in line:
                # Header
                header_font = pygame.font.Font(None, 28)
                text = header_font.render(line, True, (255, 255, 150))
                panel_surf.blit(text, (panel_width//2 - text.get_width()//2, y_offset))
                y_offset += 35
            else:
                # Regular text
                words = line.split()
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if content_font.size(test_line)[0] > content_width - 20:
                        if current_line:
                            text = content_font.render(current_line, True, (240, 250, 255))
                            panel_surf.blit(text, (panel_width//2 - text.get_width()//2, y_offset))
                            y_offset += 26
                            current_line = word
                        else:
                            # Force break long word
                            text = content_font.render(word, True, (240, 250, 255))
                            panel_surf.blit(text, (60, y_offset))
                            y_offset += 26
                    else:
                        current_line = test_line
                if current_line:
                    text = content_font.render(current_line, True, (240, 250, 255))
                    panel_surf.blit(text, (panel_width//2 - text.get_width()//2, y_offset))
                    y_offset += 26
        
        self.max_scroll = max(0, y_offset - panel_height + 120)
        
        # Scrollbar if needed
        if self.max_scroll > 0:
            scrollbar_height = panel_height - 100
            scrollbar_y = 50 + (self.scroll_offset / self.max_scroll) * (scrollbar_height - 50)
            pygame.draw.rect(panel_surf, (100, 150, 200, 150), 
                           (panel_width - 20, 50, 8, scrollbar_height), border_radius=4)
            pygame.draw.rect(panel_surf, (150, 200, 255, 200), 
                           (panel_width - 18, scrollbar_y, 4, 50), border_radius=2)
        
        # Close button
        button_rect = pygame.Rect(panel_width//2 - 120, panel_height - 90, 240, 50)
        button_surf = pygame.Surface((240, 50), pygame.SRCALPHA)
        
        # Button gradient
        for y in range(50):
            alpha = int(160 * (1 - y/50))
            pygame.draw.line(button_surf, (*COLOR_BUTTON_ENABLED, alpha), (0, y), (240, y))
        
        pygame.draw.rect(button_surf, (255, 255, 255, 120), (0, 0, 240, 50), 3, border_radius=15)
        panel_surf.blit(button_surf, (button_rect.x, button_rect.y))
        
        # Button text
        button_font = pygame.font.Font(None, 28)
        button_text = button_font.render("Tutup Codex", True, (0, 0, 0))
        button_shadow = button_font.render("Tutup Codex", True, (255, 255, 255, 80))
        panel_surf.blit(button_shadow, (panel_width//2 - button_shadow.get_width()//2 + 1, panel_height - 75 + 1))
        panel_surf.blit(button_text, (panel_width//2 - button_text.get_width()//2, panel_height - 75))
        
        # Draw panel
        surface.blit(panel_surf, (panel_x, panel_y))
        
        return button_rect.move(panel_x, panel_y)


class WorldMap:
    def __init__(self):
        self.locations = [
            Location("Spirit Forest", (200, 300), COLOR_SPIRIT_FOREST, Level.LEVEL_1),
            Location("Crimson Mountain", (600, 300), COLOR_CRIMSON_MOUNTAIN, Level.LEVEL_2),
            Location("Lightkeeper Castle", (1000, 300), COLOR_LIGHTKEEPER_CASTLE, Level.LEVEL_3)
        ]
        self.locations[0].unlocked = True  # Forest always unlocked
        
        self.codex_panel = None
        self.all_codex_read = False
        self.start_button_rect = None
        
        # Particle system for map
        self.particles = []
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'speed': random.uniform(0.5, 2),
                'size': random.uniform(1, 3),
                'alpha': random.randint(50, 150)
            })
    
    def update(self, dt: float) -> None:
        """Update map particles"""
        for p in self.particles:
            p['y'] -= p['speed']
            if p['y'] < -10:
                p['y'] = WINDOW_HEIGHT + 10
                p['x'] = random.randint(0, WINDOW_WIDTH)
    
    def check_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Check which location is hovered"""
        for loc in self.locations:
            loc.hovered = loc.is_clicked(mouse_pos)
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[CodexPanel]:
        """Handle click on world map"""
        # Check locations
        for loc in self.locations:
            if loc.unlocked and loc.is_clicked(mouse_pos):
                self.codex_panel = CodexPanel(loc)
                self.codex_panel.visible = True
                return self.codex_panel
        
        # Check start button
        if self.all_codex_read and self.start_button_rect:
            if self.start_button_rect.collidepoint(mouse_pos):
                return "start_journey"
        
        return None
    
    def mark_codex_read(self) -> None:
        """Mark current location's codex as read"""
        if self.codex_panel:
            for loc in self.locations:
                if loc.name in self.codex_panel.title:
                    loc.codex_read = True
                    self.codex_panel.visible = False
                    
                    # Unlock next location if available
                    current_index = self.locations.index(loc)
                    if current_index < len(self.locations) - 1:
                        self.locations[current_index + 1].unlocked = True
                    
                    # Check if all codex read
                    self.all_codex_read = all(loc.codex_read for loc in self.locations)
                    break
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw world map"""
        # Background
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(COLOR_MAP_BG[0] * (1 - ratio) + 5 * ratio)
            g = int(COLOR_MAP_BG[1] * (1 - ratio) + 10 * ratio)
            b = int(COLOR_MAP_BG[2] * (1 - ratio) + 20 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))
        
        # Particles
        for p in self.particles:
            pygame.draw.circle(surface, (100, 200, 255, p['alpha']), 
                             (int(p['x']), int(p['y'])), int(p['size']))
        
        # Title
        font_title = pygame.font.Font(None, 72)
        title = font_title.render("PETA PERJALANAN ELION", True, (200, 230, 255))
        surface.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        # Subtitle
        font_sub = pygame.font.Font(None, 28)
        subtitle = font_sub.render("Pelajari pengetahuan sebelum memulai", True, (180, 220, 255))
        surface.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, 120))
        
        # Connection lines
        for i in range(len(self.locations) - 1):
            loc1 = self.locations[i]
            loc2 = self.locations[i + 1]
            
            line_color = COLOR_MAP_LINE_ACTIVE if loc1.codex_read else COLOR_MAP_LINE
            line_width = 4 if loc1.codex_read else 2
            
            # Animated particles along the line if active
            if loc1.codex_read:
                t = (pygame.time.get_ticks() % 3000) / 3000
                px = loc1.pos[0] + (loc2.pos[0] - loc1.pos[0]) * t
                py = loc1.pos[1] + (loc2.pos[1] - loc1.pos[1]) * t
                pygame.draw.circle(surface, (100, 255, 200), (int(px), int(py)), 6)
            
            pygame.draw.line(surface, line_color, loc1.pos, loc2.pos, line_width)
        
        # Draw locations
        for loc in self.locations:
            loc.draw(surface)
            
            # Show name on hover
            if loc.hovered and loc.unlocked:
                font = pygame.font.Font(None, 32)
                name = font.render(loc.name, True, (255, 255, 200))
                surface.blit(name, (loc.pos[0] - name.get_width()//2, loc.pos[1] + 60))
                
                status = "✓ Sudah dipelajari" if loc.codex_read else "📖 Klik untuk pelajari"
                status_font = pygame.font.Font(None, 22)
                status_text = status_font.render(status, True, (200, 255, 200))
                surface.blit(status_text, (loc.pos[0] - status_text.get_width()//2, loc.pos[1] + 90))
        
        # Start Journey Button
        if self.all_codex_read:
            button_width, button_height = 500, 60
            button_x = WINDOW_WIDTH//2 - button_width//2
            button_y = WINDOW_HEIGHT - 150
            
            # Glow effect
            pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) * 0.3 + 0.7
            glow_surf = pygame.Surface((button_width + 40, button_height + 40), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (100, 255, 200, int(100 * pulse)), 
                           (20, 20, button_width, button_height), border_radius=15)
            surface.blit(glow_surf, (button_x - 20, button_y - 20))
            
            # Button
            pygame.draw.rect(surface, COLOR_BUTTON_ENABLED, 
                           (button_x, button_y, button_width, button_height), border_radius=10)
            pygame.draw.rect(surface, (255, 255, 255), 
                           (button_x, button_y, button_width, button_height), 3, border_radius=10)
            
            font_button = pygame.font.Font(None, 30)
            button_text = font_button.render("MULAI PERJALANAN ELION", True, (0, 0, 0))
            surface.blit(button_text, (button_x + button_width//2 - button_text.get_width()//2, 
                                     button_y + 15))
            
            self.start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        else:
            # Disabled button
            button_width, button_height = 500, 60
            button_x = WINDOW_WIDTH//2 - button_width//2
            button_y = WINDOW_HEIGHT - 150
            
            pygame.draw.rect(surface, COLOR_BUTTON_DISABLED, 
                           (button_x, button_y, button_width, button_height), border_radius=10)
            pygame.draw.rect(surface, (100, 100, 100), 
                           (button_x, button_y, button_width, button_height), 2, border_radius=10)
            
            font_button = pygame.font.Font(None, 30)
            button_text = font_button.render("PELAJARI SEMUA CODEX TERLEBIH DAHULU", True, (200, 200, 200))
            surface.blit(button_text, (button_x + button_width//2 - button_text.get_width()//2, 
                                     button_y + 20))
            
            self.start_button_rect = None

# ==================== PLAYER ====================
class Player:
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
        self._vx = 0.0
        self._vy = 0.0
        self._speed = PLAYER_SPEED
        self._size = PLAYER_SIZE
        self._inventory: List[str] = []
        self._lives = 3
        self._score = 0
        self._invincible_timer = 0.0
        self._glow_timer = 0.0
        self._glow_color: Optional[Tuple[int, int, int]] = None
        self._idle_timer = 0.0
        self._bob_offset = 0.0
        self._rotation = 0.0
        
        # Level 3 altar interaction
        self._at_altar = False
        self._placing_gems = False
        self._gem_placement_timer = 0.0

        # Attack system for Level 2+
        self._has_spirit_lantern = False
        self._attack_cooldown = 0.0
        self._last_direction = (1, 0)
        self._spirit_bursts: List[dict] = []
        self._attack_flash_timer = 0.0
        self._trail_particles: List[dict] = []
        
        # Reference to particle system for drawing
        self._particle_system_ref: Optional[ParticleSystem] = None
        
        # Create cached surfaces
        self._player_surface = None
        self._glow_surface = None
        self.create_surfaces()
    
    def create_surfaces(self):
        """Create authentic pixel art knight sprite surfaces"""
        # Player surface (32x32 or 48x48 untuk pixel art klasik)
        base_size = 32
        self._size = 64  # Ukuran lebih besar untuk player yang lebih dominan
        temp_surface = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
        
        # Color palette untuk pixel art (warna terbatas, lebih terang)
        silver = (180, 180, 180)       # Perak
        steel_blue = (100, 140, 180)   # Biru baja
        gold = (220, 190, 60)          # Emas tua
        brown = (100, 70, 40)          # Coklat
        black = (20, 20, 20)           # Hitam (tidak terlalu pekat)
        white = (255, 255, 255)        # Putih
        skin_light = (255, 220, 180)   # Kulit terang
        skin_dark = (240, 190, 140)    # Kulit gelap
        red = (180, 60, 60)            # Merah
        blue_energy = (80, 180, 255)   # Biru energi
        blue_dark = (40, 80, 160)      # Biru tua
        gray = (100, 100, 100)         # Abu-abu
        
        # === BODY/ARMOR ===
        # Chest plate - bentuk kotak pixel
        for y in range(10, 18):  # y: 10-17
            for x in range(8, 24):  # x: 8-23
                temp_surface.set_at((x, y), silver)
        
        # Armor shading - sisi kiri lebih gelap
        for y in range(10, 18):
            for x in range(8, 12):
                pixel = list(silver)
                pixel[0] = max(0, pixel[0] - 20)
                pixel[1] = max(0, pixel[1] - 20)
                pixel[2] = max(0, pixel[2] - 20)
                temp_surface.set_at((x, y), tuple(pixel))
        
        # Armor highlights - sisi kanan lebih terang
        for y in range(10, 18):
            for x in range(20, 24):
                pixel = list(silver)
                pixel[0] = min(255, pixel[0] + 20)
                pixel[1] = min(255, pixel[1] + 20)
                pixel[2] = min(255, pixel[2] + 20)
                temp_surface.set_at((x, y), tuple(pixel))
        
        # Gold trim di pinggir armor
        for x in range(8, 24):
            temp_surface.set_at((x, 10), gold)  # Atas
            temp_surface.set_at((x, 17), gold)  # Bawah
        
        for y in range(10, 18):
            temp_surface.set_at((8, y), gold)   # Kiri
            temp_surface.set_at((23, y), gold)  # Kanan
        
        # Blue emblem di tengah armor
        temp_surface.set_at((15, 13), blue_energy)
        temp_surface.set_at((16, 13), blue_energy)
        temp_surface.set_at((15, 14), blue_energy)
        temp_surface.set_at((16, 14), blue_energy)
        
        # Cross emblem
        temp_surface.set_at((15, 12), blue_dark)
        temp_surface.set_at((16, 12), blue_dark)
        temp_surface.set_at((15, 15), blue_dark)
        temp_surface.set_at((16, 15), blue_dark)
        temp_surface.set_at((14, 13), blue_dark)
        temp_surface.set_at((14, 14), blue_dark)
        temp_surface.set_at((17, 13), blue_dark)
        temp_surface.set_at((17, 14), blue_dark)
        
        # === HEAD ===
        # Wajah - bentuk oval pixel
        for y in range(4, 10):
            for x in range(12, 20):
                if (x >= 13 and x <= 18 and y >= 5 and y <= 9):
                    temp_surface.set_at((x, y), skin_light)
        
        # Rambut - bentuk helm sederhana
        for y in range(2, 5):
            for x in range(12, 20):
                if (x >= 13 and x <= 18 and y >= 3 and y <= 4):
                    temp_surface.set_at((x, y), brown)
        
        # Helmet outline
        for y in range(4, 10):
            for x in [12, 19]:
                temp_surface.set_at((x, y), gray)
        
        for x in range(12, 20):
            temp_surface.set_at((x, 4), gray)
            temp_surface.set_at((x, 9), gray)
        
        # Helmet crest (sederhana)
        temp_surface.set_at((15, 2), red)
        temp_surface.set_at((16, 2), red)
        temp_surface.set_at((15, 1), red)
        temp_surface.set_at((16, 1), red)
        
        # === EYES ===
        # Pixel eyes yang sederhana
        temp_surface.set_at((14, 6), white)
        temp_surface.set_at((17, 6), white)
        temp_surface.set_at((14, 6), black)  # Override dengan pupil
        temp_surface.set_at((17, 6), black)  # Override dengan pupil
        
        # Eye highlight (1 pixel)
        temp_surface.set_at((15, 6), white)
        temp_surface.set_at((18, 6), white)
        
        # === LOWER BODY ===
        # Leather pants
        for y in range(18, 24):
            for x in range(10, 22):
                if (x >= 11 and x <= 20 and y >= 19 and y <= 23):
                    temp_surface.set_at((x, y), brown)
        
        # Pants shading
        for y in range(19, 24):
            for x in range(11, 15):
                pixel = list(brown)
                pixel[0] = max(0, pixel[0] - 20)
                pixel[1] = max(0, pixel[1] - 20)
                pixel[2] = max(0, pixel[2] - 20)
                temp_surface.set_at((x, y), tuple(pixel))
        
        # === BOOTS ===
        # Left boot
        for y in range(24, 28):
            for x in range(10, 16):
                if (x >= 11 and x <= 15 and y >= 25 and y <= 27):
                    temp_surface.set_at((x, y), black)
        
        # Right boot
        for y in range(24, 28):
            for x in range(16, 22):
                if (x >= 17 and x <= 21 and y >= 25 and y <= 27):
                    temp_surface.set_at((x, y), black)
        
        # Boot buckles
        temp_surface.set_at((13, 26), silver)
        temp_surface.set_at((19, 26), silver)
        
        # === ARMS ===
        # Left arm (atas)
        for i in range(4):
            temp_surface.set_at((7 - i, 13 + i), skin_dark)
        
        # Left arm (bawah)
        for i in range(3):
            temp_surface.set_at((4 + i, 17), skin_dark)
        
        # Right arm (atas - memegang pedang)
        for i in range(4):
            temp_surface.set_at((24 + i, 13 + i), skin_light)
        
        # === SWORD ===
        # Sword handle
        for y in range(15, 19):
            for x in range(27, 29):
                temp_surface.set_at((x, y), brown)
        
        # Sword blade (pixelated energy)
        blade_pixels = [
            (29, 14), (30, 14), (31, 14),
            (29, 15), (30, 15), (31, 15),
            (29, 16), (30, 16), (31, 16),
            (29, 17), (30, 17), (31, 17),
        ]
        
        for px in blade_pixels:
            temp_surface.set_at(px, blue_energy)
        
        # Sword core (lebih terang)
        core_pixels = [(30, 15), (30, 16)]
        for px in core_pixels:
            temp_surface.set_at(px, white)
        
        # === CAPE ===
        # Cape back (simple triangle shape)
        cape_points = [
            (10, 10), (22, 10),  # Top line
            (25, 20),            # Bottom right
            (7, 20),             # Bottom left
        ]
        
        # Fill cape dengan warna merah pixel
        for y in range(10, 21):
            for x in range(7, 26):
                # Simple point-in-polygon untuk pixel art
                if (x >= 10 - (y - 10) and x <= 22 + (y - 10)):
                    if y <= 20:
                        temp_surface.set_at((x, y), red)
        
        # Cape shading (sisi kiri lebih gelap)
        for y in range(10, 21):
            for x in range(7, 16):
                if temp_surface.get_at((x, y))[:3] == red:
                    pixel = list(red)
                    pixel[0] = max(0, pixel[0] - 40)
                    pixel[1] = max(0, pixel[1] - 40)
                    pixel[2] = max(0, pixel[2] - 40)
                    temp_surface.set_at((x, y), tuple(pixel))
        
        # Cape pattern (salib sederhana)
        cross_pixels = [
            (15, 12), (16, 12), (17, 12),
            (15, 13), (16, 13), (17, 13),
            (15, 14), (16, 14), (17, 14),
            (14, 13), (18, 13),
        ]
        
        for px in cross_pixels:
            if px[1] < 21:  # Pastikan dalam bounds
                temp_surface.set_at(px, white)
        
        # === SHADOWS DAN HIGHLIGHTS ===
        # Shadow di bawah armor
        for x in range(8, 24):
            temp_surface.set_at((x, 18), gray)
        
        # Highlight di atas armor
        for x in range(9, 23):
            temp_surface.set_at((x, 10), (220, 220, 220))
        
        # Scale ke ukuran akhir
        self._player_surface = pygame.transform.scale(temp_surface, (self._size, self._size))
        
        # === GLOW EFFECT (untuk pixel art) ===
        self._glow_surface = pygame.Surface((self._size + 8, self._size + 8), pygame.SRCALPHA)
        
        # Glow grid pattern (lebih pixelated)
        glow_pattern = [
            (4, 4), (12, 4), (20, 4), (28, 4),
            (4, 12), (28, 12),
            (4, 20), (12, 20), (20, 20), (28, 20),
            (4, 28), (12, 28), (20, 28), (28, 28),
        ]
        
        for gx, gy in glow_pattern:
            # Outer glow (lebih transparan)
            pygame.draw.rect(self._glow_surface, (*blue_energy, 60), 
                            (gx * 2, gy * 2, 8, 8))  # Scale x2
            # Inner glow (lebih terang)
            pygame.draw.rect(self._glow_surface, (*blue_energy, 120), 
                            (gx * 2 + 2, gy * 2 + 2, 4, 4))
        
        # Sword glow khusus
        sword_glow_coords = [(28, 13), (32, 13), (28, 18), (32, 18)]
        for gx, gy in sword_glow_coords:
            pygame.draw.rect(self._glow_surface, (*blue_energy, 100), 
                            (gx * 2, gy * 2, 4, 4))
        
        # === ANIMATION FRAMES (untuk idle animation) ===
        self._idle_frames = []
        
        # Frame 1 (standar)
        frame1 = self._player_surface.copy()
        self._idle_frames.append(frame1)
        
        # Frame 2 (sedikit bergerak - cape dan sword)
        frame2 = self._player_surface.copy()
        
        # Sword sedikit bergerak (animasi sederhana)
        # Karena sudah di-scale, kita skip detail animasi untuk sekarang
        self._idle_frames.append(frame2)
        pixel[0] = min(255, pixel[0] + 20)
        frame2.set_at((x, y), tuple(pixel))
        
        self._idle_frames.append(frame2)
        
        # Frame 3 (kembali ke normal dengan variasi)
        frame3 = self._player_surface.copy()
        
        # Emblem glow berdenyut
        emblem_glow = [(15, 13), (16, 13), (15, 14), (16, 14)]
        for px in emblem_glow:
            frame3.set_at(px, (120, 220, 255))
        
        self._idle_frames.append(frame3)
        
        # Animation properties
        self._current_frame = 0
        self._frame_timer = 0
        self._frame_delay = 0.2  # 5 FPS untuk pixel art
        
        # Set initial surface
        self._player_surface = self._idle_frames[0]

    def update(self, dt: float) -> None:
        """Update dengan animasi pixel art"""
        # Existing update logic...
        
        # Pixel art animation
        self._frame_timer += dt
        if self._frame_timer >= self._frame_delay:
            self._frame_timer = 0
            self._current_frame = (self._current_frame + 1) % len(self._idle_frames)
            self._player_surface = self._idle_frames[self._current_frame]
        
        # Bobbing effect yang lebih halus untuk pixel art
        self._idle_timer += dt
        self._bob_offset = math.sin(self._idle_timer * 1.5) * 1  # Gerakan lebih kecil

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int], 
            particle_system: ParticleSystem) -> None:
        """Draw dengan pixel art style"""
        self._particle_system_ref = particle_system
        
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1] + self._bob_offset)
        
        # Invincibility flicker (pixelated)
        if self._invincible_timer > 0 and int(self._invincible_timer * 8) % 2:
            return
        
        # Draw glow (untuk pixel art, lebih sederhana)
        if self._glow_color and self._glow_timer > 0:
            glow_alpha = int(80 * (self._glow_timer / 3.0))
            glow_temp = self._glow_surface.copy()
            glow_temp.fill((255, 255, 255, glow_alpha), None, pygame.BLEND_RGBA_MULT)
            
            # Pixelated glow positioning
            surface.blit(glow_temp, 
                        (screen_x - 4 + (int(self._bob_offset) % 2),  # Ditambahkan jitter pixel
                        screen_y - 4 + (int(self._idle_timer * 2) % 2)),
                        special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Draw player dengan nearest-neighbor scaling jika diperlukan
        player_rect = pygame.Rect(screen_x, screen_y, self._size, self._size)
        
        # Untuk pixel art, hindari smoothing
        if self._size != 32:  # Jika perlu scaling
            scaled_sprite = pygame.transform.scale(self._player_surface, 
                                                (self._size, self._size))
            surface.blit(scaled_sprite, player_rect.topleft)
        else:
            surface.blit(self._player_surface, player_rect.topleft)
        
        # Trail particles untuk pixel art (lebih jarang)
        if random.random() < 0.08 and (self._vx != 0 or self._vy != 0):
            cx, cy = self.get_center()
            # Particle warna biru energi
            particle_system.emit(cx - 8, cy, (80, 180, 255), 
                            count=1, spread=2, life=0.3, particle_type="sparkle")
    
    # Membuka kemampuan Spirit Lantern
    def unlock_spirit_lantern(self) -> None:
        self._has_spirit_lantern = True
        self._glow_color = COLOR_SPIRIT_CYAN
        self._glow_timer = 3.0
    
    # Memeriksa apakah pemain dapat menyerang
    def can_attack(self) -> bool:
        return self._has_spirit_lantern and self._attack_cooldown <= 0
    
    # Melakukan serangan Spirit Burst
    def attack(self) -> None:
        if not self.can_attack():
            return
        
        self._attack_cooldown = PLAYER_ATTACK_COOLDOWN
        self._attack_flash_timer = 0.1
        
        cx, cy = self.get_center()
        
        dx, dy = self._last_direction
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length
        else:
            dx, dy = 1, 0
        
        self._spirit_bursts.append({
            'x': cx,
            'y': cy,
            'vx': dx * SPIRIT_BURST_SPEED,
            'vy': dy * SPIRIT_BURST_SPEED,
            'life': SPIRIT_BURST_LIFETIME,
            'size': SPIRIT_BURST_SIZE,
            'distance_traveled': 0.0
        })
        
        if self._particle_system_ref:
            self._particle_system_ref.emit(cx, cy, COLOR_SPIRIT_CYAN, 
                                         count=15, spread=40, life=0.5)
    
    # Getter untuk posisi, status, dan inventaris pemain
    def get_position(self) -> Tuple[float, float]:
        return (self._x, self._y)
    
    # Getter untuk posisi tengah pemain
    def get_center(self) -> Tuple[int, int]:
        return (int(self._x + self._size // 2), int(self._y + self._size // 2))
    
    # Getter untuk rect pemain
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self._x), int(self._y), self._size, self._size)
    
    # Getter untuk jumlah nyawa pemain
    def get_lives(self) -> int:
        return self._lives
    
    # Getter untuk skor pemain
    def get_score(self) -> int:
        return self._score
    
    # Getter untuk jumlah permata dalam inventaris
    def get_gem_count(self) -> int:
        return len([item for item in self._inventory if 'gem' in item])
    
    # Getter untuk inventaris pemain
    def get_inventory(self) -> List[str]:
        return self._inventory.copy()
    
    # Memeriksa apakah pemain memiliki permata tertentu
    def has_gem(self, gem_type: str) -> bool:
        return gem_type in self._inventory
    
    # Memeriksa apakah pemain berada di altar
    def is_at_altar(self) -> bool:
        return self._at_altar
    
    # Memeriksa apakah pemain sedang menempatkan permata
    def is_placing_gems(self) -> bool:
        return self._placing_gems
    
    # Menambahkan permata ke inventaris pemain
    def collect_gem(self, gem_type: str, color: Tuple[int, int, int]) -> None:
        self._inventory.append(gem_type)
        self._score += 100
        self._glow_color = color
        self._glow_timer = 3.0
    
    # Menghapus permata dari inventaris pemain
    def remove_gem(self, gem_type: str) -> bool:
        if gem_type in self._inventory:
            self._inventory.remove(gem_type)
            return True
        return False
    
    # Mengurangi nyawa pemain jika tidak dalam keadaan kebal
    def take_damage(self) -> bool:
        if self._invincible_timer <= 0:
            self._lives -= 1
            self._invincible_timer = 2.0
            return True
        return False
    
    # Menangani input pemain untuk pergerakan dan aksi
    def handle_input(self, keys: pygame.key.ScancodeWrapper, dt: float, world_width: int, world_height: int) -> None:
        if self._placing_gems:
            self._vx = 0.0
            self._vy = 0.0
            return
            
        self._vx = 0.0
        self._vy = 0.0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self._vy = -self._speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self._vy = self._speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self._vx = -self._speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self._vx = self._speed
        
        if self._vx != 0 and self._vy != 0:
            self._vx *= 0.707
            self._vy *= 0.707
        
        self._x += self._vx * dt
        self._y += self._vy * dt
        
        self._x = max(0, min(world_width - self._size, self._x))
        self._y = max(0, min(world_height - self._size, self._y))
        
        if self._vx != 0 or self._vy != 0:
            self._idle_timer = 0
            self._last_direction = (self._vx, self._vy)
        
        if keys[pygame.K_SPACE]:
            self.attack()
    
    # Getter untuk daftar Spirit Bursts aktif
    def get_spirit_bursts(self) -> List[dict]:
        return self._spirit_bursts.copy()
    
    # Menghapus Spirit Burst tertentu
    def remove_spirit_burst(self, burst: dict) -> None:
        if burst in self._spirit_bursts:
            self._spirit_bursts.remove(burst)
    
    # Memulai proses penempatan permata di altar
    def start_gem_placement(self) -> None:
        if not self._placing_gems and self.get_gem_count() > 0:
            self._placing_gems = True
            self._gem_placement_timer = 0.0
    
    # Memperbarui status pemain
    def update(self, dt: float) -> None:
        if self._invincible_timer > 0:
            self._invincible_timer -= dt
        
        if self._glow_timer > 0:
            self._glow_timer -= dt
            if self._glow_timer <= 0:
                self._glow_color = None
        
        if self._placing_gems:
            self._gem_placement_timer += dt
            if self._gem_placement_timer >= 2.0:
                self._placing_gems = False
                self._gem_placement_timer = 0.0
        
        self._idle_timer += dt
        self._bob_offset = math.sin(self._idle_timer * 2) * 2
        
        # Update attack system
        if self._attack_cooldown > 0:
            self._attack_cooldown -= dt
        
        if self._attack_flash_timer > 0:
            self._attack_flash_timer -= dt
        
        # Update spirit bursts
        for burst in self._spirit_bursts[:]:
            burst['x'] += burst['vx'] * dt
            burst['y'] += burst['vy'] * dt
            burst['life'] -= dt
            burst['distance_traveled'] += math.sqrt(burst['vx']**2 + burst['vy']**2) * dt
            
            if burst['life'] <= 0 or burst['distance_traveled'] > ATTACK_RANGE:
                self._spirit_bursts.remove(burst)
    
    # Menggambar pemain ke permukaan
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int], 
             particle_system: ParticleSystem) -> None:
        self._particle_system_ref = particle_system
        
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1] + self._bob_offset)
        
        if self._invincible_timer > 0 and int(self._invincible_timer * 10) % 2:
            return
        
        # Draw glow jika ada
        if self._glow_color and self._glow_timer > 0:
            glow_alpha = int(150 * (self._glow_timer / 3.0))
            glow_temp = self._glow_surface.copy()
            glow_temp.fill((*self._glow_color, glow_alpha), None, pygame.BLEND_RGBA_MULT)
            surface.blit(glow_temp, (screen_x - 12, screen_y - 12),
                        special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Trail particles
        if random.random() < 0.15 and (self._vx != 0 or self._vy != 0):
            cx, cy = self.get_center()
            particle_system.emit(cx - 15, cy, COLOR_SPIRIT_CYAN, 
                               count=1, spread=5, life=0.4, particle_type="sparkle")
        
        # Draw player dengan rotasi
        rotated_player = pygame.transform.rotate(self._player_surface, self._rotation)
        player_rect = rotated_player.get_rect(center=(screen_x + self._size//2, 
                                                     screen_y + self._size//2))
        surface.blit(rotated_player, player_rect.topleft)
        
        # Draw placement progress
        if self._placing_gems:
            progress = self._gem_placement_timer / 2.0
            radius = int(24 * progress)
            alpha = int(220 * (1 - abs(progress - 0.5) * 2))
            
            circle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (255, 255, 255, alpha), 
                             (radius, radius), radius, 3)
            
            # Inner rotation
            inner_radius = int(radius * 0.7)
            inner_surf = pygame.Surface((inner_radius * 2, inner_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(inner_surf, (200, 255, 200, alpha//2), 
                             (inner_radius, inner_radius), inner_radius)
            
            # Rotate inner circle
            rotation = self._gem_placement_timer * 180
            rotated_inner = pygame.transform.rotate(inner_surf, rotation)
            inner_rect = rotated_inner.get_rect(center=(radius, radius))
            circle_surf.blit(rotated_inner, inner_rect.topleft)
            
            surface.blit(circle_surf, (screen_x + self._size//2 - radius, 
                                     screen_y + self._size//2 - radius))
        
        # Attack flash
        if self._attack_flash_timer > 0:
            flash_alpha = int(180 * (self._attack_flash_timer / 0.1))
            flash_surf = pygame.Surface((self._size + 24, self._size + 24), pygame.SRCALPHA)
            pygame.draw.rect(flash_surf, (255, 255, 255, flash_alpha),
                           (12, 12, self._size, self._size), border_radius=12)
            surface.blit(flash_surf, (screen_x - 12, screen_y - 12),
                        special_flags=pygame.BLEND_ADD)
        
        # Draw spirit bursts
        for burst in self._spirit_bursts:
            bx = int(burst['x'] - camera_offset[0])
            by = int(burst['y'] - camera_offset[1])
            burst_size = burst['size']
            
            burst_surf = pygame.Surface((burst_size * 4, burst_size * 4), pygame.SRCALPHA)
            
            # Outer glow
            pygame.draw.circle(burst_surf, (100, 220, 255, 120),
                             (burst_size * 2, burst_size * 2), burst_size * 2)
            
            # Middle layer
            pygame.draw.circle(burst_surf, COLOR_SPIRIT_CYAN,
                             (burst_size * 2, burst_size * 2), int(burst_size * 1.5))
            
            # Core
            pygame.draw.circle(burst_surf, (255, 255, 255, 200),
                             (burst_size * 2, burst_size * 2), burst_size // 2)
            
            # Rotation
            rotation = burst['life'] * 360
            rotated_burst = pygame.transform.rotate(burst_surf, rotation)
            burst_rect = rotated_burst.get_rect(center=(bx, by))
            surface.blit(rotated_burst, burst_rect.topleft,
                        special_flags=pygame.BLEND_ADD)
            
            # Trail particles
            if random.random() < 0.4:
                particle_system.emit(burst['x'], burst['y'], COLOR_SPIRIT_CYAN,
                                   count=2, spread=15, life=0.4, particle_type="sparkle")
        
        # Draw cooldown indicator
        if self._has_spirit_lantern and self._attack_cooldown > 0:
            cooldown_ratio = self._attack_cooldown / PLAYER_ATTACK_COOLDOWN
            radius = 10
            indicator_x = screen_x + self._size + 12
            indicator_y = screen_y + 5
            
            # Background
            pygame.draw.circle(surface, (40, 40, 40, 200), (indicator_x, indicator_y), radius)
            
            if cooldown_ratio < 1.0:
                # Progress arc
                angle = 360 * (1 - cooldown_ratio)
                arc_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.arc(arc_surf, (*COLOR_SPIRIT_CYAN, 200),
                              (0, 0, radius * 2, radius * 2),
                              math.radians(-90), math.radians(-90 + angle), 3)
                surface.blit(arc_surf, (indicator_x - radius, indicator_y - radius))
            
            # Border
            pygame.draw.circle(surface, COLOR_WHITE, (indicator_x, indicator_y), radius, 2)
            
            # Center dot
            pygame.draw.circle(surface, COLOR_SPIRIT_CYAN, (indicator_x, indicator_y), 2)


# ==================== COMPANION ====================
class Companion:
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
        self._size = COMPANION_SIZE
        self._follow_speed = COMPANION_FOLLOW_SPEED
        self._bob_timer = 0.0
        self._hint_text = ""
        self._hint_timer = 0.0
        self._hint_cooldown = 0.0
        self._glow_timer = 0.0
        
        self._idle_at_altar = False
        self._altar_position: Optional[Tuple[float, float]] = None
    
    # Getter untuk posisi dan rect companion
    def get_position(self) -> Tuple[float, float]:
        return (self._x, self._y)
    
    # Getter untuk rect companion
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self._x), int(self._y), self._size, self._size)
    
    # Metode untuk memberikan petunjuk kepada pemain
    def can_give_hint(self) -> bool:
        return self._hint_cooldown <= 0
    
    # Memberikan petunjuk kepada pemain
    def give_hint(self, text: str) -> None:
        if self.can_give_hint():
            self._hint_text = text
            self._hint_timer = 3.0
            self._hint_cooldown = 5.0
            self._glow_timer = 2.0
    
    # Mengikuti pemain
    def follow_player(self, player: Player) -> None:
        if self._idle_at_altar and self._altar_position:
            target_x = self._altar_position[0] + 60
            target_y = self._altar_position[1]
        else:
            px, py = player.get_position()
            target_x = px - 40
            target_y = py
        
        self._x += (target_x - self._x) * self._follow_speed
        self._y += (target_y - self._y) * self._follow_speed
    
    # Menetapkan status idle di altar
    def set_altar_idle(self, altar_x: float, altar_y: float) -> None:
        self._idle_at_altar = True
        self._altar_position = (altar_x, altar_y)
    
    # Menghapus status idle di altar
    def update(self, dt: float) -> None:
        if self._hint_timer > 0:
            self._hint_timer -= dt
        if self._hint_cooldown > 0:
            self._hint_cooldown -= dt
        if self._glow_timer > 0:
            self._glow_timer -= dt
        
        self._bob_timer += dt * 3
    
    # Menggambar companion ke permukaan
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1])
        bob = math.sin(self._bob_timer) * 2
        
        if self._glow_timer > 0:
            glow_alpha = int(100 * (self._glow_timer / 2.0))
            glow_surf = pygame.Surface((self._size + 16, self._size + 16), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*COLOR_GEM_YELLOW, glow_alpha), 
                             (self._size // 2 + 8, self._size // 2 + 8), self._size // 2 + 8)
            surface.blit(glow_surf, (screen_x - 8, screen_y - 8 + bob))
        
        center_x = screen_x + self._size // 2
        center_y = int(screen_y + self._size // 2 + bob)
        pygame.draw.circle(surface, COLOR_HONEY_BROWN, (center_x, center_y), self._size // 2)
        pygame.draw.circle(surface, (100, 70, 30), (center_x, center_y), self._size // 2, 2)
        
        ear_offset = math.sin(self._bob_timer) * 2
        pygame.draw.circle(surface, COLOR_HONEY_BROWN, (center_x - 8, int(center_y - 10 + ear_offset)), 5)
        pygame.draw.circle(surface, COLOR_HONEY_BROWN, (center_x + 8, int(center_y - 10 + ear_offset)), 5)
        
        pygame.draw.circle(surface, COLOR_BLACK, (center_x - 5, center_y - 2), 2)
        pygame.draw.circle(surface, COLOR_BLACK, (center_x + 5, center_y - 2), 2)
        pygame.draw.circle(surface, COLOR_BLACK, (center_x, center_y + 4), 2)
        
        if self._hint_timer > 0:
            font = pygame.font.Font(None, 18)
            hint_surf = font.render(self._hint_text, True, COLOR_BLACK)
            hint_rect = hint_surf.get_rect(center=(center_x, center_y - 25))
            
            bubble_rect = hint_rect.inflate(12, 8)
            pygame.draw.rect(surface, COLOR_WHITE, bubble_rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_BLACK, bubble_rect, 2, border_radius=8)
            
            points = [
                (center_x - 4, center_y - 10),
                (center_x + 4, center_y - 10),
                (center_x, center_y - 2)
            ]
            pygame.draw.polygon(surface, COLOR_WHITE, points)
            pygame.draw.lines(surface, COLOR_BLACK, False, points, 2)
            
            surface.blit(hint_surf, hint_rect)

class MentorCompanion(Companion):  # Inherit from existing Companion class
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.mentor_activated = False
        self.mentor_particles = []
        self.mentor_wisdom_timer = 0.0
        self.current_wisdom = ""
        self.aura_timer = 0.0
        
        # Wisdom database based on game events
        self.wisdom_database = {
            "enemy_encounter": [
                "Mereka berasal dari sumber yang sama, namun bertindak berbeda.",
                "Warisan bentuk berbeda, namun inti sama.",
                "Satu kelas, banyak wujud - seperti INHERITANCE."
            ],
            "damage_taken": [
                "Kekuatan harus dijaga, tidak boleh sembarang digunakan.",
                "Attribut dalam harus dilindungi - ENCAPSULATION.",
                "Akses terbatas mencegah kerusakan."
            ],
            "gem_collected": [
                "Cahaya ini tersimpan rapi, seperti kekuatan dalam diri.",
                "Getter dan Setter menjaga integritas.",
                "ENCAPSULATION: menyembunyikan kompleksitas."
            ],
            "portal_approach": [
                "Semua pengetahuan telah kau kumpulkan.",
                "ENCAPSULATION, INHERITANCE, POLYMORPHISM.",
                "Perjalanan OOP telah kau kuasai."
            ],
            "attack_used": [
                "Satu method, banyak efek - POLYMORPHISM.",
                "Interface sama, implementasi berbeda.",
                "take_action() dipanggil, hasil beragam."
            ],
            "level_complete": [
                "Tahap demi tahap, konsep terkuak.",
                "Dari ENCAPSULATION menuju POLYMORPHISM.",
                "Perjalanan OOP adalah perjalanan pencerahan."
            ]
        }
    
    def activate_mentor(self) -> None:
        """Activate mentor mode after world map"""
        self.mentor_activated = True
        self._size = 32  # Slightly larger when mentor
        self._glow_timer = 5.0  # Initial glow
    
    def give_wisdom(self, event_type: str) -> None:
        """Give contextual wisdom based on game event"""
        if not self.mentor_activated:
            return
            
        if event_type in self.wisdom_database:
            wisdom_list = self.wisdom_database[event_type]
            self.current_wisdom = random.choice(wisdom_list)
            self.mentor_wisdom_timer = 4.0  # Show for 4 seconds
            self._hint_timer = 4.0
            self._hint_text = self.current_wisdom
            
            # Add mentor particles
            cx, cy = self._x + self._size // 2, self._y + self._size // 2
            for _ in range(10):
                self.mentor_particles.append({
                    'x': cx,
                    'y': cy,
                    'vx': random.uniform(-20, 20),
                    'vy': random.uniform(-30, -10),
                    'life': 1.0,
                    'color': (255, 255, 200)
                })
    
    def update(self, dt: float) -> None:
        super().update(dt)
        
        if self.mentor_activated:
            self.aura_timer += dt
            
            # Update mentor particles
            for p in self.mentor_particles[:]:
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt
                p['vy'] += 50 * dt  # Gravity
                p['life'] -= dt
                
                if p['life'] <= 0:
                    self.mentor_particles.remove(p)
            
            # Add new aura particles
            if random.random() < 0.3:
                cx, cy = self._x + self._size // 2, self._y + self._size // 2
                angle = random.uniform(0, math.pi * 2)
                radius = self._size // 2 + 10
                self.mentor_particles.append({
                    'x': cx + math.cos(angle) * radius,
                    'y': cy + math.sin(angle) * radius,
                    'vx': math.cos(angle + math.pi/2) * 10,
                    'vy': math.sin(angle + math.pi/2) * 10,
                    'life': 2.0,
                    'color': (255, 255, 200, 150)
                })
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        # Draw mentor particles
        if self.mentor_activated:
            for p in self.mentor_particles:
                if p['life'] > 0:
                    alpha = int(255 * (p['life'] / 2.0))
                    x = int(p['x'] - camera_offset[0])
                    y = int(p['y'] - camera_offset[1])
                    
                    glow_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*p['color'][:3], alpha), (4, 4), 4)
                    surface.blit(glow_surf, (x - 4, y - 4))
        
        # Draw mentor aura
        if self.mentor_activated and self.aura_timer > 0:
            screen_x = int(self._x - camera_offset[0])
            screen_y = int(self._y - camera_offset[1])
            bob = math.sin(self._bob_timer) * 2
            
            # Pulsing aura
            pulse = (math.sin(self.aura_timer * 2) + 1) * 0.3 + 0.7
            aura_size = int(self._size * pulse)
            aura_surf = pygame.Surface((aura_size + 30, aura_size + 30), pygame.SRCALPHA)
            
            # Multiple aura layers
            for i in range(3, 0, -1):
                layer_size = aura_size + i * 10
                layer_alpha = int(40 / i * pulse)
                pygame.draw.circle(aura_surf, (*COLOR_MENTOR_AURA[:3], layer_alpha), 
                                 (aura_size//2 + 15, aura_size//2 + 15), layer_size//2)
            
            surface.blit(aura_surf, (screen_x - 15, screen_y - 15 + bob))
        
        # Call parent draw method
        super().draw(surface, camera_offset)
        
        # Draw special mentor hint
        if self.mentor_activated and self.mentor_wisdom_timer > 0:
            # Removed mentor text box as requested
            font = pygame.font.Font(None, 22)
            wisdom_lines = self._wrap_text(self.current_wisdom, 380, font)
            for i, line in enumerate(wisdom_lines):
                wisdom_text = font.render(line, True, (220, 255, 220))
                wisdom_rect = wisdom_text.get_rect(center=(surface.get_width()//2, 
                                                          surface.get_height() - 75 + i * 25))
                surface.blit(wisdom_text, wisdom_rect)
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            test_width = font.size(test_line)[0]
            
            if test_width > max_width:
                if len(current_line) == 1:
                    lines.append(test_line)
                    current_line = []
                else:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

# ==================== ENEMIES ====================
class Enemy:
    def __init__(self, x: float, y: float, enemy_type: str):
        self._x = x
        self._y = y
        self._vx = 0.0
        self._vy = 0.0
        self._size = ENEMY_SIZE
        self._type = enemy_type
        self._speed = ENEMY_PATROL_SPEED
        self._alert_timer = 0.0
        self._health = 1
    
    # Getter untuk posisi, rect, dan status kesehatan musuh
    def get_position(self) -> Tuple[float, float]:
        return (self._x, self._y)
    
    # Getter untuk rect musuh
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self._x), int(self._y), self._size, self._size)
    
    # Getter untuk kesehatan musuh
    def get_health(self) -> int:
        return self._health
    
    # Metode untuk menerima damage
    def take_damage(self, damage: int = 1) -> bool:
        self._health -= damage
        return self._health <= 0
    
    # Memeriksa tabrakan dengan rect tertentu
    def collides_with(self, rect: pygame.Rect) -> bool:
        return self.get_rect().colliderect(rect)
    
    # Metode abstrak untuk tindakan musuh
    def take_action(self, player: Player, dt: float) -> None:
        pass
    
    # Memperbarui posisi musuh
    def update(self, dt: float, world_width: int, world_height: int) -> None:
        self._x += self._vx * dt
        self._y += self._vy * dt
        
        self._x = max(0, min(world_width - self._size, self._x))
        self._y = max(0, min(world_height - self._size, self._y))
        
        if self._alert_timer > 0:
            self._alert_timer -= dt
    
    # Metode abstrak untuk menggambar musuh
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        pass


class GlimpEnemy(Enemy):
    def __init__(self, x: float, y: float, waypoints: List[Tuple[float, float]]):
        super().__init__(x, y, "glimp")
        self._waypoints = waypoints
        self._current_waypoint = 0
        self._wobble_timer = 0.0

    def take_action(self, player: Player, dt: float) -> None:
        target = self._waypoints[self._current_waypoint]
        dx = target[0] - self._x
        dy = target[1] - self._y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist < 5:
            self._current_waypoint = (self._current_waypoint + 1) % len(self._waypoints)
        elif dist > 0:
            self._vx = (dx / dist) * self._speed
            self._vy = (dy / dist) * self._speed
        
        px, py = player.get_position()
        player_dist = math.sqrt((px - self._x) ** 2 + (py - self._y) ** 2)
        if player_dist < 100:
            self._alert_timer = 0.5
        
        self._wobble_timer += dt * 4
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1])
        wobble = math.sin(self._wobble_timer) * 2
        
        if self._alert_timer > 0:
            glow_alpha = int(120 * (self._alert_timer / 0.5))
            glow_surf = pygame.Surface((self._size + 12, self._size + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 80, 80, glow_alpha),
                           (6, 6, self._size, self._size), border_radius=10)
            surface.blit(glow_surf, (screen_x - 6, screen_y - 6 + wobble))
        
        enemy_rect = pygame.Rect(screen_x, int(screen_y + wobble), self._size, self._size)
        pygame.draw.rect(surface, (255, 80, 80), enemy_rect, border_radius=10)
        
        eye_x = screen_x + self._size // 2
        eye_y = int(screen_y + self._size // 2 + wobble)
        eye_size = 10 if self._alert_timer > 0 else 8
        pygame.draw.circle(surface, COLOR_WHITE, (eye_x, eye_y), eye_size)
        pupil_size = 6 if self._alert_timer > 0 else 4
        pygame.draw.circle(surface, COLOR_BLACK, (eye_x, eye_y), pupil_size)


class UmbraEnemy(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "umbra")
        self._aggro_range = 150
        self._stretch_factor = 1.0
        self._trail_particles: List[dict] = []

    def take_action(self, player: Player, dt: float) -> None:
        px, py = player.get_position()
        dx = px - self._x
        dy = py - self._y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist < self._aggro_range and dist > 0:
            self._vx = (dx / dist) * ENEMY_CHASE_SPEED
            self._vy = (dy / dist) * ENEMY_CHASE_SPEED
            self._stretch_factor = 1.2
            self._alert_timer = 0.3
            
            if random.random() < 0.3:
                self._trail_particles.append({
                    'x': self._x + self._size // 2,
                    'y': self._y + self._size // 2,
                    'life': 0.5
                })
        else:
            self._vx = 0
            self._vy = 0
            self._stretch_factor = 1.0
        
        for p in self._trail_particles[:]:
            p['life'] -= dt
            if p['life'] <= 0:
                self._trail_particles.remove(p)
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1])
        
        for p in self._trail_particles:
            alpha = int(150 * (p['life'] / 0.5))
            trail_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*COLOR_SHADOW_PURPLE, alpha), (4, 4), 4)
            surface.blit(trail_surf, (int(p['x'] - camera_offset[0] - 4), 
                                    int(p['y'] - camera_offset[1] - 4)))
        
        if self._alert_timer > 0:
            glow_surf = pygame.Surface((self._size + 12, self._size + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*COLOR_SHADOW_PURPLE, 100),
                           (6, 6, self._size, self._size), border_radius=8)
            surface.blit(glow_surf, (screen_x - 6, screen_y - 6))
        
        stretch_w = int(self._size * self._stretch_factor)
        stretch_x = screen_x - (stretch_w - self._size) // 2
        pygame.draw.rect(surface, COLOR_SHADOW_PURPLE,
                        (stretch_x, screen_y, stretch_w, self._size), border_radius=8)
        
        left_eye = (stretch_x + stretch_w // 3, screen_y + self._size // 2)
        right_eye = (stretch_x + 2 * stretch_w // 3, screen_y + self._size // 2)
        pygame.draw.circle(surface, COLOR_GEM_YELLOW, left_eye, 4)
        pygame.draw.circle(surface, COLOR_GEM_YELLOW, right_eye, 4)
        pygame.draw.circle(surface, (255, 80, 80), left_eye, 2)
        pygame.draw.circle(surface, (255, 80, 80), right_eye, 2)


class FlareWolfEnemy(Enemy):
    def __init__(self, x: float, y: float, waypoints: List[Tuple[float, float]]):
        super().__init__(x, y, "flare_wolf")
        self._waypoints = waypoints
        self._current_waypoint = 0
        self._zigzag_timer = 0.0
        self._dash_cooldown = 0.0
        self._dashing = False
        self._dash_timer = 0.0
        self._dash_direction = (0.0, 0.0)
        self._trail_particles: List[dict] = []
        self._health = 2

    def take_damage(self, damage: int = 1) -> bool:
        self._health -= damage
        if self._dashing:
            self._dashing = False
            self._speed = ENEMY_PATROL_SPEED
            self._dash_cooldown = 1.0
        return self._health <= 0
    
    def take_action(self, player: Player, dt: float) -> None:
        px, py = player.get_position()
        player_dist = math.sqrt((px - self._x) ** 2 + (py - self._y) ** 2)
        
        if not self._dashing and self._dash_cooldown <= 0 and player_dist < 200:
            self._dashing = True
            self._dash_timer = 0.3
            self._dash_cooldown = 2.0
            
            dx = px - self._x
            dy = py - self._y
            dist = max(0.1, math.sqrt(dx * dx + dy * dy))
            self._dash_direction = (dx / dist, dy / dist)
            
            self._speed = ENEMY_CHASE_SPEED * 1.5
        
        if self._dashing:
            self._dash_timer -= dt
            self._vx = self._dash_direction[0] * self._speed
            self._vy = self._dash_direction[1] * self._speed
            
            if random.random() < 0.5:
                self._trail_particles.append({
                    'x': self._x + self._size // 2,
                    'y': self._y + self._size // 2,
                    'life': 0.6,
                    'size': random.randint(2, 4)
                })
            
            if self._dash_timer <= 0:
                self._dashing = False
                self._speed = ENEMY_PATROL_SPEED
        else:
            self._dash_cooldown -= dt
            
            self._zigzag_timer += dt * 3
            zigzag_offset = math.sin(self._zigzag_timer) * 20
            
            target = self._waypoints[self._current_waypoint]
            dx = target[0] - self._x
            dy = target[1] - self._y + zigzag_offset
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < 10:
                self._current_waypoint = (self._current_waypoint + 1) % len(self._waypoints)
            elif dist > 0:
                self._vx = (dx / dist) * self._speed
                self._vy = (dy / dist) * self._speed
        
        if player_dist < 150:
            self._alert_timer = 0.5
        
        for p in self._trail_particles[:]:
            p['life'] -= dt
            if p['life'] <= 0:
                self._trail_particles.remove(p)
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1])
        
        for p in self._trail_particles:
            alpha = int(200 * (p['life'] / 0.6))
            size = p['size']
            trail_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            pygame.draw.circle(trail_surf, (255, 200, 0, alpha), (size, size), size)
            pygame.draw.circle(trail_surf, (255, 100, 0, alpha//2), (size, size), size//2)
            
            surface.blit(trail_surf, (int(p['x'] - camera_offset[0] - size), 
                                    int(p['y'] - camera_offset[1] - size)))
        
        if self._alert_timer > 0 or self._dashing:
            glow_color = (255, 100, 0) if self._dashing else (255, 80, 80)
            glow_alpha = 150 if self._dashing else int(120 * (self._alert_timer / 0.5))
            glow_surf = pygame.Surface((self._size + 16, self._size + 16), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*glow_color, glow_alpha),
                           (8, 8, self._size, self._size), border_radius=12)
            surface.blit(glow_surf, (screen_x - 8, screen_y - 8))
        
        wolf_rect = pygame.Rect(screen_x, screen_y, self._size, self._size)
        body_color = (255, 140, 0) if self._dashing else COLOR_FLARE_WOLF
        pygame.draw.rect(surface, body_color, wolf_rect, border_radius=8)
        pygame.draw.rect(surface, (200, 80, 0), wolf_rect, width=2, border_radius=8)
        
        ear_y = screen_y + 5
        pygame.draw.polygon(surface, body_color, [
            (screen_x + 5, ear_y),
            (screen_x + 15, screen_y - 5),
            (screen_x + 10, ear_y)
        ])
        pygame.draw.polygon(surface, body_color, [
            (screen_x + 20, ear_y),
            (screen_x + 25, screen_y - 5),
            (screen_x + 25, ear_y)
        ])
        
        left_eye = (screen_x + 10, screen_y + 12)
        right_eye = (screen_x + 20, screen_y + 12)
        eye_size = 4 if self._dashing else 3
        pygame.draw.circle(surface, COLOR_GEM_YELLOW, left_eye, eye_size + 1)
        pygame.draw.circle(surface, COLOR_GEM_YELLOW, right_eye, eye_size + 1)
        pygame.draw.circle(surface, (255, 50, 50), left_eye, eye_size - 1)
        pygame.draw.circle(surface, (255, 50, 50), right_eye, eye_size - 1)


class ForestGuardianEnemy(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "forest_guardian")
        self._size = MINI_BOSS_SIZE
        self._health = 3
        self._attack_timer = 0.0
        self._attack_cooldown = 3.0
        self._charging_attack = False
        self._charge_timer = 0.0
        self._projectiles: List[dict] = []
        self._rune_glow_timer = 0.0
        self._hit_flash_timer = 0.0
    
    def take_damage(self, damage: int = 1) -> bool:
        self._health -= damage
        self._hit_flash_timer = 0.1
        
        if self._health == 2:
            self._attack_cooldown = 2.5
        elif self._health == 1:
            self._attack_cooldown = 2.0
            self._speed = ENEMY_PATROL_SPEED * 0.9
        
        return self._health <= 0
    
    def update(self, dt: float, world_width: int, world_height: int) -> None:
        super().update(dt, world_width, world_height)
        if self._hit_flash_timer > 0:
            self._hit_flash_timer -= dt
    
    def take_action(self, player: Player, dt: float) -> None:
        px, py = player.get_position()
        dx = px - self._x
        dy = py - self._y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 100 and not self._charging_attack:
            if dist > 0:
                self._vx = (dx / dist) * (ENEMY_PATROL_SPEED * 0.7)
                self._vy = (dy / dist) * (ENEMY_PATROL_SPEED * 0.7)
        else:
            self._vx = 0
            self._vy = 0
        
        self._attack_timer += dt
        if self._attack_timer >= self._attack_cooldown and dist < 300:
            self._charging_attack = True
            self._charge_timer = 1.0
            self._attack_timer = 0
        
        if self._charging_attack:
            self._charge_timer -= dt
            self._rune_glow_timer = 0.5
            
            if self._charge_timer <= 0:
                if dist > 0:
                    proj_dx = dx / dist
                    proj_dy = dy / dist
                    self._projectiles.append({
                        'x': self._x + self._size // 2,
                        'y': self._y + self._size // 2,
                        'vx': proj_dx * 100,
                        'vy': proj_dy * 100,
                        'life': 3.0,
                        'size': 12
                    })
                self._charging_attack = False
                self._attack_cooldown = random.uniform(2.5, 4.0)
        
        for proj in self._projectiles[:]:
            proj['x'] += proj['vx'] * dt
            proj['y'] += proj['vy'] * dt
            proj['life'] -= dt
            if proj['life'] <= 0:
                self._projectiles.remove(proj)
        
        if self._rune_glow_timer > 0:
            self._rune_glow_timer -= dt
        
        self._alert_timer = 0.3
    
    def get_projectiles(self) -> List[dict]:
        return self._projectiles.copy()
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1])
        
        body_rect = pygame.Rect(screen_x, screen_y, self._size, self._size)
        pygame.draw.rect(surface, (47, 74, 42), body_rect, border_radius=10)
        pygame.draw.rect(surface, (35, 55, 31), body_rect, width=3, border_radius=10)
        
        rune_alpha = int(200 * (self._rune_glow_timer / 0.5)) if self._rune_glow_timer > 0 else 80
        rune_color = (100, 255, 200, rune_alpha)
        
        if rune_alpha > 0:
            rune_surf = pygame.Surface((self._size, self._size), pygame.SRCALPHA)
            pygame.draw.polygon(rune_surf, rune_color, [
                (10, 15), (20, 10), (30, 15), (20, 30)
            ])
            pygame.draw.circle(rune_surf, rune_color, (20, 20), 5)
            surface.blit(rune_surf, (screen_x, screen_y))
        
        left_eye = (screen_x + 15, screen_y + 15)
        right_eye = (screen_x + 25, screen_y + 15)
        eye_glow = 8 if self._charging_attack else 6
        
        for eye in [left_eye, right_eye]:
            glow_surf = pygame.Surface((eye_glow * 2, eye_glow * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 255, 200, 150), 
                             (eye_glow, eye_glow), eye_glow)
            surface.blit(glow_surf, (eye[0] - eye_glow, eye[1] - eye_glow))
        
        pygame.draw.circle(surface, (50, 200, 150), left_eye, 4)
        pygame.draw.circle(surface, (50, 200, 150), right_eye, 4)
        
        for proj in self._projectiles:
            proj_x = int(proj['x'] - camera_offset[0])
            proj_y = int(proj['y'] - camera_offset[1])
            proj_size = proj['size']
            alpha = int(200 * (proj['life'] / 3.0))
            
            proj_surf = pygame.Surface((proj_size * 2, proj_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(proj_surf, (100, 255, 255, alpha), 
                             (proj_size, proj_size), proj_size)
            pygame.draw.circle(proj_surf, (255, 255, 255, alpha), 
                             (proj_size, proj_size), proj_size // 2)
            surface.blit(proj_surf, (proj_x - proj_size, proj_y - proj_size))
        
        health_bar_width = 40
        health_bar_height = 6
        health_ratio = self._health / 3.0
        
        bar_x = screen_x + (self._size - health_bar_width) // 2
        bar_y = screen_y - 10
        
        pygame.draw.rect(surface, (50, 50, 50), 
                        (bar_x, bar_y, health_bar_width, health_bar_height))
        pygame.draw.rect(surface, (100, 255, 100), 
                        (bar_x, bar_y, int(health_bar_width * health_ratio), health_bar_height))




# ==================== TILEMAP ====================
class TileMap:
    def __init__(self, width: int, height: int, level: Level = Level.LEVEL_1):
        self.width = width
        self.height = height
        self.tile_size = TILE_SIZE
        self.tiles_x = width // self.tile_size
        self.tiles_y = height // self.tile_size
        self.level = level
        
        self.base_layer = pygame.Surface((width, height))
        self.objects_below_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.objects_above_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        
        self._generate_tilemap()
    
    def _generate_tilemap(self) -> None:
        if self.level == Level.LEVEL_2:
            self._generate_level2()
        elif self.level == Level.LEVEL_3:
            self._generate_level3()
        else:
            self._generate_level1()
    
    def _generate_level1(self) -> None:
        """Enhanced Spirit Forest tiles"""
        # Create tile variations
        grass_colors = [
            (140, 180, 140),    # Light green
            (130, 170, 130),    # Medium green
            (120, 160, 120),    # Dark green
            (150, 190, 150),    # Bright green
        ]
        
        flower_colors = [
            (255, 200, 200),    # Pink
            (200, 220, 255),    # Blue
            (255, 255, 200),    # Yellow
            (220, 200, 255),    # Purple
        ]
        
        for y in range(self.tiles_y):
            for x in range(self.tiles_x):
                # Checkerboard pattern with noise
                noise = (x * 73 + y * 97) % 20
                base_idx = ((x + y) % 2 + (noise > 15)) % len(grass_colors)
                color = grass_colors[base_idx]
                
                # Add subtle texture
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                 self.tile_size, self.tile_size)
                pygame.draw.rect(self.base_layer, color, rect)
                
                # Texture dots
                if noise < 3:
                    dot_size = 2
                    dot_x = x * self.tile_size + self.tile_size // 4
                    dot_y = y * self.tile_size + self.tile_size // 4
                    pygame.draw.circle(self.base_layer, 
                                     (color[0] - 20, color[1] - 20, color[2] - 20),
                                     (dot_x, dot_y), dot_size)
                
                if noise > 17:
                    dot_size = 1
                    dot_x = x * self.tile_size + 3 * self.tile_size // 4
                    dot_y = y * self.tile_size + 3 * self.tile_size // 4
                    pygame.draw.circle(self.base_layer, 
                                     (color[0] + 20, color[1] + 20, color[2] + 20),
                                     (dot_x, dot_y), dot_size)
        
        # Enhanced objects
        for _ in range(25):
            x = random.randint(0, self.width - 60)
            y = random.randint(0, self.height - 60)
            
            # Fallen logs dengan texture
            log_length = random.randint(30, 50)
            log_width = random.randint(12, 18)
            
            # Log shadow
            pygame.draw.ellipse(self.objects_below_layer, (80, 60, 40, 150),
                              (x + 4, y + 24, log_length, log_width))
            
            # Log main
            pygame.draw.ellipse(self.objects_below_layer, (100, 80, 60),
                              (x, y + 20, log_length, log_width))
            
            # Log texture lines
            for i in range(3):
                line_y = y + 20 + log_width // 2 + (i - 1) * 3
                pygame.draw.line(self.objects_below_layer, (80, 60, 40),
                               (x + 5, line_y), (x + log_length - 5, line_y), 1)
        
        # Flowers and plants
        for _ in range(40):
            x = random.randint(0, self.width - 40)
            y = random.randint(0, self.height - 40)
            flower_type = random.choice(["small", "medium", "large"])
            flower_color = random.choice(flower_colors)
            
            if flower_type == "small":
                # Small flower cluster
                for _ in range(3):
                    fx = x + random.randint(0, 20)
                    fy = y + random.randint(0, 20)
                    pygame.draw.circle(self.objects_above_layer, (*flower_color, 180),
                                     (fx, fy), 4)
                    pygame.draw.circle(self.objects_above_layer, (255, 255, 255, 100),
                                     (fx, fy), 2)
            elif flower_type == "medium":
                # Medium flower dengan leaves
                pygame.draw.circle(self.objects_above_layer, (*flower_color, 200),
                                 (x + 10, y + 10), 8)
                pygame.draw.circle(self.objects_above_layer, (255, 255, 255, 150),
                                 (x + 10, y + 10), 4)
                
                # Leaves
                leaf_color = (100, 180, 100, 150)
                leaf_points = [
                    (x + 5, y + 15),
                    (x + 10, y + 5),
                    (x + 15, y + 15)
                ]
                pygame.draw.polygon(self.objects_above_layer, leaf_color, leaf_points)
            else:
                # Large flower dengan stem
                stem_color = (80, 140, 80, 200)
                pygame.draw.line(self.objects_above_layer, stem_color,
                               (x + 10, y + 25), (x + 10, y + 10), 3)
                
                # Flower petals
                petal_colors = [flower_color, 
                              (max(0, min(255, flower_color[0] + 20)), max(0, min(255, flower_color[1] + 20)), max(0, min(255, flower_color[2] + 20)), 200),
                              (max(0, min(255, flower_color[0] - 20)), max(0, min(255, flower_color[1] - 20)), max(0, min(255, flower_color[2] - 20)), 200)]
                
                for i, pcolor in enumerate(petal_colors):
                    angle = i * 120 * math.pi / 180
                    px = x + 10 + math.cos(angle) * 10
                    py = y + 10 + math.sin(angle) * 10
                    pygame.draw.circle(self.objects_above_layer, pcolor, (int(px), int(py)), 6)
                
                # Center
                pygame.draw.circle(self.objects_above_layer, (255, 240, 200, 220),
                                 (x + 10, y + 10), 4)
    
    def _generate_level2(self) -> None:
        """Enhanced Crimson Mountain tiles"""
        # Base terrain colors
        rock_colors = [
            (130, 90, 70),    # Light brown
            (110, 75, 55),    # Medium brown
            (90, 60, 40),     # Dark brown
            (120, 85, 65),    # Reddish brown
        ]
        
        lava_colors = [
            (255, 100, 50),   # Bright orange
            (255, 80, 40),    # Medium orange
            (255, 60, 30),    # Dark orange
            (220, 120, 60),   # Yellow-orange
        ]
        
        for y in range(self.tiles_y):
            for x in range(self.tiles_x):
                # Volcanic terrain dengan noise
                noise = (x * 67 + y * 89) % 30
                base_idx = ((x // 2 + y // 2) % 2 + (noise > 20)) % len(rock_colors)
                color = rock_colors[base_idx]
                
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                 self.tile_size, self.tile_size)
                pygame.draw.rect(self.base_layer, color, rect)
                
                # Crack textures
                if noise < 5:
                    crack_color = (color[0] - 30, color[1] - 30, color[2] - 30)
                    start_x = x * self.tile_size + random.randint(2, self.tile_size - 2)
                    start_y = y * self.tile_size + random.randint(2, self.tile_size - 2)
                    end_x = start_x + random.randint(-8, 8)
                    end_y = start_y + random.randint(-8, 8)
                    pygame.draw.line(self.base_layer, crack_color,
                                   (start_x, start_y), (end_x, end_y), 1)
                
                # Lava patches
                if noise > 25:
                    patch_size = random.randint(4, 8)
                    patch_x = x * self.tile_size + random.randint(4, self.tile_size - patch_size - 4)
                    patch_y = y * self.tile_size + random.randint(4, self.tile_size - patch_size - 4)
                    patch_color = random.choice(lava_colors)
                    
                    # Lava glow
                    glow_surf = pygame.Surface((patch_size + 4, patch_size + 4), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*patch_color, 80),
                                     (patch_size//2 + 2, patch_size//2 + 2), patch_size//2 + 2)
                    self.base_layer.blit(glow_surf, (patch_x - 2, patch_y - 2))
                    
                    # Lava core
                    pygame.draw.circle(self.base_layer, patch_color,
                                     (patch_x + patch_size//2, patch_y + patch_size//2),
                                     patch_size//2)
        
        # Burnt trees
        for _ in range(20):
            x = random.randint(0, self.width - 80)
            y = random.randint(0, self.height - 100)
            
            # Tree trunk dengan char effect
            trunk_width = random.randint(14, 22)
            trunk_height = random.randint(30, 50)
            trunk_x = x + (60 - trunk_width) // 2
            trunk_y = y + 30
            
            # Trunk shadow
            pygame.draw.rect(self.objects_below_layer, (60, 40, 30, 150),
                           (trunk_x + 3, trunk_y + 3, trunk_width, trunk_height),
                           border_radius=4)
            
            # Trunk main
            trunk_color = COLOR_BURNT_BROWN
            pygame.draw.rect(self.objects_below_layer, trunk_color,
                           (trunk_x, trunk_y, trunk_width, trunk_height),
                           border_radius=4)
            
            # Char marks
            for _ in range(random.randint(2, 5)):
                mark_x = trunk_x + random.randint(2, trunk_width - 2)
                mark_y = trunk_y + random.randint(5, trunk_height - 5)
                mark_width = random.randint(2, 4)
                pygame.draw.line(self.objects_below_layer, (40, 25, 15),
                               (mark_x, mark_y), (mark_x + mark_width, mark_y), 2)
            
            # Dead canopy
            if random.random() < 0.8:
                canopy_radius = random.randint(18, 28)
                canopy_x = x + 30
                canopy_y = y + 20
                
                # Canopy layers
                canopy_colors = [(50, 35, 25, 180), (60, 40, 30, 150), (70, 45, 35, 120)]
                for i, ccolor in enumerate(canopy_colors):
                    layer_radius = canopy_radius - i * 4
                    pygame.draw.circle(self.objects_below_layer, ccolor,
                                     (canopy_x, canopy_y), layer_radius)
        
        # Volcanic rocks
        for _ in range(15):
            x = random.randint(0, self.width - 80)
            y = random.randint(0, self.height - 60)
            rock_size = random.randint(25, 45)
            
            # Rock shadow
            shadow_surf = pygame.Surface((rock_size + 6, rock_size + 6), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100),
                              (3, 3, rock_size, rock_size))
            self.objects_below_layer.blit(shadow_surf, (x - 3, y - 3))
            
            # Rock main
            rock_color = (90, 70, 60)
            pygame.draw.ellipse(self.objects_above_layer, rock_color,
                              (x, y, rock_size, rock_size))
            
            # Rock highlights
            highlight_color = (110, 90, 80)
            highlight_size = rock_size // 2
            highlight_x = x + rock_size // 4
            highlight_y = y + rock_size // 4
            pygame.draw.ellipse(self.objects_above_layer, highlight_color,
                              (highlight_x, highlight_y, highlight_size, highlight_size))
            
            # Rock cracks
            for _ in range(random.randint(2, 4)):
                crack_start = (x + random.randint(5, rock_size - 5),
                             y + random.randint(5, rock_size - 5))
                crack_end = (crack_start[0] + random.randint(-10, 10),
                           crack_start[1] + random.randint(-10, 10))
                pygame.draw.line(self.objects_above_layer, (60, 45, 35),
                               crack_start, crack_end, 1)
    
    def _generate_level3(self) -> None:
        """Enhanced Castle tiles"""
        # Marble floor colors
        marble_colors = [
            (160, 160, 170),  # Light gray
            (150, 150, 160),  # Medium gray
            (140, 140, 150),  # Dark gray
            (170, 170, 180),  # Blue-gray
        ]
        
        gold_color = (210, 180, 80)
        
        for y in range(self.tiles_y):
            for x in range(self.tiles_x):
                # Marble floor dengan veins
                noise = (x * 71 + y * 113) % 25
                base_idx = ((x // 3 + y // 3) % 2 + (noise > 18)) % len(marble_colors)
                color = marble_colors[base_idx]
                
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                 self.tile_size, self.tile_size)
                pygame.draw.rect(self.base_layer, color, rect)
                
                # Marble veins
                if noise < 8:
                    vein_color = (color[0] + 20, color[1] + 20, color[2] + 20)
                    vein_width = random.randint(1, 2)
                    
                    # Vertical vein
                    if noise % 2 == 0:
                        vein_x = x * self.tile_size + self.tile_size // 2
                        start_y = y * self.tile_size + random.randint(2, self.tile_size // 3)
                        end_y = start_y + random.randint(self.tile_size // 2, self.tile_size - 4)
                        pygame.draw.line(self.base_layer, vein_color,
                                       (vein_x, start_y), (vein_x, end_y), vein_width)
                    
                    # Horizontal vein
                    else:
                        vein_y = y * self.tile_size + self.tile_size // 2
                        start_x = x * self.tile_size + random.randint(2, self.tile_size // 3)
                        end_x = start_x + random.randint(self.tile_size // 2, self.tile_size - 4)
                        pygame.draw.line(self.base_layer, vein_color,
                                       (start_x, vein_y), (end_x, vein_y), vein_width)
                
                # Gold inlays
                if noise > 22:
                    inlay_size = random.randint(4, 8)
                    inlay_x = x * self.tile_size + random.randint(4, self.tile_size - inlay_size - 4)
                    inlay_y = y * self.tile_size + random.randint(4, self.tile_size - inlay_size - 4)
                    
                    # Gold glow
                    glow_surf = pygame.Surface((inlay_size + 6, inlay_size + 6), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*gold_color, 60),
                                     (inlay_size//2 + 3, inlay_size//2 + 3), inlay_size//2 + 3)
                    self.base_layer.blit(glow_surf, (inlay_x - 3, inlay_y - 3))
                    
                    # Gold circle
                    pygame.draw.circle(self.base_layer, gold_color,
                                     (inlay_x + inlay_size//2, inlay_y + inlay_size//2),
                                     inlay_size//2)
        
        # Castle structure
        castle_w = min(800, self.width - 200)
        castle_h = min(480, self.height - 200)
        castle_x = (self.width - castle_w) // 2
        castle_y = (self.height - castle_h) // 2
        
        # Castle walls dengan detail
        wall_color = (140, 140, 150)
        wall_shade = (120, 120, 130)
        wall_highlight = (160, 160, 170)
        
        # Main wall body
        wall_rect = pygame.Rect(castle_x, castle_y, castle_w, castle_h)
        pygame.draw.rect(self.objects_below_layer, wall_color, wall_rect)
        
        # Wall shading
        pygame.draw.rect(self.objects_below_layer, wall_shade, wall_rect, 6)
        
        # Wall highlights
        highlight_rect = pygame.Rect(castle_x + 4, castle_y + 4, 
                                   castle_w - 8, castle_h - 8)
        pygame.draw.rect(self.objects_below_layer, wall_highlight, 
                        highlight_rect, 2)
        
        # Battlements
        battlement_w = 26
        for bx in range(castle_x, castle_x + castle_w, battlement_w * 2):
            # Battlement shadow
            pygame.draw.rect(self.objects_above_layer, (0, 0, 0, 100),
                           (bx + 2, castle_y - 12 + 2, battlement_w, 12))
            
            # Battlement main
            battlement_rect = pygame.Rect(bx, castle_y - 12, battlement_w, 12)
            pygame.draw.rect(self.objects_above_layer, wall_shade, battlement_rect)
            
            # Battlement highlight
            pygame.draw.rect(self.objects_above_layer, (180, 180, 190),
                           (bx + 2, castle_y - 10, battlement_w - 4, 8))
            
            # Arrow slit
            slit_color = (60, 60, 70)
            slit_x = bx + battlement_w // 2
            pygame.draw.rect(self.objects_above_layer, slit_color,
                           (slit_x - 2, castle_y - 8, 4, 6))
        
        # Enhanced towers
        tower_radius = 44
        towers = [
            (castle_x - tower_radius + 8, castle_y - tower_radius + 8),
            (castle_x + castle_w - 8 - tower_radius, castle_y - tower_radius + 8),
            (castle_x - tower_radius + 8, castle_y + castle_h - 8 - tower_radius),
            (castle_x + castle_w - 8 - tower_radius, castle_y + castle_h - 8 - tower_radius)
        ]
        
        for tx, ty in towers:
            # Tower shadow
            shadow_surf = pygame.Surface((tower_radius * 2 + 6, tower_radius * 2 + 6), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 120),
                              (3, 3, tower_radius * 2, tower_radius * 2))
            self.objects_below_layer.blit(shadow_surf, (tx - 3, ty - 3))
            
            # Tower main
            pygame.draw.ellipse(self.objects_below_layer, wall_color, 
                              (tx, ty, tower_radius * 2, tower_radius * 2))
            
            # Tower shading
            pygame.draw.ellipse(self.objects_below_layer, wall_shade,
                              (tx, ty, tower_radius * 2, tower_radius * 2), 4)
            
            # Tower battlements
            for i in range(6):
                rx = tx + i * (tower_radius * 2 // 6)
                batt_w = tower_radius * 2 // 7
                
                # Battlement shadow
                pygame.draw.rect(self.objects_above_layer, (0, 0, 0, 100),
                               (rx + 1, ty - 14 + 1, batt_w, 14))
                
                # Battlement
                pygame.draw.rect(self.objects_above_layer, wall_shade,
                               (rx, ty - 14, batt_w, 14))
                
                # Battlement highlight
                pygame.draw.rect(self.objects_above_layer, (180, 180, 190),
                               (rx + 2, ty - 12, batt_w - 4, 10))
            
            # Flag pole
            pole_x = tx + tower_radius
            pole_y = ty - 22
            pole_color = (80, 60, 40)
            
            # Pole shadow
            pygame.draw.line(self.objects_above_layer, (0, 0, 0, 100),
                           (pole_x + 1, pole_y + 1), (pole_x + 1, pole_y - 32 + 1), 4)
            
            # Pole main
            pygame.draw.line(self.objects_above_layer, pole_color,
                           (pole_x, pole_y), (pole_x, pole_y - 32), 4)
            
            # Flag dengan animasi
            flag_wave = math.sin(pygame.time.get_ticks() * 0.001) * 2
            flag_points = [
                (pole_x, pole_y - 30),
                (pole_x + 20 + flag_wave, pole_y - 26),
                (pole_x, pole_y - 22)
            ]
            
            # Flag shadow
            shadow_points = [(p[0] + 1, p[1] + 1) for p in flag_points]
            pygame.draw.polygon(self.objects_above_layer, (0, 0, 0, 100), shadow_points)
            
            # Flag main
            pygame.draw.polygon(self.objects_above_layer, (200, 40, 40), flag_points)
            
            # Flag detail
            pygame.draw.line(self.objects_above_layer, (240, 240, 240),
                           (pole_x + 4, pole_y - 28), (pole_x + 16, pole_y - 26), 1)
        
        # Enhanced entrance
        entrance_w = 150
        entrance_h = 170
        ent_x = castle_x + (castle_w - entrance_w) // 2
        ent_y = castle_y + castle_h - entrance_h
        
        # Entrance arch shadow
        arch_shadow = pygame.Surface((entrance_w + 6, entrance_h + 6), pygame.SRCALPHA)
        pygame.draw.arc(arch_shadow, (0, 0, 0, 150),
                       (3, 3, entrance_w, entrance_h), math.pi, 2*math.pi, 10)
        self.objects_above_layer.blit(arch_shadow, (ent_x - 3, ent_y - 3))
        
        # Entrance arch
        pygame.draw.arc(self.objects_above_layer, (100, 100, 110),
                       (ent_x, ent_y, entrance_w, entrance_h), math.pi, 2*math.pi, 8)
        
        # Entrance door
        door_rect = pygame.Rect(ent_x + 25, ent_y + entrance_h//2, 
                               entrance_w - 50, entrance_h//2)
        
        # Door shadow
        pygame.draw.rect(self.objects_below_layer, (20, 20, 20, 200), door_rect)
        
        # Door main
        door_color = (80, 60, 40)
        pygame.draw.rect(self.objects_below_layer, door_color, door_rect)
        
        # Door details
        door_knob_x = ent_x + entrance_w - 40
        door_knob_y = ent_y + entrance_h - 60
        pygame.draw.circle(self.objects_below_layer, (180, 160, 100),
                         (door_knob_x, door_knob_y), 6)
        
        # Door panels
        for i in range(2):
            panel_x = ent_x + 40 + i * 50
            panel_rect = pygame.Rect(panel_x, ent_y + entrance_h - 80, 40, 60)
            pygame.draw.rect(self.objects_below_layer, 
                           (door_color[0] - 20, door_color[1] - 20, door_color[2] - 20),
                           panel_rect, 2)
        
        # Windows dengan stained glass effect
        win_w, win_h = 32, 44
        stained_colors = [
            (200, 60, 60, 180),    # Red
            (60, 200, 60, 180),    # Green
            (60, 60, 200, 180),    # Blue
            (200, 200, 60, 180),   # Yellow
        ]
        
        for wy in range(castle_y + 50, castle_y + castle_h - 100, 90):
            for wx in range(castle_x + 40, castle_x + castle_w - 40, 130):
                if wx + win_w < castle_x + castle_w:
                    # Window frame shadow
                    pygame.draw.rect(self.objects_above_layer, (0, 0, 0, 150),
                                   (wx + 2, wy + 2, win_w, win_h))
                    
                    # Window frame
                    pygame.draw.rect(self.objects_above_layer, (60, 50, 40),
                                   (wx, wy, win_w, win_h))
                    
                    # Stained glass
                    glass_x = wx + 4
                    glass_y = wy + 6
                    glass_w = win_w - 8
                    glass_h = win_h - 12
                    
                    # Glass segments
                    segment_w = glass_w // 2
                    segment_h = glass_h // 2
                    
                    for sy in range(2):
                        for sx in range(2):
                            seg_x = glass_x + sx * segment_w
                            seg_y = glass_y + sy * segment_h
                            seg_color = random.choice(stained_colors)
                            
                            # Glass segment
                            seg_surf = pygame.Surface((segment_w, segment_h), pygame.SRCALPHA)
                            seg_surf.fill(seg_color)
                            
                            # Glass highlight
                            highlight = pygame.Surface((segment_w, segment_h), pygame.SRCALPHA)
                            pygame.draw.rect(highlight, (255, 255, 255, 60),
                                           (0, 0, segment_w, segment_h), 1)
                            pygame.draw.line(highlight, (255, 255, 255, 40),
                                           (segment_w//2, 0), (segment_w//2, segment_h))
                            pygame.draw.line(highlight, (255, 255, 255, 40),
                                           (0, segment_h//2), (segment_w, segment_h//2))
                            
                            seg_surf.blit(highlight, (0, 0))
                            self.objects_below_layer.blit(seg_surf, (seg_x, seg_y))
                    
                    # Window arch
                    arch_rect = pygame.Rect(wx, wy - 8, win_w, win_h // 2)
                    pygame.draw.arc(self.objects_above_layer, (80, 70, 50),
                                   arch_rect, math.pi, 2*math.pi, 4)
                    
                    # Window arch highlight
                    highlight_rect = pygame.Rect(wx + 2, wy - 6, win_w - 4, win_h // 2 - 4)
                    pygame.draw.arc(self.objects_above_layer, (180, 160, 140),
                                   highlight_rect, math.pi, 2*math.pi, 2)
        
        # Pathway dengan cobblestones
        path_w = 140
        path_x = ent_x + (entrance_w - path_w)//2
        path_y = ent_y + entrance_h
        
        stone_colors = [(100, 100, 100), (110, 110, 110), (90, 90, 90), (120, 120, 120)]
        
        for i in range(150):
            stone_y = path_y + i * 10
            if stone_y > self.height:
                break
            
            # Row of stones
            for j in range(path_w // 12):
                stone_x = path_x + j * 12 + (i % 2) * 6
                stone_color = random.choice(stone_colors)
                
                # Stone shadow
                pygame.draw.circle(self.objects_below_layer, (0, 0, 0, 100),
                                 (stone_x + 6, stone_y + 2), 4)
                
                # Stone
                pygame.draw.circle(self.objects_below_layer, stone_color,
                                 (stone_x + 5, stone_y), 4)
                
                # Stone highlight
                pygame.draw.circle(self.objects_below_layer, 
                                 (stone_color[0] + 20, stone_color[1] + 20, stone_color[2] + 20),
                                 (stone_x + 5, stone_y - 1), 2)
        
        # Enhanced torches
        torch_offsets = [(-30, 50), (entrance_w + 4, 50)]
        
        for ox, oy in torch_offsets:
            tx = ent_x + entrance_w//2 + ox
            ty = ent_y + oy
            
            # Torch pole shadow
            pygame.draw.rect(self.objects_above_layer, (0, 0, 0, 150),
                           (tx + 1, ty + 1, 8, 28))
            
            # Torch pole
            pole_gradient = pygame.Surface((8, 28), pygame.SRCALPHA)
            for py in range(28):
                alpha = 255 - py * 8
                pygame.draw.line(pole_gradient, (100, 80, 60, alpha),
                               (0, py), (8, py))
            self.objects_above_layer.blit(pole_gradient, (tx, ty))
            
            # Torch bracket
            bracket_y = ty - 4
            pygame.draw.rect(self.objects_above_layer, (80, 60, 40),
                           (tx - 2, bracket_y, 12, 4))
            
            # Flame
            flame_size = 18
            flame_x = tx + 4
            flame_y = ty - 12
            
            # Flame glow
            glow_surf = pygame.Surface((flame_size * 2, flame_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 200, 100, 80),
                             (flame_size, flame_size), flame_size)
            self.objects_above_layer.blit(glow_surf, (flame_x - flame_size, flame_y - flame_size),
                                         special_flags=pygame.BLEND_ADD)
            
            # Flame core
            flame_points = [
                (flame_x, flame_y - 8),
                (flame_x + 6, flame_y),
                (flame_x, flame_y + 12),
                (flame_x - 6, flame_y)
            ]
            pygame.draw.polygon(self.objects_above_layer, (255, 180, 60), flame_points)
            
            # Flame highlight
            highlight_points = [
                (flame_x, flame_y - 6),
                (flame_x + 4, flame_y),
                (flame_x, flame_y + 8),
                (flame_x - 4, flame_y)
            ]
            pygame.draw.polygon(self.objects_above_layer, (255, 220, 140), highlight_points)
        
        # Enhanced altar
        altar_x = castle_x + castle_w//2 - 70
        altar_y = castle_y + castle_h//2 - 70
        altar_size = 140
        
        # Altar shadow
        altar_shadow = pygame.Surface((altar_size + 10, altar_size + 10), pygame.SRCALPHA)
        pygame.draw.rect(altar_shadow, (0, 0, 0, 100),
                        (5, 5, altar_size, altar_size), border_radius=15)
        self.objects_below_layer.blit(altar_shadow, (altar_x - 5, altar_y - 5))
        
        # Altar base
        altar_base = pygame.Surface((altar_size, altar_size), pygame.SRCALPHA)
        
        # Altar gradient
        for y in range(altar_size):
            ratio = y / altar_size
            r = int(230 * (1 - ratio) + 200 * ratio)
            g = int(220 * (1 - ratio) + 180 * ratio)
            b = int(200 * (1 - ratio) + 150 * ratio)
            alpha = 240
            pygame.draw.line(altar_base, (r, g, b, alpha), (0, y), (altar_size, y))
        
        # Altar border
        pygame.draw.rect(altar_base, (180, 160, 140), 
                        (0, 0, altar_size, altar_size), width=6, border_radius=15)
        
        # Altar inner border
        pygame.draw.rect(altar_base, (200, 180, 160), 
                        (4, 4, altar_size - 8, altar_size - 8), width=2, border_radius=11)
        
        # Altar center glow
        center_size = 44
        center_x = altar_size // 2 - center_size // 2
        center_y = altar_size // 2 - center_size // 2
        
        # Center glow
        center_glow = pygame.Surface((center_size, center_size), pygame.SRCALPHA)
        pygame.draw.circle(center_glow, (255, 240, 200, 100),
                         (center_size//2, center_size//2), center_size//2)
        altar_base.blit(center_glow, (center_x, center_y),
                       special_flags=pygame.BLEND_ADD)
        
        # Center circle
        pygame.draw.circle(altar_base, (255, 240, 180),
                         (altar_size//2, altar_size//2), center_size//2 - 4)
        
        # Center highlight
        pygame.draw.circle(altar_base, (255, 255, 220),
                         (altar_size//2, altar_size//2), center_size//2 - 8)
        
        self.objects_below_layer.blit(altar_base, (altar_x, altar_y))
    
    def get_altar_position(self) -> Optional[Tuple[int, int]]:
        if self.level == Level.LEVEL_3:
            castle_w = min(800, self.width - 200)
            castle_h = min(480, self.height - 200)
            castle_x = (self.width - castle_w) // 2
            castle_y = (self.height - castle_h) // 2
            altar_size = 140
            return (castle_x + castle_w//2 - altar_size//2, 
                    castle_y + castle_h//2 - altar_size//2)
        return None
    
    def draw_base(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        surface.blit(self.base_layer, (-camera_offset[0], -camera_offset[1]))
    
    def draw_objects_below(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        surface.blit(self.objects_below_layer, (-camera_offset[0], -camera_offset[1]))
    
    def draw_objects_above(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        surface.blit(self.objects_above_layer, (-camera_offset[0], -camera_offset[1]))


# ==================== COLLECTIBLES ====================
class Gem:
    def __init__(self, x: float, y: float, gem_type: str, color: Tuple[int, int, int]):
        self._x = x
        self._y = y
        self._type = gem_type
        self._color = color
        self._size = GEM_SIZE
        self._collected = False
        self._pulse_timer = 0.0
        self._pulse_scale = 1.0
        
        self._floating_to_altar = False
        self._altar_target: Optional[Tuple[float, float]] = None
        self._float_speed = 100.0
        self._float_timer = 0.0
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self._x), int(self._y), self._size, self._size)
    
    def get_center(self) -> Tuple[int, int]:
        return (int(self._x + self._size // 2), int(self._y + self._size // 2))
    
    def get_position(self) -> Tuple[float, float]:
        return (self._x, self._y)
    
    def is_collected(self) -> bool:
        return self._collected
    
    def is_floating(self) -> bool:
        return self._floating_to_altar
    
    def collect(self) -> Tuple[str, Tuple[int, int, int]]:
        self._collected = True
        return (self._type, self._color)
    
    def start_floating_to_altar(self, altar_x: float, altar_y: float) -> None:
        self._floating_to_altar = True
        self._altar_target = (altar_x, altar_y)
        self._float_timer = 0.0
    
    def update(self, dt: float) -> None:
        if self._floating_to_altar and self._altar_target:
            self._float_timer += dt
            dx = self._altar_target[0] - self._x
            dy = self._altar_target[1] - self._y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 5:
                self._x += (dx / dist) * self._float_speed * dt
                self._y += (dy / dist) * self._float_speed * dt
                
                self._pulse_timer += dt * 3
                self._pulse_scale = 1.0 + math.sin(self._pulse_timer) * 0.3
            else:
                self._floating_to_altar = False
        elif not self._collected:
            self._pulse_timer += dt * 2
            self._pulse_scale = 1.0 + math.sin(self._pulse_timer) * 0.2
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int], particle_system: ParticleSystem) -> None:
        if self._collected and not self._floating_to_altar:
            return
        
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1])
        
        if random.random() < 0.05:
            cx, cy = self.get_center()
            if self._floating_to_altar:
                particle_system.emit(cx, cy, self._color, count=2, spread=20, life=0.8)
            else:
                particle_system.emit(cx, cy, self._color, count=1, spread=10, life=0.5)
        
        glow_size = int(self._size * self._pulse_scale)
        glow_surf = pygame.Surface((glow_size + 20, glow_size + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self._color, 80), 
                         (glow_size // 2 + 10, glow_size // 2 + 10), glow_size // 2 + 10)
        surface.blit(glow_surf, (screen_x - 10, screen_y - 10))
        
        center_x = screen_x + self._size // 2
        center_y = screen_y + self._size // 2
        points = [
            (center_x, center_y - 10),
            (center_x + 10, center_y),
            (center_x, center_y + 10),
            (center_x - 10, center_y)
        ]
        pygame.draw.polygon(surface, COLOR_WHITE, points, width=2)
        
        inner_points = [
            (center_x, center_y - 8),
            (center_x + 8, center_y),
            (center_x, center_y + 8),
            (center_x - 8, center_y)
        ]
        pygame.draw.polygon(surface, self._color, inner_points)


class Portal:
    def __init__(self, x: float, y: float, portal_type: str = "default", target_level: Optional[Level] = None):
        self._x = x
        self._y = y
        self._size = PORTAL_SIZE
        self._pulse_timer = 0.0
        self._swirl_timer = 0.0
        self._active = True
        self._portal_type = portal_type
        self._target_level = target_level
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self._x), int(self._y), self._size, self._size)
    
    def get_type(self) -> str:
        return self._portal_type
    
    def get_target_level(self) -> Optional[Level]:
        return self._target_level
    
    def update(self, dt: float, player: Player) -> None:
        self._pulse_timer += dt * 2
        self._swirl_timer += dt * 3
        
        px, py = player.get_position()
        dist = math.sqrt((px - self._x) ** 2 + (py - self._y) ** 2)
        if dist < 80:
            self._pulse_timer += dt * 4
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int], particle_system: ParticleSystem) -> None:
        if not self._active:
            return
        
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1])
        center_x = screen_x + self._size // 2
        center_y = screen_y + self._size // 2
        
        pulse = math.sin(self._pulse_timer) * 0.1 + 1.0
        
        if self._portal_type == "red":
            portal_color = (255, 80, 80)
            particle_color = (255, 140, 100)
        elif self._portal_type == "victory":
            portal_color = (255, 255, 100)
            particle_color = (255, 255, 150)
        else:
            portal_color = (100, 200, 255)
            particle_color = COLOR_SPIRIT_CYAN
        
        if random.random() < 0.2:
            angle = random.uniform(0, math.pi * 2)
            radius = self._size // 2
            px = center_x + math.cos(angle) * radius
            py = center_y + math.sin(angle) * radius
            particle_system.emit(px, py, particle_color, count=1, spread=20, life=1.0)
        
        for i in range(3, 0, -1):
            radius = int(self._size * 0.6 * pulse + i * 8)
            alpha = 100 - i * 30
            glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*portal_color, alpha), 
                             (radius, radius), radius)
            surface.blit(glow_surf, (center_x - radius, center_y - radius))
        
        portal_rect = pygame.Rect(screen_x, screen_y, self._size, self._size)
        pygame.draw.rect(surface, portal_color, portal_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_WHITE, portal_rect, width=3, border_radius=12)
        
        swirl_radius = self._size // 2 - 8
        for i in range(4):
            angle = self._swirl_timer + i * math.pi / 2
            sx = center_x + math.cos(angle) * swirl_radius * 0.7
            sy = center_y + math.sin(angle) * swirl_radius * 0.7
            dot_size = int(6 + math.sin(self._swirl_timer * 2 + i) * 2)
            pygame.draw.circle(surface, portal_color, (int(sx), int(sy)), dot_size)
        
        font = pygame.font.Font(None, 20)
        if self._portal_type == "red":
            text = "LEVEL 2"
        elif self._portal_type == "victory":
            text = "CASTLE"
        else:
            text = "EXIT"
        
        text_surf = font.render(text, True, COLOR_BLACK)
        text_rect = text_surf.get_rect(center=(center_x, center_y))
        surface.blit(text_surf, text_rect)


class SpiritAltar:
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
        self._size = 120
        self._activated = False
        self._activation_timer = 0.0
        self._gems_placed = 0
        self._gem_positions: List[Tuple[float, float]] = []
        self._tree_growth_timer = 0.0
        self._tree_visible = False
        self._tree_height = 0.0
        
        center_x = x + self._size // 2
        center_y = y + self._size // 2
        radius = 50
        for i in range(3):
            angle = i * 120 * math.pi / 180
            gem_x = center_x + math.cos(angle) * radius
            gem_y = center_y + math.sin(angle) * radius
            self._gem_positions.append((gem_x, gem_y))
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self._x - 20), int(self._y - 20), 
                          self._size + 40, self._size + 40)
    
    def get_center(self) -> Tuple[int, int]:
        return (int(self._x + self._size // 2), int(self._y + self._size // 2))
    
    def is_activated(self) -> bool:
        return self._activated
    
    def place_gem(self) -> bool:
        if self._gems_placed < 3:
            self._gems_placed += 1
            
            if self._gems_placed >= 3:
                self._activated = True
                self._activation_timer = 0.0
                return True
        return False
    
    def get_gem_position(self, gem_index: int) -> Optional[Tuple[float, float]]:
        if 0 <= gem_index < len(self._gem_positions):
            return self._gem_positions[gem_index]
        return None
    
    def update(self, dt: float) -> None:
        if self._activated:
            self._activation_timer += dt
            
            if self._activation_timer > 1.0 and not self._tree_visible:
                self._tree_visible = True
                self._tree_growth_timer = 0.0
            
            if self._tree_visible:
                self._tree_growth_timer += dt
                self._tree_height = min(1.0, self._tree_growth_timer / 3.0)
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int], particle_system: ParticleSystem) -> None:
        screen_x = int(self._x - camera_offset[0])
        screen_y = int(self._y - camera_offset[1])
        center_x = screen_x + self._size // 2
        center_y = screen_y + self._size // 2
        
        if self._activated:
            pulse = (math.sin(self._activation_timer * 3) + 1) * 0.5
            glow_radius = int(self._size * 0.8 + pulse * 40)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_alpha = int(100 + pulse * 80)
            pygame.draw.circle(glow_surf, (100, 255, 200, glow_alpha), 
                             (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius))
        
        for i in range(self._gems_placed):
            gem_pos = self._gem_positions[i]
            gem_x = int(gem_pos[0] - camera_offset[0])
            gem_y = int(gem_pos[1] - camera_offset[1])
            
            gem_glow = pygame.Surface((40, 40), pygame.SRCALPHA)
            pulse = (math.sin(self._activation_timer * 4 + i) + 1) * 0.5
            glow_alpha = int(150 + pulse * 105)
            
            if i == 0:
                gem_color = (100, 255, 100, glow_alpha)
            elif i == 1:
                gem_color = (100, 200, 255, glow_alpha)
            else:
                gem_color = (255, 255, 100, glow_alpha)
            
            pygame.draw.circle(gem_glow, gem_color, (20, 20), 20)
            surface.blit(gem_glow, (gem_x - 20, gem_y - 20))
            
            if random.random() < 0.1:
                particle_system.emit(gem_pos[0], gem_pos[1], gem_color[:3], 
                                   count=1, spread=15, life=0.7, particle_type="light_flower")
        
        if self._tree_visible:
            tree_height = int(200 * self._tree_height)
            tree_width = int(80 * self._tree_height)
            
            trunk_color = (150, 120, 80)
            trunk_rect = pygame.Rect(center_x - tree_width//4, 
                                   center_y - tree_height + 20,
                                   tree_width//2, tree_height)
            pygame.draw.rect(surface, trunk_color, trunk_rect, border_radius=tree_width//4)
            
            canopy_layers = 3
            for layer in range(canopy_layers):
                layer_y = center_y - tree_height + 20 - layer * 20
                layer_radius = int(tree_width * 0.6 * (1 - layer * 0.2))
                layer_alpha = int(180 * (1 - layer * 0.3) * self._tree_height)
                
                canopy_surf = pygame.Surface((layer_radius * 2, layer_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(canopy_surf, (100, 255, 200, layer_alpha), 
                                 (layer_radius, layer_radius), layer_radius)
                surface.blit(canopy_surf, (center_x - layer_radius, layer_y - layer_radius))
            
            if random.random() < 0.2:
                blossom_x = center_x + random.randint(-40, 40)
                blossom_y = center_y - tree_height + random.randint(50, 100)
                particle_system.emit(blossom_x, blossom_y, (200, 255, 220), 
                                   count=3, spread=30, life=1.5, particle_type="light_flower")


# ==================== UI ====================
class UI:
    @staticmethod
    def draw_hud(surface: pygame.Surface, player: Player, elapsed_time: float, current_level: Level) -> None:
        # Enhanced HUD panel with better layout
        panel_width = 230
        panel_height = 150
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Glass effect background
        pygame.draw.rect(panel_surf, (0, 0, 0, 140), (0, 0, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(panel_surf, (120, 200, 255, 80), (0, 0, panel_width, panel_height), 3, border_radius=15)
        
        # Inner glow
        inner_glow = pygame.Surface((panel_width - 20, panel_height - 20), pygame.SRCALPHA)
        pygame.draw.rect(inner_glow, (255, 255, 255, 25), (0, 0, panel_width - 20, panel_height - 20), border_radius=12)
        panel_surf.blit(inner_glow, (10, 10))
        
        surface.blit(panel_surf, (20, 20))
        
        # Fonts
        font_title = pygame.font.Font(None, 24)
        font_text = pygame.font.Font(None, 20)
        
        # Level
        level_text = font_title.render(f"LEVEL {current_level.value}", True, COLOR_GEM_YELLOW)
        surface.blit(level_text, (35, 35))
        
        # Lives
        lives_y = 65
        lives_text = font_text.render("LIVES:", True, (220, 220, 220))
        surface.blit(lives_text, (35, lives_y))

        # Pixel art heart colors
        heart_red = (255, 90, 90)        # Main red
        heart_dark_red = (200, 60, 60)   # Dark red for shading
        heart_light_red = (255, 130, 130) # Light red for highlight
        heart_outline = (80, 30, 30)     # Outline color
        heart_glow = (255, 120, 120, 60) # Glow color with alpha

        # Heart size and spacing
        heart_size = 18  # Pixel size for each heart
        heart_spacing = 28

        for i in range(3):
            heart_x = 105 + i * heart_spacing
            
            if i < player.get_lives():
                # === FULL HEART - Detailed Pixel Art dengan bentuk lebih realistis ===
                
                # 1. Outer glow effect (pulsing)
                pulse = (math.sin(pygame.time.get_ticks() * 0.003 + i) + 1) * 0.3 + 0.7
                glow_size = int(heart_size * pulse)
                glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                
                # Glow layers
                for layer in range(3, 0, -1):
                    layer_size = glow_size - layer * 2
                    layer_alpha = 40 // (layer + 1)
                    # Draw pixelated glow (diamond shape)
                    for gy in range(layer_size):
                        for gx in range(layer_size):
                            # Diamond mask
                            if abs(gx - layer_size//2) + abs(gy - layer_size//2) <= layer_size//2:
                                glow_surf.set_at((gx + layer, gy + layer), (*heart_red[:3], layer_alpha))
                
                surface.blit(glow_surf, (heart_x - glow_size//2, lives_y - glow_size//2 + 2))
                
                # 2. Main heart shape (9x8 pixel grid) - bentuk heart yang lebih realistis
                heart_pixels = [
                    # Row 0 (dua lobus atas terpisah)
                    (1, 0, heart_red), (2, 0, heart_red), (5, 0, heart_red), (6, 0, heart_red),
                    
                    # Row 1 (lobus membesar)
                    (0, 1, heart_red), (1, 1, heart_red), (2, 1, heart_red), (3, 1, heart_red), 
                    (4, 1, heart_red), (5, 1, heart_red), (6, 1, heart_red), (7, 1, heart_red),
                    
                    # Row 2 (lebar penuh)
                    (0, 2, heart_red), (1, 2, heart_red), (2, 2, heart_red), (3, 2, heart_red), 
                    (4, 2, heart_red), (5, 2, heart_red), (6, 2, heart_red), (7, 2, heart_red),
                    
                    # Row 3 (mulai menyempit)
                    (0, 3, heart_red), (1, 3, heart_red), (2, 3, heart_red), (3, 3, heart_red), 
                    (4, 3, heart_red), (5, 3, heart_red), (6, 3, heart_red), (7, 3, heart_red),
                    
                    # Row 4 (menyempit)
                    (1, 4, heart_red), (2, 4, heart_red), (3, 4, heart_red), (4, 4, heart_red), 
                    (5, 4, heart_red), (6, 4, heart_red),
                    
                    # Row 5 (lebih sempit)
                    (2, 5, heart_red), (3, 5, heart_red), (4, 5, heart_red), (5, 5, heart_red),
                    
                    # Row 6 (menuju titik)
                    (3, 6, heart_red), (4, 6, heart_red),
                    
                    # Row 7 (titik bawah)
                    (3, 7, heart_red), (4, 7, heart_red),
                    
                    # Row 8 (ujung lancip)
                    (4, 8, heart_red),
                ]
                
                # 3. Heart shading (darker pixels on left/bottom)
                shading_pixels = [
                    # Left lobe shading
                    (0, 1, heart_dark_red), (1, 1, heart_dark_red),
                    (0, 2, heart_dark_red), (1, 2, heart_dark_red),
                    (0, 3, heart_dark_red), (1, 3, heart_dark_red),
                    (1, 4, heart_dark_red), (2, 4, heart_dark_red),
                    (2, 5, heart_dark_red), (3, 5, heart_dark_red),
                    (3, 6, heart_dark_red), (3, 7, heart_dark_red),
                    (4, 8, heart_dark_red),
                ]
                
                # 4. Heart highlights (lighter pixels on right/top)
                highlight_pixels = [
                    # Right lobe highlights
                    (6, 0, heart_light_red), (5, 0, heart_light_red),
                    (7, 1, heart_light_red), (6, 1, heart_light_red),
                    (7, 2, heart_light_red), (6, 2, heart_light_red),
                    (7, 3, heart_light_red), (6, 3, heart_light_red),
                    (6, 4, heart_light_red), (5, 4, heart_light_red),
                    (5, 5, heart_light_red), (4, 6, heart_light_red),
                ]
                
                # 5. Draw all heart pixels (scaled up)
                pixel_size = 2  # Scale factor
                
                # Draw main heart shape
                for px, py, color in heart_pixels:
                    pygame.draw.rect(surface, color, 
                                (heart_x + px * pixel_size, 
                                    lives_y + py * pixel_size, 
                                    pixel_size, pixel_size))
                
                # Overlay shading
                for px, py, color in shading_pixels:
                    pygame.draw.rect(surface, color, 
                                (heart_x + px * pixel_size, 
                                    lives_y + py * pixel_size, 
                                    pixel_size, pixel_size))
                
                # Overlay highlights
                for px, py, color in highlight_pixels:
                    pygame.draw.rect(surface, color, 
                                (heart_x + px * pixel_size, 
                                    lives_y + py * pixel_size, 
                                    pixel_size, pixel_size))
                
                # 6. Outline (pixelated outline)
                outline_pixels = [
                    # Top outline (dua lobus)
                    (0, 0, heart_outline), (1, -1, heart_outline), (2, -1, heart_outline), (3, 0, heart_outline),
                    (4, 0, heart_outline), (5, -1, heart_outline), (6, -1, heart_outline), (7, 0, heart_outline),
                    
                    # Left side
                    (-1, 1, heart_outline), (-1, 2, heart_outline), (-1, 3, heart_outline),
                    (0, 4, heart_outline), (1, 5, heart_outline), (2, 6, heart_outline),
                    (2, 7, heart_outline), (3, 8, heart_outline),
                    
                    # Right side
                    (8, 1, heart_outline), (8, 2, heart_outline), (8, 3, heart_outline),
                    (7, 4, heart_outline), (6, 5, heart_outline), (5, 6, heart_outline),
                    (5, 7, heart_outline), (5, 8, heart_outline),
                    
                    # Bottom point
                    (4, 9, heart_outline),
                ]
                
                # Draw outline (1 pixel thick)
                for px, py, color in outline_pixels:
                    draw_x = heart_x + px * pixel_size
                    draw_y = lives_y + py * pixel_size
                    pygame.draw.rect(surface, color, 
                                (draw_x, draw_y, pixel_size, pixel_size))
                
                # 7. Inner glow (for beating effect)
                beat = abs(math.sin(pygame.time.get_ticks() * 0.005 + i * 1.5))
                inner_glow_alpha = int(100 * beat)
                
                if inner_glow_alpha > 20:
                    # Center glow pixels
                    center_pixels = [(3, 2), (4, 2), (3, 3), (4, 3), (3, 4), (4, 4)]
                    for cx, cy in center_pixels:
                        glow_rect = pygame.Rect(
                            heart_x + cx * pixel_size,
                            lives_y + cy * pixel_size,
                            pixel_size, pixel_size
                        )
                        # Draw with additive blending
                        glow_surf = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
                        glow_surf.fill((255, 180, 180, inner_glow_alpha))
                        surface.blit(glow_surf, glow_rect.topleft, 
                                special_flags=pygame.BLEND_ADD)
                
                # 8. Reflection highlight (top lobes)
                reflection_pixels = [(1, 0), (2, 0), (5, 0), (6, 0), (1, 1), (2, 1)]
                for rx, ry in reflection_pixels:
                    reflect_surf = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
                    reflect_surf.fill((255, 255, 255, 80))
                    surface.blit(reflect_surf, 
                            (heart_x + rx * pixel_size, 
                                lives_y + ry * pixel_size))
                
            else:
                # === EMPTY HEART ===
                empty_gray = (100, 100, 100)
                empty_dark = (70, 70, 70)
                empty_outline = (50, 50, 50)
                crack_color = (60, 60, 60)
                
                # 1. Empty heart shape (outline only dengan bentuk baru)
                empty_pixels = [
                    # Row 0
                    (1, 0, empty_gray), (2, 0, empty_gray), (5, 0, empty_gray), (6, 0, empty_gray),
                    # Row 1 (outline sides)
                    (0, 1, empty_gray), (7, 1, empty_gray),
                    # Row 2
                    (0, 2, empty_gray), (7, 2, empty_gray),
                    # Row 3
                    (0, 3, empty_gray), (7, 3, empty_gray),
                    # Row 4
                    (1, 4, empty_gray), (6, 4, empty_gray),
                    # Row 5
                    (2, 5, empty_gray), (5, 5, empty_gray),
                    # Row 6
                    (3, 6, empty_gray), (4, 6, empty_gray),
                    # Row 7
                    (3, 7, empty_gray), (4, 7, empty_gray),
                    # Row 8
                    (4, 8, empty_gray),
                ]
                
                # 2. Darker shading for empty heart
                empty_shading = [
                    (0, 1, empty_dark), (0, 2, empty_dark), (0, 3, empty_dark),
                    (1, 4, empty_dark), (2, 5, empty_dark), (3, 6, empty_dark),
                    (3, 7, empty_dark), (4, 8, empty_dark),
                ]
                
                # 3. Crack effect (interior)
                crack_pixels = [
                    (1, 1, crack_color), (2, 1, crack_color), (3, 1, crack_color),
                    (4, 1, crack_color), (5, 1, crack_color), (6, 1, crack_color),
                    (1, 2, crack_color), (3, 2, crack_color), (4, 2, crack_color), (6, 2, crack_color),
                    (2, 3, crack_color), (3, 3, crack_color), (5, 3, crack_color),
                    (3, 4, crack_color), (4, 4, crack_color),
                ]
                
                # 4. Draw empty heart
                pixel_size = 2
                
                for px, py, color in empty_pixels:
                    pygame.draw.rect(surface, color, 
                                (heart_x + px * pixel_size, 
                                    lives_y + py * pixel_size, 
                                    pixel_size, pixel_size))
                
                for px, py, color in empty_shading:
                    pygame.draw.rect(surface, color, 
                                (heart_x + px * pixel_size, 
                                    lives_y + py * pixel_size, 
                                    pixel_size, pixel_size))
                
                # Draw cracks
                for px, py, color in crack_pixels:
                    pygame.draw.rect(surface, color, 
                                (heart_x + px * pixel_size, 
                                    lives_y + py * pixel_size, 
                                    pixel_size, pixel_size))
                
                # 5. Outline for empty heart
                empty_outline_pixels = [
                    (0, 0, empty_outline), (1, -1, empty_outline), (2, -1, empty_outline),
                    (3, 0, empty_outline), (4, 0, empty_outline), (5, -1, empty_outline),
                    (6, -1, empty_outline), (7, 0, empty_outline),
                    (-1, 1, empty_outline), (-1, 2, empty_outline), (-1, 3, empty_outline),
                    (8, 1, empty_outline), (8, 2, empty_outline), (8, 3, empty_outline),
                    (0, 4, empty_outline), (7, 4, empty_outline),
                    (1, 5, empty_outline), (6, 5, empty_outline),
                    (2, 6, empty_outline), (5, 6, empty_outline),
                    (2, 7, empty_outline), (5, 7, empty_outline),
                    (3, 8, empty_outline), (5, 8, empty_outline),
                    (4, 9, empty_outline),
                ]
                
                for px, py, color in empty_outline_pixels:
                    pygame.draw.rect(surface, color, 
                                (heart_x + px * pixel_size, 
                                    lives_y + py * pixel_size, 
                                    pixel_size, pixel_size))
                
                # 6. Faded shadow effect
                shadow_alpha = 30
                shadow_pixels = [(2, 2), (3, 2), (4, 2), (3, 3), (4, 3), (3, 4)]
                for sx, sy in shadow_pixels:
                    shadow_surf = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
                    shadow_surf.fill((0, 0, 0, shadow_alpha))
                    surface.blit(shadow_surf, 
                            (heart_x + sx * pixel_size, 
                                lives_y + sy * pixel_size))
            
        # Gems
        gems_y = 95
        gems_text = font_text.render(f"GEMS: {player.get_gem_count()}/3", True, COLOR_GEM_GREEN)
        surface.blit(gems_text, (35, gems_y))
        
        # Gem icons
        gem_types = [COLOR_GEM_GREEN, COLOR_GEM_BLUE, COLOR_GEM_YELLOW]
        for i, gem_color in enumerate(gem_types):
            gem_x = 120 + i * 22
            gem_center = (gem_x, gems_y + 8)
            
            if i < player.get_gem_count():
                # Collected gem with glow
                gem_glow = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.circle(gem_glow, (*gem_color, 120), (7, 7), 7)
                surface.blit(gem_glow, (gem_x - 7, gems_y + 1))
                
                pygame.draw.circle(surface, gem_color, gem_center, 5)
                pygame.draw.circle(surface, (255, 255, 255), gem_center, 5, 1)
                pygame.draw.circle(surface, (255, 255, 255, 150), (gem_x - 2, gems_y + 6), 2)
            else:
                # Empty gem slot
                pygame.draw.circle(surface, (60, 60, 60), gem_center, 5, 1)
        
        # Score
        score_y = 125
        score_text = font_text.render(f"SCORE: {player.get_score()}", True, COLOR_WHITE)
        surface.blit(score_text, (35, score_y))
        
        # Time panel (separate from main HUD)
        time_width = 160
        time_height = 55
        time_x = surface.get_width() - time_width - 20
        time_surf = pygame.Surface((time_width, time_height), pygame.SRCALPHA)

        # Time panel background
        pygame.draw.rect(time_surf, (0, 0, 0, 140), (0, 0, time_width, time_height), border_radius=12)
        pygame.draw.rect(time_surf, (120, 200, 255, 80), (0, 0, time_width, time_height), 3, border_radius=12)

        surface.blit(time_surf, (time_x, 20))

        # Calculate time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        # Clock icon (positioned left with more spacing)
        clock_center = (time_x + 30, 47)
        pygame.draw.circle(surface, (100, 200, 255), clock_center, 10)
        pygame.draw.circle(surface, (255, 255, 255), clock_center, 10, 2)

        # Clock hands
        second_angle = (elapsed_time % 60) * 6 - 90
        minute_angle = ((elapsed_time / 60) % 60) * 6 - 90

        second_x = clock_center[0] + math.cos(math.radians(second_angle)) * 7
        second_y = clock_center[1] + math.sin(math.radians(second_angle)) * 7
        pygame.draw.line(surface, (255, 100, 100), clock_center, (second_x, second_y), 1)

        minute_x = clock_center[0] + math.cos(math.radians(minute_angle)) * 6
        minute_y = clock_center[1] + math.sin(math.radians(minute_angle)) * 6
        pygame.draw.line(surface, (255, 255, 255), clock_center, (minute_x, minute_y), 2)

        pygame.draw.circle(surface, (255, 255, 255), clock_center, 2)

        # Time label (positioned right side with better spacing)
        time_label = font_text.render("TIME", True, (200, 220, 240))
        label_x = time_x + 70
        surface.blit(time_label, (label_x, 28))

        # Time text (positioned below label with better vertical spacing)
        font_time = pygame.font.Font(None, 28)
        time_text = font_time.render(time_str, True, COLOR_GEM_YELLOW)
        time_text_x = label_x + (time_label.get_width() - time_text.get_width()) // 2  # Center align with label
        surface.blit(time_text, (time_text_x, 48))
    
    @staticmethod
    def draw_hint_box(surface: pygame.Surface, text: str, y_position: int = 500) -> None:
        if not text:
            return
        
        font = pygame.font.Font(None, 24)
        text_surf = font.render(text, True, COLOR_WHITE)
        text_rect = text_surf.get_rect(center=(surface.get_width() // 2, y_position))
        
        bg_rect = text_rect.inflate(20, 10)
        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 150))
        pygame.draw.rect(bg_surf, (100, 200, 255, 100), (0, 0, bg_rect.width, bg_rect.height), 
                        width=2, border_radius=8)
        surface.blit(bg_surf, bg_rect.topleft)
        surface.blit(text_surf, text_rect)
    
    @staticmethod
    def draw_menu(surface: pygame.Surface, menu_particle_timer: float) -> None:
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(30 * (1 - ratio) + 15 * ratio)
            g = int(80 * (1 - ratio) + 40 * ratio)
            b = int(50 * (1 - ratio) + 25 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))
        
        for i in range(15):
            x = (menu_particle_timer * 30 + i * 80) % surface.get_width()
            y = surface.get_height() // 2 + math.sin(menu_particle_timer * 2 + i) * 60
            pygame.draw.circle(surface, (*COLOR_SPIRIT_CYAN, 150), (int(x), int(y)), 3)
        
        font_title = pygame.font.Font(None, 120)
        title_shadow = font_title.render("ELION", True, (0, 150, 150))
        title = font_title.render("ELION", True, COLOR_SPIRIT_CYAN)
        
        title_rect = title.get_rect(center=(surface.get_width() // 2, 120))
        surface.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title, title_rect)
        
        font_sub = pygame.font.Font(None, 40)
        subtitle = font_sub.render("The Last Lightkeeper", True, COLOR_WHISPER_GREEN)
        subtitle_rect = subtitle.get_rect(center=(surface.get_width() // 2, 200))
        surface.blit(subtitle, subtitle_rect)
        
        pulse = abs(math.sin(menu_particle_timer * 2)) * 0.2 + 0.8
        button_rect = pygame.Rect(0, 0, 200, 60)
        button_rect.center = (surface.get_width() // 2, 300)
        
        glow_surf = pygame.Surface((220, 80), pygame.SRCALPHA)
        glow_surf.fill((*COLOR_SPIRIT_CYAN, int(60 * pulse)))
        surface.blit(glow_surf, (button_rect.x - 10, button_rect.y - 10))
        
        pygame.draw.rect(surface, (40, 100, 120), button_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_SPIRIT_CYAN, button_rect, width=3, border_radius=10)
        
        play_text = font_sub.render("PLAY", True, COLOR_WHITE)
        play_rect = play_text.get_rect(center=button_rect.center)
        surface.blit(play_text, play_rect)
        
        font_small = pygame.font.Font(None, 22)
        instructions = [
            "Press ENTER to Start",
            "WASD or Arrow Keys to Move",
            "SPACE to Attack (Level 2+)",
            "Collect 3 Spirit Gems",
            "ESC to Quit"
        ]
        
        for i, inst in enumerate(instructions):
            inst_text = font_small.render(inst, True, (200, 230, 200))
            inst_rect = inst_text.get_rect(center=(surface.get_width() // 2, 400 + i * 30))
            surface.blit(inst_text, inst_rect)
    
    @staticmethod
    def draw_attack_hint(surface: pygame.Surface, player: Player) -> None:
        if not player._has_spirit_lantern:
            return
        
        hint_text = "Press SPACE to release Spirit Burst"
        font = pygame.font.Font(None, 20)
        text_surf = font.render(hint_text, True, COLOR_SPIRIT_CYAN)
        
        text_rect = text_surf.get_rect(center=(surface.get_width() // 2, 
                                              surface.get_height() - 30))
        
        bg_rect = text_rect.inflate(15, 8)
        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 150))
        pygame.draw.rect(bg_surf, (100, 200, 255, 100), 
                        (0, 0, bg_rect.width, bg_rect.height), 
                        width=2, border_radius=6)
        
        surface.blit(bg_surf, bg_rect.topleft)
        surface.blit(text_surf, text_rect)
    
    @staticmethod
    def draw_win_screen(surface: pygame.Surface, elapsed_time: float, score: int) -> None:
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(20 * (1 - ratio) + 10 * ratio)
            g = int(80 * (1 - ratio) + 40 * ratio)
            b = int(60 * (1 - ratio) + 30 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))
        
        font_title = pygame.font.Font(None, 100)
        font_text = pygame.font.Font(None, 36)
        
        title = font_title.render("VICTORY!", True, COLOR_GEM_YELLOW)
        title_rect = title.get_rect(center=(surface.get_width() // 2, 120))
        shadow = font_title.render("VICTORY!", True, (100, 100, 0))
        surface.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title, title_rect)
        
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        stats = [
            f"Time: {minutes:02d}:{seconds:02d}",
            f"Final Score: {score}",
            "",
            "Press ENTER to Return to Menu"
        ]
        
        for i, stat in enumerate(stats):
            color = COLOR_WHITE if i < 2 else (150, 150, 150)
            text = font_text.render(stat, True, color)
            text_rect = text.get_rect(center=(surface.get_width() // 2, 250 + i * 50))
            surface.blit(text, text_rect)
    
    @staticmethod
    def draw_ending_sequence(surface: pygame.Surface, sequence_timer: float) -> None:
        fade_alpha = 0
        if sequence_timer < 1.0:
            fade_alpha = int(255 * (1 - sequence_timer))
            fade_color = (255, 255, 255, fade_alpha)
        elif sequence_timer < 3.0:
            fade_alpha = int(100 * (3.0 - sequence_timer) / 2.0)
            fade_color = (255, 255, 255, fade_alpha)
        else:
            fade_color = (0, 0, 0, 0)
        
        if fade_alpha > 0:
            fade_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            fade_surf.fill(fade_color)
            surface.blit(fade_surf, (0, 0))
        
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 36)
        
        if sequence_timer >= 3.0:
            text1_alpha = min(255, int(255 * (sequence_timer - 3.0)))
            text1 = font_large.render("The Last Lightkeeper is restored…", True, COLOR_BLACK)
            text1.set_alpha(text1_alpha)
            text1_rect = text1.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 30))
            surface.blit(text1, text1_rect)
        
        if sequence_timer >= 4.0:
            text2_alpha = min(255, int(255 * (sequence_timer - 4.0)))
            text2 = font_medium.render("Thank you, young guardian.", True, COLOR_BLACK)
            text2.set_alpha(text2_alpha)
            text2_rect = text2.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 30))
            surface.blit(text2, text2_rect)
        
        if sequence_timer >= 6.0:
            pulse = (math.sin(sequence_timer * 3) + 1) * 0.5
            prompt_alpha = int(200 * pulse)
            prompt = font_medium.render("Press ENTER to return to menu", True, COLOR_WHITE)
            prompt.set_alpha(prompt_alpha)
            prompt_rect = prompt.get_rect(center=(surface.get_width() // 2, surface.get_height() - 50))
            surface.blit(prompt, prompt_rect)

# ==================== OPENING GAME ====================
class OpeningCutscene:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 64)
        self.font_text = pygame.font.Font(None, 32)
        
        # Teks cutscene berurutan
        self.lines = [
            "Sejak zaman kuno, dunia dijaga oleh para Lightkeeper...",
            "Namun kini, cahaya itu hampir padam.",
            "Tiga Spirit Gem telah tersebar dan dijaga kekuatan gelap.",
            "Hanya satu yang tersisa untuk memulihkan keseimbangan...",
            "ELION, sang Lightkeeper terakhir."
        ]
        
        self.index = 0           # Teks yang sedang ditampilkan
        self.alpha = 0           # Transparansi current text
        self.fade_speed = 100    # Kecepatan fade
        self.state = "fade_in"   # fade_in → hold → fade_out
        self.hold_timer = 0      # Waktu menahan teks
        self.hold_duration = 2   # Detik
        
        self.finished = False

        # Surface untuk fade + text
        self.text_surface = None
        self.update_text_surface()

    def update_text_surface(self):
        """Render ulang teks sesuai index"""
        text = self.lines[self.index]
        self.text_surface = self.font_text.render(text, True, (255, 255, 255))
        self.text_surface.set_alpha(self.alpha)

    def update(self, dt):
        """Update animasi fade-in dan fade-out"""
        if self.state == "fade_in":
            self.alpha += self.fade_speed * dt
            if self.alpha >= 255:
                self.alpha = 255
                self.state = "hold"
                self.hold_timer = 0
        
        elif self.state == "hold":
            self.hold_timer += dt
            if self.hold_timer >= self.hold_duration:
                self.state = "fade_out"
        
        elif self.state == "fade_out":
            self.alpha -= self.fade_speed * dt
            if self.alpha <= 0:
                self.alpha = 0
                self.index += 1
                if self.index >= len(self.lines):
                    self.finished = True
                else:
                    self.state = "fade_in"
                    self.update_text_surface()
        
        self.text_surface.set_alpha(self.alpha)

    def draw(self):
        """Gambar background + teks dengan fade"""
        self.screen.fill((10, 10, 10))  # Background hitam lembut

        if not self.finished:
            rect = self.text_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(self.text_surface, rect)
        else:
            # Teks Judul Besar setelah cutscene selesai
            title = self.font_title.render("ELION – THE LAST LIGHTKEEPER", True, (255, 255, 180))
            title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(title, title_rect)

# ==================== ENHANCED ENDING REFLECTION ====================
class EndingReflection:
    def __init__(self):
        self.sequence_timer = 0.0
        self.stages = []
        self.current_stage = 0
        self.finished = False
        
        # Reflection stages
        self.stages = [
            (1.0, "black", ""),  # Initial fade to black
            (2.0, "fade_in", "Perjalanan Elion bukan hanya tentang cahaya..."),
            (1.5, "hold", "Perjalanan Elion bukan hanya tentang cahaya..."),
            (1.0, "fade_out", "Perjalanan Elion bukan hanya tentang cahaya..."),
            
            (1.0, "fade_in", "Ia belajar menjaga kekuatan dalam dirinya."),
            (1.5, "hold", "Ia belajar menjaga kekuatan dalam dirinya."),
            (1.0, "fade_out", "Ia belajar menjaga kekuatan dalam dirinya."),
            
            (1.0, "fade_in", "Mewarisi kemampuan dari masa lalu..."),
            (1.5, "hold", "Mewarisi kemampuan dari masa lalu..."),
            (1.0, "fade_out", "Mewarisi kemampuan dari masa lalu..."),
            
            (1.0, "fade_in", "Dan bertindak sesuai perannya."),
            (2.0, "hold", "Dan bertindak sesuai perannya."),
            (1.0, "fade_out", "Dan bertindak sesuai perannya."),
            
            (1.0, "fade_in", "Encapsulation. Inheritance. Polymorphism."),
            (3.0, "hold", "Encapsulation. Inheritance. Polymorphism."),
            (1.0, "fade_out", "Encapsulation. Inheritance. Polymorphism."),
            
            (1.0, "fade_in", "— The Last Lightkeeper"),
            (3.0, "hold", "— The Last Lightkeeper"),
            (2.0, "final", "— The Last Lightkeeper")
        ]
        
        # Visual elements
        self.particles = []
        self.light_beam_height = 0
        self.silhouette_alpha = 0
        self.concept_glow = {"encapsulation": 0, "inheritance": 0, "polymorphism": 0}
        
    def update(self, dt: float) -> None:
        """Update ending sequence"""
        self.sequence_timer += dt
        
        # Update current stage
        if self.current_stage < len(self.stages):
            stage_duration, stage_type, stage_text = self.stages[self.current_stage]
            
            if self.sequence_timer >= stage_duration:
                self.sequence_timer = 0.0
                self.current_stage += 1
                
                # Start effects for certain stages
                if self.current_stage == 5:  # After first text
                    self.light_beam_height = 0
                elif self.current_stage == 16:  # "Encapsulation..." stage
                    self.concept_glow = {"encapsulation": 0, "inheritance": 0, "polymorphism": 0}
        else:
            self.finished = True
        
        # Update light beam
        if self.light_beam_height < 1.0:
            self.light_beam_height = min(1.0, self.light_beam_height + dt * 0.3)
        
        # Update concept glow
        if self.current_stage >= 13:  # During concepts stage
            for concept in self.concept_glow:
                self.concept_glow[concept] = (math.sin(pygame.time.get_ticks() * 0.002) + 1) * 0.5
        
        # Update particles
        for p in self.particles[:]:
            p['y'] -= p['speed'] * dt
            p['life'] -= dt
            if p['life'] <= 0:
                self.particles.remove(p)
        
        # Add new particles
        if random.random() < 0.3:
            self.particles.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': WINDOW_HEIGHT + 10,
                'speed': random.uniform(50, 150),
                'size': random.uniform(2, 5),
                'color': (100, 255, 200),
                'life': random.uniform(2, 4)
            })
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw ending reflection"""
        # Background - dark blue gradient
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(5 * (1 - ratio) + 10 * ratio)
            g = int(10 * (1 - ratio) + 30 * ratio)
            b = int(20 * (1 - ratio) + 50 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))
        
        # Particles
        for p in self.particles:
            alpha = int(255 * (p['life'] / 4.0))
            pygame.draw.circle(surface, (*p['color'], alpha), 
                             (int(p['x']), int(p['y'])), int(p['size']))
        
        # Light beam from top
        if self.light_beam_height > 0:
            beam_height = int(surface.get_height() * self.light_beam_height)
            beam_surf = pygame.Surface((surface.get_width(), beam_height), pygame.SRCALPHA)
            
            # Gradient beam
            for y in range(beam_height):
                alpha = int(30 * (1 - y/beam_height))
                pygame.draw.line(beam_surf, (255, 255, 255, alpha), 
                                (0, y), (surface.get_width(), y))
            
            surface.blit(beam_surf, (0, 0))
        
        # Silhouette of Elion and Companion
        if self.current_stage >= 4:  # After first few texts
            silhouette_surf = pygame.Surface((300, 400), pygame.SRCALPHA)
            
            # Elion silhouette
            pygame.draw.rect(silhouette_surf, (0, 0, 0, 200), 
                           (100, 100, 60, 120), border_radius=10)
            # Companion silhouette
            pygame.draw.circle(silhouette_surf, (0, 0, 0, 200), 
                             (200, 160), 30)
            
            surface.blit(silhouette_surf, 
                        (surface.get_width()//2 - 150, 
                         surface.get_height()//2 - 100))
        
        # Draw current text
        if self.current_stage < len(self.stages):
            _, stage_type, text = self.stages[self.current_stage]
            
            if text and stage_type != "black":
                # Calculate alpha based on stage type
                if stage_type == "fade_in":
                    alpha = int(255 * (self.sequence_timer / 1.0))
                elif stage_type == "fade_out":
                    alpha = int(255 * (1 - self.sequence_timer / 1.0))
                else:  # hold, final
                    alpha = 255
                
                # Draw text
                if "Encapsulation" in text or "Lightkeeper" in text:
                    # Special styling for key texts
                    font_size = 48 if "Encapsulation" in text else 36
                    font = pygame.font.Font(None, font_size)
                    color = (255, 255, 100) if "Encapsulation" in text else (200, 200, 255)
                else:
                    font = pygame.font.Font(None, 42)
                    color = (220, 240, 255)
                
                text_surf = font.render(text, True, color)
                text_surf.set_alpha(alpha)
                text_rect = text_surf.get_rect(center=(surface.get_width()//2, 
                                                      surface.get_height()//2))
                
                # Draw glow for concepts
                if "Encapsulation" in text:
                    glow_alpha = int(100 * self.concept_glow.get("encapsulation", 0))
                    glow_surf = pygame.Surface((text_rect.width + 40, text_rect.height + 20), 
                                              pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (100, 255, 200, glow_alpha), 
                                   (0, 0, glow_surf.get_width(), glow_surf.get_height()), 
                                   border_radius=10)
                    surface.blit(glow_surf, (text_rect.x - 20, text_rect.y - 10))
                
                surface.blit(text_surf, text_rect)
        
        # Draw continue prompt
        if self.finished or self.current_stage >= len(self.stages) - 3:
            pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) * 0.5
            alpha = int(200 * pulse)
            
            font = pygame.font.Font(None, 32)
            prompt = font.render("Tekan ENTER untuk kembali ke menu", True, (255, 255, 255))
            prompt.set_alpha(alpha)
            prompt_rect = prompt.get_rect(center=(surface.get_width()//2, 
                                                 surface.get_height() - 50))
            surface.blit(prompt, prompt_rect)


# ==================== GAME CLASS ====================
class Game:
    def __init__(self):
        # Setup window dengan vsync
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 
                                              pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("ELION – The Last Lightkeeper (Enhanced Visual Edition)")
        
        self.render_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))
        self.screen = self.window
        
        # Initialize systems
        self.cutscene = None
        self.world_map = WorldMap()
        self.ending_reflection = None
        self.companion: Optional[MentorCompanion] = None
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Game state
        self.current_level = Level.LEVEL_1
        self.world_width = 1920
        self.world_height = 1080
        
        # Enhanced systems
        self.particle_system = ParticleSystem()
        self.camera = Camera(RENDER_WIDTH, RENDER_HEIGHT, self.world_width, self.world_height)
        self.tilemap = TileMap(self.world_width, self.world_height, self.current_level)
        
        # Game objects
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.gems: List[Gem] = []
        self.portal: Optional[Portal] = None
        self.altar: Optional[SpiritAltar] = None
        
        # Level state
        self.level2_miniboss_defeated = False
        self.level2_cutscene_played = False
        self.level3_gems_floating: List[Gem] = []
        
        # Timers
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.menu_particle_timer = 0.0
        self.ending_sequence_timer = 0.0
        self.ending_sequence_active = False
        
        # Initialize first level
        self._init_level(self.current_level)
        
        # Audio setup
        self.setup_audio()
    
    def setup_audio(self):
        """Setup audio system"""
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self._bgm_path: Optional[str] = None
        self._worldmap_bgm_path: Optional[str] = None
        self._ending2_played = False
        
        base_dir = os.path.dirname(__file__)
        
        def try_load_sound(key: str, filename: str):
            path = os.path.join(base_dir, filename)
            if os.path.isfile(path):
                try:
                    self.sounds[key] = pygame.mixer.Sound(path)
                    self.sounds[key].set_volume(0.7)
                except Exception:
                    self.sounds[key] = None
            else:
                self.sounds[key] = None
        
        # Load sound effects
        try_load_sound('start', 'audio/start.mp3')
        try_load_sound('portal', 'audio/portal.mp3')
        try_load_sound('ending', 'audio/ending.mp3')
        try_load_sound('ending2', 'audio/ending2.mp3')
        try_load_sound('collect', 'audio/collect.mp3')
        try_load_sound('attack', 'audio/attack.mp3')
        try_load_sound('damage', 'audio/damage.mp3')
        try_load_sound('worldMap', 'audio/world_map.mp3')
        
        # BGM
        bgm_path = os.path.join(base_dir, 'audio/BGM.mp3')
        if os.path.isfile(bgm_path):
            self._bgm_path = bgm_path
        
        # World Map BGM
        worldmap_bgm_path = os.path.join(base_dir, 'audio/world_map.mp3')
        if os.path.isfile(worldmap_bgm_path):
            self._worldmap_bgm_path = worldmap_bgm_path
    
    def _init_level(self, level: Level) -> None:
        self.current_level = level
        
        if level == Level.LEVEL_2:
            self.world_width = LEVEL2_WORLD_WIDTH
            self.world_height = LEVEL2_WORLD_HEIGHT
        elif level == Level.LEVEL_3:
            self.world_width = LEVEL3_WORLD_WIDTH
            self.world_height = LEVEL3_WORLD_HEIGHT
        else:
            self.world_width = 1920
            self.world_height = 1080
        
        self.camera = Camera(RENDER_WIDTH, RENDER_HEIGHT, self.world_width, self.world_height)
        self.tilemap = TileMap(self.world_width, self.world_height, level)
        
        self.enemies = []
        self.gems = []
        self.portal = None
        self.altar = None
        self.level3_gems_floating = []
        
        if self.player is None:
            self.player = Player(200, 200)
        else:
            if level == Level.LEVEL_3:
                while self.player.get_gem_count() < 3:
                    gem_types = ["gem_green", "gem_blue", "gem_yellow"]
                    gem_colors = [COLOR_GEM_GREEN, COLOR_GEM_BLUE, COLOR_GEM_YELLOW]
                    for i, gem_type in enumerate(gem_types):
                        if not self.player.has_gem(gem_type):
                            self.player.collect_gem(gem_type, gem_colors[i])
                            break
            self.player._x = 200
            self.player._y = 200
        
        if self.companion is None:
            if hasattr(self, 'world_map') and self.world_map.all_codex_read:
                self.companion = MentorCompanion(160, 200)
                self.companion.activate_mentor()
            else:
                self.companion = Companion(160, 200)
        else:
            # Ensure companion is MentorCompanion if needed
            if hasattr(self, 'world_map') and self.world_map.all_codex_read and not isinstance(self.companion, MentorCompanion):
                old_x, old_y = self.companion.get_position()
                self.companion = MentorCompanion(old_x, old_y)
                self.companion.activate_mentor()
            else:
                self.companion._x = 160
                self.companion._y = 200
                self.companion._idle_at_altar = False
                self.companion._altar_position = None
        
        if level == Level.LEVEL_1:
            self._init_level1()
        elif level == Level.LEVEL_2:
            self._init_level2()
        elif level == Level.LEVEL_3:
            self._init_level3()
    
    def _init_level1(self) -> None:
        self.enemies = [
            GlimpEnemy(400, 300, [(400, 300), (700, 300), (700, 500), (400, 500)]),
            GlimpEnemy(900, 400, [(900, 400), (1200, 400)]),
            UmbraEnemy(600, 600),
            UmbraEnemy(1000, 700)
        ]
        
        self.gems = [
            Gem(500, 250, "gem_green", COLOR_GEM_GREEN),
            Gem(1100, 500, "gem_blue", COLOR_GEM_BLUE),
            Gem(1500, 800, "gem_yellow", COLOR_GEM_YELLOW)
        ]
        
        self.portal = Portal(1700, 900, "red", Level.LEVEL_2)
    
    def _init_level2(self) -> None:
        self.level2_miniboss_defeated = False
        self.level2_cutscene_played = False
        
        self.enemies = [
            FlareWolfEnemy(400, 300, [(400, 300), (600, 300), (600, 500), (400, 500)]),
            FlareWolfEnemy(800, 400, [(800, 400), (1000, 400), (1000, 600), (800, 600)]),
            FlareWolfEnemy(1200, 200, [(1200, 200), (1400, 200), (1400, 400), (1200, 400)]),
            ForestGuardianEnemy(1800, 500)
        ]
        
        for _ in range(5):
            x = random.randint(100, self.world_width - 100)
            y = random.randint(100, self.world_height - 100)
            crystal = Gem(x, y, "crystal_decor", (200, 150, 100))
            crystal._collected = True
            self.gems.append(crystal)
        
        self.portal = None
    
    def _init_level3(self) -> None:
        self.enemies = []
        self.gems = []
        
        altar_pos = self.tilemap.get_altar_position()
        if altar_pos:
            self.altar = SpiritAltar(altar_pos[0], altar_pos[1])
        
        self.portal = None
    
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # MENU: Enter goes to World Map instead of directly to cutscene
                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.WORLD_MAP
                        try:
                            self.play_sfx('worldMap')
                        except Exception:
                            pass
                
                # WORLD MAP: ESC returns to menu
                elif self.state == GameState.WORLD_MAP:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                
                # CODEX VIEW: ESC or ENTER closes codex
                elif self.state == GameState.CODEX_VIEW:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                        self.world_map.mark_codex_read()
                        self.state = GameState.WORLD_MAP
                
                # CUTSCENE: Skip with ENTER
                elif self.state == GameState.CUTSCENE:
                    if event.key == pygame.K_RETURN:
                        self.cutscene.finished = True
                
                # WIN SCREEN: ENTER goes to menu
                elif self.state == GameState.WIN:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.MENU
                
                # ENDING: ENTER returns to menu after reflection
                elif self.state == GameState.ENDING:
                    if event.key == pygame.K_RETURN and self.ending_reflection and \
                       (self.ending_reflection.finished or 
                        self.ending_reflection.current_stage >= len(self.ending_reflection.stages) - 3):
                        self.state = GameState.MENU
                        self.ending_sequence_active = False
                        self.ending_sequence_timer = 0.0
            
            # Mouse clicks for World Map
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == GameState.WORLD_MAP:
                    result = self.world_map.handle_click(event.pos)
                    
                    if result == "start_journey":
                        # Start the game journey
                        try:
                            if hasattr(self, 'play_sfx'):
                                self.play_sfx('start')
                        except Exception:
                            pass
                        self.cutscene = OpeningCutscene(self.screen)
                        self.change_state(GameState.CUTSCENE)
                    
                    elif isinstance(result, CodexPanel):
                        self.state = GameState.CODEX_VIEW
                
                elif self.state == GameState.CODEX_VIEW:
                    # Check if close button clicked
                    close_button = self.world_map.codex_panel.draw(self.window)
                    if close_button and close_button.collidepoint(event.pos):
                        self.world_map.mark_codex_read()
                        self.state = GameState.WORLD_MAP
            
            # Mouse motion for World Map hover
            if event.type == pygame.MOUSEMOTION:
                if self.state == GameState.WORLD_MAP:
                    self.world_map.check_hover(event.pos)
    
    def update(self, dt: float) -> None:
        if self.state == GameState.MENU:
            self.menu_particle_timer += dt
            return

        elif self.state == GameState.WORLD_MAP:
            self.world_map.update(dt)
            return
        
        elif self.state == GameState.CODEX_VIEW:
            return
        
        elif self.state == GameState.CUTSCENE:
            if self.cutscene:
                self.cutscene.update(dt)
                if self.cutscene.finished:
                    self.change_state(GameState.PLAYING)
            return
        
        elif self.state == GameState.ENDING:
            if self.ending_reflection:
                self.ending_reflection.update(dt)
            else:
                self.ending_sequence_timer += dt
                
            # Play second ending track
            if not getattr(self, '_ending2_played', False) and \
               ((self.ending_reflection and self.ending_reflection.current_stage > 10) or 
                self.ending_sequence_timer >= 3.0):
                try:
                    self.play_sfx('ending2')
                except Exception:
                    pass
                self._ending2_played = True
            return

        self.elapsed_time = pygame.time.get_ticks() / 1000.0 - self.start_time
        
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, dt, self.world_width, self.world_height)
        self.player.update(dt)
        
        self.companion.follow_player(self.player)
        self.companion.update(dt)
        
        px, py = self.player.get_position()
        self.camera.set_target(px, py)
        
        if self.current_level == Level.LEVEL_3 and self.altar and self.altar.is_activated():
            self.camera.set_zoom(0.9)
        else:
            self.camera.set_zoom(1.0)
        
        self.camera.update(dt)
        
        if self.current_level == Level.LEVEL_2:
            self._update_level2(dt)
        elif self.current_level == Level.LEVEL_3:
            self._update_level3(dt)
        else:
            self._update_default_level(dt)
        
        self.particle_system.update(dt)
    
    def _update_default_level(self, dt: float) -> None:
        for enemy in self.enemies[:]:
            enemy.take_action(self.player, dt)
            enemy.update(dt, self.world_width, self.world_height)
            
            if enemy.collides_with(self.player.get_rect()):
                if self.player.take_damage():
                    try:
                        self.play_sfx('damage')
                    except Exception:
                        pass
                    self.camera.shake(8, 0.3)
                    cx, cy = self.player.get_center()
                    self.particle_system.emit(cx, cy, (255, 80, 80), count=20, spread=60, life=0.8)
                    
                    if self.player.get_lives() <= 0:
                        self.state = GameState.GAMEOVER

        # Add mentor wisdom for events
        enemy_encountered = False
        for enemy in self.enemies:
            # Check if player is near enemy
            px, py = self.player.get_position()
            ex, ey = enemy.get_position()
            dist = math.sqrt((px - ex)**2 + (py - ey)**2)
            
            if dist < 150 and not enemy_encountered:
                if self.companion and random.random() < 0.01:  # 1% chance per frame
                    self.companion.give_wisdom("enemy_encounter")
                    enemy_encountered = True
        
        for gem in self.gems[:]:
            gem.update(dt)
            
            if not gem.is_collected() and gem.get_rect().colliderect(self.player.get_rect()):
                gem_type, gem_color = gem.collect()
                self.player.collect_gem(gem_type, gem_color)
                
                try:
                    self.play_sfx('collect')
                except Exception:
                    pass
                
                self.camera.shake(5, 0.2)
                cx, cy = gem.get_center()
                self.particle_system.emit(cx, cy, gem_color, count=30, spread=80, life=1.2)
                
                if self.companion.can_give_hint():
                    remaining = 3 - self.player.get_gem_count()
                    if remaining > 0:
                        self.companion.give_hint(f"{remaining} more to go!")
                    else:
                        self.companion.give_hint("Find the portal!")
        
        self.gems = [gem for gem in self.gems if not gem.is_collected()]
        
        if self.portal:
            self.portal.update(dt, self.player)
            
            if self.portal.get_rect().colliderect(self.player.get_rect()):
                target_level = self.portal.get_target_level()
                if target_level:
                    try:
                        self.play_sfx('portal')
                    except Exception:
                        pass
                    self._transition_to_level(target_level)
                elif self.player.get_gem_count() >= 3:
                    try:
                        self.play_sfx('portal')
                    except Exception:
                        pass
                    self.camera.shake(10, 0.5)
                    cx, cy = self.player.get_center()
                    self.particle_system.emit(cx, cy, COLOR_SPIRIT_CYAN, count=50, spread=100, life=2.0)
                    self.change_state(GameState.WIN)
    
    def _update_level2(self, dt: float) -> None:
        if not self.level2_cutscene_played:
            self.level2_cutscene_played = True
            self._play_level2_cutscene()
        
        for enemy in self.enemies[:]:
            enemy.take_action(self.player, dt)
            enemy.update(dt, self.world_width, self.world_height)
            
            for burst in self.player.get_spirit_bursts()[:]:
                burst_rect = pygame.Rect(
                    int(burst['x'] - burst['size']//2),
                    int(burst['y'] - burst['size']//2),
                    burst['size'], burst['size']
                )
                
                if enemy.collides_with(burst_rect):
                    if enemy.take_damage():
                        self.enemies.remove(enemy)
                        
                        ex, ey = enemy.get_position()
                        cx = ex + enemy._size // 2
                        cy = ey + enemy._size // 2
                        
                        if enemy._type == "flare_wolf":
                            self.particle_system.emit(cx, cy, (255, 140, 0), 
                                                    count=25, spread=70, life=1.0)
                        elif enemy._type == "forest_guardian":
                            try:
                                self.play_sfx('attack')
                            except Exception:
                                pass
                            self.particle_system.emit(cx, cy, (100, 255, 100), 
                                                    count=40, spread=100, life=1.5)
                            self.level2_miniboss_defeated = True
                            self.portal = Portal(1900, 500, "victory", Level.LEVEL_3)
                        else:
                            self.particle_system.emit(cx, cy, COLOR_SPIRIT_CYAN, 
                                                    count=20, spread=60, life=0.8)
                        
                        self.camera.shake(5, 0.2)
                        self.player._score += 50 if enemy._type == "forest_guardian" else 30
                        self.player.remove_spirit_burst(burst)
                        break
                    else:
                        if enemy._type == "forest_guardian":
                            self.camera.shake(3, 0.1)
                            ex, ey = enemy.get_position()
                            cx = ex + enemy._size // 2
                            cy = ey + enemy._size // 2
                            self.particle_system.emit(cx, cy, COLOR_SPIRIT_CYAN,
                                                    count=15, spread=40, life=0.5)
                        
                        self.player.remove_spirit_burst(burst)
                        break
            
            if enemy.collides_with(self.player.get_rect()):
                if self.player.take_damage():
                    self.camera.shake(8, 0.3)
                    cx, cy = self.player.get_center()
                    
                    if enemy._type == "flare_wolf":
                        self.particle_system.emit(cx, cy, (255, 100, 0), count=25, spread=70, life=0.9)
                    else:
                        self.particle_system.emit(cx, cy, (255, 80, 80), count=20, spread=60, life=0.8)
                    
                    if self.player.get_lives() <= 0:
                        self.state = GameState.GAMEOVER

                    if self.companion and random.random() < 0.3:  # 30% chance on damage
                        self.companion.give_wisdom("damage_taken")
        
        for enemy in self.enemies:
            if enemy._type == "forest_guardian":
                for proj in enemy.get_projectiles():
                    proj_rect = pygame.Rect(int(proj['x'] - proj['size']//2), 
                                        int(proj['y'] - proj['size']//2),
                                        proj['size'], proj['size'])
                    
                    if proj_rect.colliderect(self.player.get_rect()):
                        if self.player.take_damage():
                            self.camera.shake(6, 0.2)
                            cx, cy = self.player.get_center()
                            self.particle_system.emit(cx, cy, (100, 200, 255), count=15, spread=40, life=0.7)
        
        if random.random() < 0.1:
            ember_x = random.randint(0, self.world_width)
            ember_y = random.randint(0, 100)
            self.particle_system.emit(ember_x, ember_y, COLOR_EMBER_ORANGE, 
                                    count=random.randint(1, 3), spread=30, life=2.0,
                                    particle_type="ember")
        
        if self.portal:
            self.portal.update(dt, self.player)
            
            if self.portal.get_rect().colliderect(self.player.get_rect()):
                target_level = self.portal.get_target_level()
                if target_level:
                    try:
                        self.play_sfx('portal')
                    except Exception:
                        pass
                    self._transition_to_level(target_level)
    
    def _play_level2_cutscene(self) -> None:
        self.companion.give_hint("ELION... The path ahead is dangerous.")
        self.player.unlock_spirit_lantern()
        
        cx, cy = self.player.get_center()
        self.particle_system.emit(cx, cy, COLOR_SPIRIT_CYAN, 
                                 count=50, spread=100, life=1.5)
        
        self.camera.shake(10, 0.5)
    
    def _update_level3(self, dt: float) -> None:
        if random.random() < 0.05:
            mist_x = random.randint(0, self.world_width)
            mist_y = random.randint(self.world_height//2, self.world_height)
            self.particle_system.emit(mist_x, mist_y, COLOR_MIST_WHITE, 
                                    count=random.randint(1, 2), spread=40, life=3.0,
                                    particle_type="mist")
        
        if random.random() < 0.03:
            flower_x = random.randint(0, self.world_width)
            flower_y = random.randint(0, self.world_height)
            self.particle_system.emit(flower_x, flower_y, (200, 255, 220), 
                                    count=1, spread=5, life=2.5,
                                    particle_type="light_flower")
        
        if self.altar:
            self.altar.update(dt)
            
            if not self.altar.is_activated() and self.altar.get_rect().colliderect(self.player.get_rect()):
                if self.player.get_gem_count() >= 3 and not self.player.is_placing_gems():
                    self.player.start_gem_placement()
                    
                    altar_center = self.altar.get_center()
                    self.companion.set_altar_idle(altar_center[0], altar_center[1])
                    
                    if not self.level3_gems_floating:
                        gem_types = [gt for gt in self.player.get_inventory() if 'gem' in gt]
                        for i, gem_type in enumerate(gem_types[:3]):
                            floating_gem = Gem(self.player._x, self.player._y, gem_type, 
                                             COLOR_GEM_GREEN if i==0 else 
                                             COLOR_GEM_BLUE if i==1 else COLOR_GEM_YELLOW)
                            floating_gem._collected = True
                            
                            gem_pos = self.altar.get_gem_position(i)
                            if gem_pos:
                                floating_gem.start_floating_to_altar(gem_pos[0], gem_pos[1])
                                self.level3_gems_floating.append(floating_gem)
                                self.player.remove_gem(gem_type)
            
            if self.altar.is_activated() and not self.portal:
                altar_center = self.altar.get_center()
                self.portal = Portal(altar_center[0] - PORTAL_SIZE//2, 
                           altar_center[1] - 100,
                           "victory", None)
        
        for gem in self.level3_gems_floating[:]:
            gem.update(dt)
            
            if not gem.is_floating():
                if self.altar.place_gem():
                    self.camera.shake(15, 0.6)
                    altar_center = self.altar.get_center()
                    self.particle_system.emit(altar_center[0], altar_center[1], 
                                            COLOR_SPIRIT_TREE, count=100, spread=150, life=2.0)
                
                self.level3_gems_floating.remove(gem)
        
        if self.portal and self.portal.get_rect().colliderect(self.player.get_rect()):
            # play portal SFX
            try:
                self.play_sfx('portal')
            except Exception:
                pass
            self.change_state(GameState.ENDING)
    
    def _transition_to_level(self, target_level: Level) -> None:
        self.camera.shake(10, 0.5)
        cx, cy = self.player.get_center()
        self.particle_system.emit(cx, cy, COLOR_SPIRIT_CYAN, count=50, spread=100, life=2.0)
        
        self._init_level(target_level)
    
    def draw(self) -> None:
        if self.state == GameState.MENU:
            UI.draw_menu(self.render_surface, self.menu_particle_timer)

        elif self.state == GameState.WORLD_MAP:
            self.world_map.draw(self.window)
            pygame.display.flip()
            return
        
        elif self.state == GameState.CODEX_VIEW:
            self.world_map.draw(self.window)
            close_button = self.world_map.codex_panel.draw(self.window)
            pygame.display.flip()
            return
        
        elif self.state == GameState.CUTSCENE:
            self.cutscene.draw()
            pygame.display.flip()
            return
        
        elif self.state == GameState.ENDING:
            if self.ending_reflection:
                self.ending_reflection.draw(self.window)
            else:
                # Fallback to old ending if reflection not initialized
                self._draw_game_scene()
                UI.draw_ending_sequence(self.render_surface, self.ending_sequence_timer)
            
            pygame.display.flip()
            return
        
        elif self.state == GameState.WIN:
            UI.draw_win_screen(self.render_surface, self.elapsed_time, self.player.get_score())
            self.particle_system.draw(self.render_surface, (0, 0))
        
        elif self.state == GameState.PLAYING:
            self._draw_game_scene()
        
        # Scale and display
        scaled_surface = pygame.transform.scale(self.render_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def change_state(self, new_state: GameState) -> None:
        """Handle high-level state transitions."""
        self.state = new_state
        if new_state == GameState.PLAYING:
            # start gameplay timer and initialize level
            self.start_time = pygame.time.get_ticks() / 1000.0
            if not self.current_level:
                self.current_level = Level.LEVEL_1
            self._init_level(self.current_level)

            # Activate mentor companion if all codex read
            if self.companion and self.world_map.all_codex_read:
                # Ensure companion is MentorCompanion
                if not isinstance(self.companion, MentorCompanion):
                    # Convert to MentorCompanion
                    old_x, old_y = self.companion.get_position()
                    self.companion = MentorCompanion(old_x, old_y)
                self.companion.activate_mentor()
                # Give initial wisdom
                self.companion.give_wisdom("level_complete")

            # start BGM if available
            try:
                if self._bgm_path:
                    pygame.mixer.music.load(self._bgm_path)
                    pygame.mixer.music.set_volume(1)
                    pygame.mixer.music.play(-1)
            except Exception:
                pass

        elif new_state == GameState.ENDING:
            # Initialize ending reflection
            self.ending_reflection = EndingReflection()
            self.ending_sequence_active = True
            self._ending2_played = False
            # fade out bgm and play ending SFX
            try:
                pygame.mixer.music.fadeout(1000)
            except Exception:
                pass
            try:
                self.play_sfx('ending')
            except Exception:
                pass

        elif new_state == GameState.WORLD_MAP:
            # Play world map BGM
            try:
                if self._worldmap_bgm_path:
                    pygame.mixer.music.load(self._worldmap_bgm_path)
                    pygame.mixer.music.set_volume(0.6)
                    pygame.mixer.music.play(-1)
            except Exception:
                pass

        elif new_state == GameState.CUTSCENE:
            # Keep world map BGM for cutscene
            try:
                if self._worldmap_bgm_path and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(self._worldmap_bgm_path)
                    pygame.mixer.music.set_volume(0.6)
                    pygame.mixer.music.play(-1)
            except Exception:
                pass

        if new_state == GameState.MENU:
            # stop BGM when returning to menu
            try:
                pygame.mixer.music.fadeout(500)
            except Exception:
                pass

    def play_sfx(self, key: str) -> None:
        """Play a loaded sound effect by key (safe no-ops if missing)."""
        if not hasattr(self, 'sounds'):
            return
        snd = self.sounds.get(key)
        if snd:
            try:
                snd.play()
            except Exception:
                pass
    
    def _draw_game_scene(self) -> None:
        """Enhanced game scene drawing"""
        camera_offset = self.camera.get_offset()
        
        # Dynamic background berdasarkan level
        if self.current_level == Level.LEVEL_2:
            # Sunset background dengan gradien lebih smooth
            for y in range(RENDER_HEIGHT):
                ratio = y / RENDER_HEIGHT
                # Gradien dari orange ke merah
                r = int(COLOR_SUNSET_ORANGE[0] * (1 - ratio) + COLOR_SUNSET_RED[0] * ratio)
                g = int(COLOR_SUNSET_ORANGE[1] * (1 - ratio) + COLOR_SUNSET_RED[1] * ratio)
                b = int(COLOR_SUNSET_ORANGE[2] * (1 - ratio) + COLOR_SUNSET_RED[2] * ratio)
                
                # Tambahkan noise untuk texture
                noise = random.randint(-5, 5)
                r = max(0, min(255, r + noise))
                g = max(0, min(255, g + noise))
                b = max(0, min(255, b + noise))
                
                pygame.draw.line(self.render_surface, (r, g, b), (0, y), (RENDER_WIDTH, y))
            
            # Sun/moon
            sun_radius = 40
            sun_x = RENDER_WIDTH // 4
            sun_y = RENDER_HEIGHT // 3
            
            # Sun glow
            sun_glow = pygame.Surface((sun_radius * 4, sun_radius * 4), pygame.SRCALPHA)
            for i in range(3, 0, -1):
                layer_radius = sun_radius + i * 10
                layer_alpha = 40 // (i + 1)
                pygame.draw.circle(sun_glow, (255, 200, 100, layer_alpha),
                                 (sun_radius * 2, sun_radius * 2), layer_radius)
            self.render_surface.blit(sun_glow, (sun_x - sun_radius * 2, sun_y - sun_radius * 2),
                                    special_flags=pygame.BLEND_ADD)
            
            # Sun core
            pygame.draw.circle(self.render_surface, (255, 220, 140), (sun_x, sun_y), sun_radius)
            pygame.draw.circle(self.render_surface, (255, 200, 100), (sun_x, sun_y), sun_radius - 5)
            
        elif self.current_level == Level.LEVEL_3:
            # Celestial background untuk castle
            for y in range(RENDER_HEIGHT):
                ratio = y / RENDER_HEIGHT
                # Gradien dari dark blue ke light purple
                r = int(30 * (1 - ratio) + 120 * ratio)
                g = int(40 * (1 - ratio) + 100 * ratio)
                b = int(70 * (1 - ratio) + 180 * ratio)
                pygame.draw.line(self.render_surface, (r, g, b), (0, y), (RENDER_WIDTH, y))
            
            # Stars
            for _ in range(20):
                star_x = random.randint(0, RENDER_WIDTH)
                star_y = random.randint(0, RENDER_HEIGHT // 2)
                star_size = random.randint(1, 3)
                star_brightness = random.randint(150, 255)
                pygame.draw.circle(self.render_surface, (star_brightness, star_brightness, star_brightness),
                                 (star_x, star_y), star_size)
                
                # Star twinkle
                if random.random() < 0.1:
                    star_glow = pygame.Surface((star_size * 4, star_size * 4), pygame.SRCALPHA)
                    pygame.draw.circle(star_glow, (255, 255, 255, 100),
                                     (star_size * 2, star_size * 2), star_size * 2)
                    self.render_surface.blit(star_glow, (star_x - star_size * 2, star_y - star_size * 2))
        
        else:  # Level 1 - Forest
            # Forest sky dengan gradien
            for y in range(RENDER_HEIGHT):
                ratio = y / RENDER_HEIGHT
                # Gradien dari light blue ke green
                r = int(100 * (1 - ratio) + 60 * ratio)
                g = int(160 * (1 - ratio) + 120 * ratio)
                b = int(200 * (1 - ratio) + 100 * ratio)
                pygame.draw.line(self.render_surface, (r, g, b), (0, y), (RENDER_WIDTH, y))
            
            # Cloud effect
            if random.random() < 0.01:
                cloud_x = random.randint(0, RENDER_WIDTH)
                cloud_y = random.randint(0, RENDER_HEIGHT // 3)
                cloud_width = random.randint(40, 80)
                cloud_height = random.randint(20, 40)
                
                cloud_surf = pygame.Surface((cloud_width, cloud_height), pygame.SRCALPHA)
                pygame.draw.ellipse(cloud_surf, (255, 255, 255, 60),
                                  (0, 0, cloud_width, cloud_height))
                self.render_surface.blit(cloud_surf, (cloud_x, cloud_y))
        
        # Draw tilemap layers
        self.tilemap.draw_base(self.render_surface, camera_offset)
        self.tilemap.draw_objects_below(self.render_surface, camera_offset)
        
        # Draw collectibles
        for gem in self.gems:
            gem.draw(self.render_surface, camera_offset, self.particle_system)
        
        for gem in self.level3_gems_floating:
            gem.draw(self.render_surface, camera_offset, self.particle_system)
        
        # Draw altar
        if self.altar:
            self.altar.draw(self.render_surface, camera_offset, self.particle_system)
        
        # Draw portal
        if self.portal:
            self.portal.draw(self.render_surface, camera_offset, self.particle_system)
        
        # Sort entities by Y for proper drawing order
        entities_to_sort = []
        
        if self.player:
            entities_to_sort.append((self.player.get_position()[1], 'player', self.player))
        if self.companion:
            entities_to_sort.append((self.companion.get_position()[1], 'companion', self.companion))
        for enemy in self.enemies:
            entities_to_sort.append((enemy.get_position()[1], 'enemy', enemy))
        
        entities_to_sort.sort(key=lambda x: x[0])
        
        # Draw entities in sorted order
        for _, entity_type, entity in entities_to_sort:
            if entity_type == 'player':
                entity.draw(self.render_surface, camera_offset, self.particle_system)
            elif entity_type == 'companion':
                entity.draw(self.render_surface, camera_offset)
            elif entity_type == 'enemy':
                entity.draw(self.render_surface, camera_offset)
        
        # Draw particles
        self.particle_system.draw(self.render_surface, camera_offset)
        
        # Draw objects above entities (trees, etc.)
        self.tilemap.draw_objects_above(self.render_surface, camera_offset)
        
        # Draw UI jika sedang playing
        if self.state == GameState.PLAYING:
            UI.draw_hud(self.render_surface, self.player, self.elapsed_time, self.current_level)
            
            # Level-specific UI
            if self.current_level == Level.LEVEL_2:
                UI.draw_attack_hint(self.render_surface, self.player)
            
            # Companion hints
            if self.companion._hint_timer > 0:
                UI.draw_hint_box(self.render_surface, self.companion._hint_text)
            
            # Altar hint
            if self.current_level == Level.LEVEL_3 and self.altar:
                if not self.altar.is_activated() and self.player.get_gem_count() >= 3:
                    if self.altar.get_rect().colliderect(self.player.get_rect()):
                        UI.draw_hint_box(self.render_surface, "Place the spirit gems on the altar", 100)

    def run(self) -> None:
        """Enhanced main game loop"""
        print("=" * 60)
        print("🌲 ELION – The Last Lightkeeper (Enhanced Visual Edition) 🌲")
        print("=" * 60)
        print("Features:")
        print("  • Enhanced visual effects and animations")
        print("  • Improved particle systems")
        print("  • Dynamic lighting and glow effects")
        print("  • Smooth camera movements")
        print("  • Detailed tilemaps for each level")
        print("=" * 60)
        print()
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()


# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    print("=" * 60)
    print("🌲 ELION – The Last Lightkeeper 🌲")
    print("=" * 60)
    print("Controls:")
    print("  WASD / Arrow Keys - Move ELION")
    print("  SPACE - Attack (Level 2+)")
    print("  ENTER - Start Game / Continue")
    print("  ESC - Quit")
    print("=" * 60)
    print()
    print("Level Progression:")
    print("  Level 1: Collect 3 Spirit Gems")
    print("  Level 2: Path to the Spirit Castle")
    print("  Level 3: The Spirit Castle (Final)")
    print("=" * 60)
    print("Features:")
    print("  • Attack System (Spirit Burst)")
    print("  • New Enemies (Flare Wolf, Forest Guardian)")
    print("  • Final Boss Battle")
    print("  • Spirit Tree Restoration Ending")
    print("=" * 60)
    
    game = Game()
    game.run()