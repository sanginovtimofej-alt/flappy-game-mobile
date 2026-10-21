# ЧАСТЬ 1: Настройки, константы, уровни и работа с файлами (Мобильная версия)
import pygame
import random
import sys
import json
import os
import math
from datetime import datetime

# Инициализация Pygame дисплея
pygame.display.init()
pygame.font.init()

# Динамическое определение разрешения экрана смартфона
info_object = pygame.display.Info()
W = info_object.current_w if info_object.current_w > 0 else 500
H = info_object.current_h if info_object.current_h > 0 else 600

# Запуск в полноэкранном режиме с автоматическим скейлингом
SCREEN = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Flappy Tabs Mobile")
FPS = 60
clock = pygame.time.Clock()

# Цветовая палитра игры
WHITE, GRAY, DARK_GRAY = (255, 255, 255), (200, 200, 200), (100, 100, 100)
SKY_BLUE, YELLOW, ORANGE = (135, 206, 235), (255, 223, 0), (255, 140, 0)
GREEN, DARK_GREEN, RED, GOLD = (34, 139, 34), (0, 100, 0), (220, 20, 60), (255, 215, 0)
PURPLE, CYAN, BLACK = (148, 0, 211), (0, 255, 255), (20, 20, 20)

# Физика птицы
GRAVITY, LIFT, BIRD_RADIUS = 0.6, -6.5, 20

# Состояния игры
MAIN_START_MENU = "MAIN_START_MENU"
IN_HATS_MENU = "IN_HATS_MENU"  
IN_MENU = "IN_MENU"
PLAYING = "PLAYING"
IN_PAUSE = "IN_PAUSE"       
DEATH_ANIMATION = "DEATH_ANIMATION"
GAME_OVER = "GAME_OVER"
WIN = "WIN"
CONFIRM_RESET = "CONFIRM_RESET"

# Кэшируем шрифты с учетом высоты экрана мобильного устройства
scale_f = H / 600.0
FONT_CACHE = {
    18: pygame.font.SysFont("arial", max(12, int(18 * scale_f))),
    20: pygame.font.SysFont("arial", max(14, int(20 * scale_f))),
    22: pygame.font.SysFont("arial", max(15, int(22 * scale_f))),
    26: pygame.font.SysFont("arial", max(18, int(26 * scale_f))),
    36: pygame.font.SysFont("arial", max(24, int(36 * scale_f))),
    44: pygame.font.SysFont("arial", max(28, int(44 * scale_f)))
}

# Список шапок 
HATS = {
    "None": {"name": "БЕЗ ШАПКИ"},
    "Crown": {"name": "КОРОНА КОРОЛЯ"},
    "Pirate": {"name": "ПИРАТСКАЯ ТРЕУГОЛКА"},
    "TopHat": {"name": "ЦИЛИНДР ДЖЕНТЛЬМЕНА"}
}

# Настройки сложностей
DIFFS = {
    "Easy": {"color": GREEN, "dist": 320},
    "Normal": {"color": YELLOW, "dist": 250},
    "Hard": {"color": RED, "dist": 210},
    "Arcade": {"gap": 150, "speed": 3.5, "dist": 260, "color": ORANGE}
}

# Структура уровней
LEVELS = {
    "Easy": [
        {"num": 1, "target": 5, "speed": 2.5, "gap": 190},
        {"num": 2, "target": 10, "speed": 2.7, "gap": 185},
        {"num": 3, "target": 15, "speed": 3.0, "gap": 180},
        {"num": 4, "target": 20, "speed": 3.2, "gap": 175},
        {"num": 5, "target": 30, "speed": 3.5, "gap": 170}
    ],
    "Normal": [
        {"num": 1, "target": 30, "speed": 4.0, "gap": 160},
        {"num": 2, "target": 45, "speed": 4.2, "gap": 155},
        {"num": 3, "target": 60, "speed": 4.5, "gap": 150},
        {"num": 4, "target": 80, "speed": 4.7, "gap": 145},
        {"num": 5, "target": 100, "speed": 5.0, "gap": 140}
    ],
    "Hard": [
        {"num": 1, "target": 100, "speed": 5.5, "gap": 115},
        {"num": 2, "target": 125, "speed": 5.8, "gap": 110},
        {"num": 3, "target": 150, "speed": 6.2, "gap": 105},
        {"num": 4, "target": 175, "speed": 6.6, "gap": 100},
        {"num": 5, "target": 200, "speed": 7.0, "gap": 95}
    ]
}

# Переменные для анимации задних фонов
cloud_x = 0
lava_pulse = 0
lava_dir = 1
hell_sparks = [[random.randint(0, W), random.randint(0, H), random.uniform(1.5, 4.0), random.randint(2, 5)] for _ in range(35)]

# МОБИЛЬНОЕ ХРАНИЛИЩЕ: Путь в изолированную песочницу Android/iOS
def get_safe_path(filename):
    if "ANDROID_ARGUMENT" in os.environ or "ANDROID_PRIVATE" in os.environ:
        try:
            from android.storage import app_storage_dir
            return os.path.join(app_storage_dir(), filename)
        except ImportError:
            pass
    return filename

def load_hi_score():
    max_score = 0
    try:
        target_dir = os.path.dirname(get_safe_path("test.json")) or "."
        for filename in os.listdir(target_dir):
            if filename.startswith("arcade_") and filename.endswith(".json"):
                with open(os.path.join(target_dir, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "score" in data and data["score"] > max_score: max_score = data["score"]
    except Exception: pass
    return max_score

game_state = MAIN_START_MENU
sel_tab = "Normal"
act_lvl = None
sel_hat = "None"  
hi_score = load_hi_score()  
scroll_y, is_dragging = 0, False

def save_arcade_progress(score, current_hi_score, final_speed):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = get_safe_path(f"arcade_{timestamp}.json")
    data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": score,
        "high_score_at_moment": max(score, current_hi_score),
        "final_speed": round(final_speed, 2)
    }
    try:
        with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception: pass

def reset_arcade_records():
    try:
        target_dir = os.path.dirname(get_safe_path("test.json")) or "."
        for filename in os.listdir(target_dir):
            if filename.startswith("arcade_") and filename.endswith(".json"): os.remove(os.path.join(target_dir, filename))
    except Exception: pass
# ЧАСТЬ 2: Отрисовка текста, кнопок, расчет цвета труб и рендеринг фонов (Мобильная версия)
def get_pipe_color(tab, lvl, score):
    if tab == "Arcade": factor = min(1.0, score / 50.0)
    else:
        base_index = 5 if tab == "Normal" else (10 if tab == "Hard" else 0)
        factor = (base_index + (lvl["num"] - 1) if lvl else 0) / 14.0
    if factor < 0.5:
        t = factor * 2.0
        r, g, b = int(34 + 221 * t), int(190 + 33 * t), int(34 - 34 * t)
    else:
        t = (factor - 0.5) * 2.0
        r, g, b = int(255 - 35 * t), int(223 - 203 * t), int(20 * t)
    
    r_val = max(0, min(255, r))
    g_val = max(0, min(255, g))
    b_val = max(0, min(255, b))
    main_color = (r_val, g_val, b_val)
    dark_color = (max(0, r_val - 50), max(0, g_val - 50), max(0, b_val - 30))
    return main_color, dark_color

def draw_background(tab, score=0):
    global cloud_x, lava_pulse, lava_dir, hell_sparks
    mode = tab
    if tab == "Arcade": mode = "Easy" if score < 15 else ("Normal" if score < 35 else "Hard")
    
    if mode == "Easy":
        SCREEN.fill((175, 230, 255))
        cloud_x = (cloud_x + 0.4) % W
        for i in range(3):
            o = i * 200
            cx = int((cloud_x + o) % (W + 100)) - 50
            pygame.draw.circle(SCREEN, WHITE, (cx, int(H * 0.2)), int(H * 0.058))
            pygame.draw.circle(SCREEN, WHITE, (cx + 25, int(H * 0.18)), int(H * 0.066))
            pygame.draw.circle(SCREEN, WHITE, (cx + 50, int(H * 0.2)), int(H * 0.05))
    elif mode == "Normal":
        for y in range(0, H, max(1, H // 300)):
            ratio = y / H
            pygame.draw.rect(SCREEN, (int(75 + 165 * ratio), int(110 * ratio), int(130 - 110 * ratio)), (0, y, W, max(1, H // 300 + 1)))
        pygame.draw.rect(SCREEN, (40, 20, 50), (int(W*0.06), H - int(H*0.2), int(W*0.12), int(H*0.2)))
        pygame.draw.rect(SCREEN, (30, 15, 40), (int(W*0.28), H - int(H*0.28), int(W*0.16), int(H*0.28)))
        pygame.draw.rect(SCREEN, (35, 15, 45), (int(W*0.64), H - int(H*0.23), int(W*0.14), int(H*0.23)))
    elif mode == "Hard":
        lava_pulse += lava_dir * 0.4
        if lava_pulse > 25 or lava_pulse < 0: lava_dir *= -1
        for y in range(0, H, 4):
            ratio = y / H
            pulse_mod = (lava_pulse / 100.0) * ratio
            r = int(25 + 140 * ratio + pulse_mod * 150)
            g = int(5 * ratio + pulse_mod * 40)
            pygame.draw.rect(SCREEN, (max(0, min(255, r)), max(0, min(255, g)), 5), (0, y, W, 4))
            
        for spark in hell_sparks:
            spark -= spark
            if spark < -10:
                spark = H + random.randint(5, 30)
                spark = random.randint(0, W)
            pygame.draw.circle(SCREEN, (255, random.randint(140, 230), 20), (int(spark), int(spark)), spark)

        for x in range(0, W, max(1, W // 120)):
            wave_y = H - int(H*0.04) + int(math.sin((x + pygame.time.get_ticks() * 0.02) * 0.05) * (H*0.01))
            pygame.draw.rect(SCREEN, (245, 75, 10), (x, wave_y, max(1, W // 120 + 1), H - wave_y))

def draw_text(text, size, color, x, y, bg_box=False):
    font = FONT_CACHE.get(size, FONT_CACHE)
    ts = font.render(text, True, color)
    rect = ts.get_rect(center=(x, y))
    if bg_box:
        box = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA).convert_alpha()
        box.fill((0, 0, 0, 160))
        SCREEN.blit(box, box.get_rect(center=(x, y)))
    SCREEN.blit(ts, rect)

def draw_btn(text, x, y, width, height, is_active, act_col=ORANGE, def_col=WHITE):
    rect = pygame.Rect(x, y, width, height)
    bg = act_col if is_active else (GRAY if rect.collidepoint(pygame.mouse.get_pos()) else def_col)
    pygame.draw.rect(SCREEN, bg, rect, border_radius=8)
    pygame.draw.rect(SCREEN, DARK_GRAY, rect, width=2, border_radius=8)
    draw_text(text, 18, (0, 0, 0), x + width // 2, y + height // 2, bg_box=False)
    return rect
# ЧАСТЬ 3: Логика и отрисовка игровых классов (Bird и Pipe) (Мобильная версия)
class Bird:
    def __init__(self):
        self.x, self.y = int(W * 0.2), H // 2
        self.radius = int(H * 0.033) if H > 0 else BIRD_RADIUS
        self.gravity = GRAVITY * (H / 600.0)
        self.lift = LIFT * (H / 600.0)
        self.velocity, self.angle, self.is_dead = 0, 0, False
        self.flap_count = 0
        self.sz = self.radius * 6
        self.surface = pygame.Surface((self.sz, self.sz), pygame.SRCALPHA).convert_alpha()

    def start_death(self):
        if not self.is_dead: self.is_dead, self.velocity = True, -10 * (H / 600.0)

    def draw(self):
        self.surface.fill((0, 0, 0, 0))  
        cx, cy = self.sz // 2, self.sz // 2 + int(self.radius * 0.5)
        self.flap_count += 0.25
        wing_offset = int(math.sin(self.flap_count) * (self.radius * 0.35)) if not self.is_dead else 5

        pygame.draw.circle(self.surface, (180, 140, 0), (cx, cy), self.radius + 2)
        pygame.draw.circle(self.surface, (255, 220, 0), (cx, cy), self.radius)
        pygame.draw.circle(self.surface, (255, 245, 150), (cx - int(self.radius*0.2), cy + int(self.radius*0.3)), int(self.radius * 0.6))
        pygame.draw.ellipse(self.surface, (180, 140, 0), (cx - int(self.radius*0.8), cy - int(self.radius*0.4) + wing_offset, int(self.radius*0.9), int(self.radius*0.8)))
        pygame.draw.ellipse(self.surface, WHITE, (cx - int(self.radius*0.7), cy - int(self.radius*0.3) + wing_offset, int(self.radius*0.7), int(self.radius*0.6)))
        pygame.draw.circle(self.surface, (0, 0, 0), (cx + int(self.radius*0.4), cy - int(self.radius*0.3)), int(self.radius*0.35))
        pygame.draw.circle(self.surface, WHITE, (cx + int(self.radius*0.4), cy - int(self.radius*0.3)), int(self.radius*0.3))
        pygame.draw.circle(self.surface, (0, 0, 0), (cx + int(self.radius*0.45), cy - int(self.radius*0.3)), int(self.radius*0.15))
        pygame.draw.circle(self.surface, WHITE, (cx + int(self.radius*0.35), cy - int(self.radius*0.4)), int(self.radius*0.075))
        pygame.draw.polygon(self.surface, (180, 140, 0), [(cx + int(self.radius*0.7), cy - int(self.radius*0.2)), (cx + int(self.radius*1.4), cy), (cx + int(self.radius*0.7), cy + int(self.radius*0.15))])
        pygame.draw.polygon(self.surface, (255, 140, 0), [(cx + int(self.radius*0.7), cy - int(self.radius*0.15)), (cx + int(self.radius*1.3), cy), (cx + int(self.radius*0.7), cy + int(self.radius*0.1))])
        pygame.draw.polygon(self.surface, (180, 140, 0), [(cx + int(self.radius*0.6), cy + int(self.radius*0.1)), (cx + int(self.radius*1.2), cy + int(self.radius*0.2)), (cx + int(self.radius*0.6), cy + int(self.radius*0.35))])
        pygame.draw.polygon(self.surface, (255, 90, 0), [(cx + int(self.radius*0.6), cy + int(self.radius*0.15)), (cx + int(self.radius*1.1), cy + int(self.radius*0.2)), (cx + int(self.radius*0.6), cy + int(self.radius*0.3))])

        if sel_hat == "Crown":
            pygame.draw.polygon(self.surface, (210, 160, 0), [(cx - 16, cy - 16), (cx - 16, cy - 30), (cx - 8, cy - 22), (cx, cy - 32), (cx + 8, cy - 22), (cx + 16, cy - 30), (cx + 16, cy - 16)])
            pygame.draw.polygon(self.surface, GOLD, [(cx - 14, cy - 17), (cx - 14, cy - 27), (cx - 7, cy - 20), (cx, cy - 29), (cx + 7, cy - 20), (cx + 14, cy - 27), (cx + 14, cy - 17)])
            pygame.draw.circle(self.surface, RED, (cx - 14, cy - 17), 2)
            pygame.draw.circle(self.surface, RED, (cx, cy - 17), 2)
            pygame.draw.circle(self.surface, RED, (cx + 14, cy - 17), 2)
        elif sel_hat == "Pirate":
            pygame.draw.ellipse(self.surface, BLACK, (cx - 22, cy - 21, 44, 10))
            pygame.draw.polygon(self.surface, BLACK, [(cx - 18, cy - 17), (cx + 18, cy - 17), (cx, cy - 33)])
            pygame.draw.circle(self.surface, WHITE, (cx, cy - 22), 3)
        elif sel_hat == "TopHat":
            pygame.draw.ellipse(self.surface, BLACK, (cx - 20, cy - 20, 40, 6))
            pygame.draw.rect(self.surface, BLACK, (cx - 14, cy - 42, 28, 24))
            pygame.draw.rect(self.surface, RED, (cx - 14, cy - 22, 28, 4))

        current_angle = self.angle if self.is_dead else max(-30, min(65, int(-self.velocity * (5.5 * (600.0 / H)))))
        rs = pygame.transform.rotate(self.surface, current_angle)
        SCREEN.blit(rs, rs.get_rect(center=(int(self.x), int(self.y))))

    def update(self):
        self.velocity += self.gravity; self.y += self.velocity
        if self.is_dead: self.angle += 12
        else:
            if self.y - self.radius < 0 or self.y + self.radius > H: return True
        return False

    def jump(self):
        if not self.is_dead: self.velocity = self.lift

class Pipe:
    def __init__(self, last_top=None):
        self.x = W
        if sel_tab == "Arcade": 
            self.gap = int(DIFFS["Arcade"]["gap"] * (H / 600.0))
            self.speed = DIFFS["Arcade"]["speed"] * (W / 500.0)
        else: 
            self.gap = int(act_lvl["gap"] * (H / 600.0))
            self.speed = act_lvl["speed"] * (W / 500.0)
            
        self.width = int(70 * (W / 500.0))
        self.passed = False
        mn, mx = int(60 * (H / 600.0)), H - self.gap - int(60 * (H / 600.0))
        if (sel_tab == "Hard" or sel_tab == "Arcade") and last_top is not None:
            mn, mx = max(mn, last_top - int(60 * (H / 600.0))), min(mx, last_top + int(90 * (H / 600.0)))
        if mn > mx: mn, mx = mx, mn
        self.top = random.randint(mn, mx)
        self.bottom = H - (self.top + self.gap)

    def draw(self, score_current=0):
        color, dark_color = get_pipe_color(sel_tab, act_lvl, score_current)
        border_h = int(20 * (H / 600.0))
        pygame.draw.rect(SCREEN, color, (self.x, 0, self.width, self.top))
        pygame.draw.rect(SCREEN, dark_color, (self.x - 4, self.top - border_h, self.width + 8, border_h))
        pygame.draw.rect(SCREEN, color, (self.x, H - self.bottom, self.width, self.bottom))
        pygame.draw.rect(SCREEN, dark_color, (self.x - 4, H - self.bottom, self.width + 8, border_h))

    def update(self): self.x -= self.speed

    def collide(self, bird):
        if bird.is_dead: return False
        if bird.x + bird.radius > self.x and bird.x - bird.radius < self.x + self.width:
            if bird.y - bird.radius < self.top or bird.y + bird.radius > H - self.bottom: return True
        return False
# ЧАСТЬ 4А: Адаптивное меню, Гардероб и Списки уровней (Мобильная версия)
def main():
    global sel_tab, act_lvl, game_state, hi_score, scroll_y, is_dragging, sel_hat
    bird, pipes, score = Bird(), [], 0
    
    # Адаптивные динамические координаты рамки (в процентах от ширины и высоты)
    win_x = int(W * 0.08)
    win_y = int(H * 0.26)
    win_w = int(W * 0.84)
    win_h = int(H * 0.58)
    
    while True:
        if game_state == MAIN_START_MENU:
            SCREEN.fill(SKY_BLUE)
            draw_text("FLAPPY TABS", 44, WHITE, W // 2, H // 2 - int(H * 0.2))
            btn_start_game = draw_btn("УРОВНИ", W // 2 - int(W * 0.25), H // 2 - int(H * 0.04), int(W * 0.5), int(H * 0.08), False, ORANGE)
            btn_hats_menu = draw_btn("ШАПКИ", W // 2 - int(W * 0.25), H // 2 + int(H * 0.07), int(W * 0.5), int(H * 0.08), False, YELLOW)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_start_game.collidepoint(event.pos): game_state = IN_MENU; scroll_y = 0
                    elif btn_hats_menu.collidepoint(event.pos): game_state = IN_HATS_MENU
        elif game_state == IN_HATS_MENU:
            SCREEN.fill(SKY_BLUE)
            draw_text("ГАРДЕРОБ ШАПОК", 36, WHITE, W // 2, int(H * 0.08))
            pygame.draw.rect(SCREEN, (50, 50, 50), (win_x, win_y, win_w, win_h), border_radius=15, width=3)
            item_h = int(win_h * 0.16)
            hat_btns = [(draw_btn(HATS[k]["name"], win_x + int(win_w*0.05), win_y + int(win_h*0.05) + (i * int(item_h * 1.2)), int(win_w*0.9), item_h, sel_hat == k, GOLD), k) for i, k in enumerate(HATS.keys())]
            btn_back_to_start = draw_btn("НАЗАД", win_x + int(win_w*0.05), win_y + win_h - int(H * 0.1), int(win_w*0.9), int(H * 0.07), False, GRAY)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_back_to_start.collidepoint(event.pos): game_state = MAIN_START_MENU
                    for btn_h, key in hat_btns:
                        if btn_h.collidepoint(event.pos): sel_hat = key
        elif game_state == IN_MENU:
            SCREEN.fill(SKY_BLUE)
            draw_text("ВЫБОР УРОВНЯ", 36, WHITE, W // 2, int(H * 0.05))
            
            tab_w = int(W * 0.22)
            tab_h = int(H * 0.05)
            btn_t_easy = draw_btn("EASY", int(W*0.04), int(H*0.14), tab_w, tab_h, sel_tab == "Easy", GREEN, WHITE)
            btn_t_norm = draw_btn("NORMAL", int(W*0.28), int(H*0.14), tab_w, tab_h, sel_tab == "Normal", YELLOW, WHITE)
            btn_t_hard = draw_btn("HARD", int(W*0.52), int(H*0.14), tab_w, tab_h, sel_tab == "Hard", RED, WHITE)
            btn_t_arc = draw_btn("ARCADE", int(W*0.76), int(H*0.14), tab_w, tab_h, sel_tab == "Arcade", ORANGE, WHITE)
            btn_menu_back = draw_btn("НАЗАД", win_x, win_y + win_h + int(H*0.02), win_w, int(H*0.06), False, GRAY)
            
            pygame.draw.rect(SCREEN, (50, 50, 50), (win_x, win_y, win_w, win_h), border_radius=15, width=3)
            lvl_btns, btn_start_arc, btn_reset_arc = [], None, None
            
            if sel_tab == "Arcade":
                draw_text("БЕСКОНЕЧНЫЙ РЕЖИМ", 22, WHITE, W // 2, win_y + int(win_h*0.1))
                draw_text(f"Ваш рекорд: {hi_score}", 20, GOLD, W // 2, win_y + int(win_h*0.22))
                btn_reset_arc = draw_btn("ОЧИСТИТЬ РЕКОРД", W // 2 - int(W*0.25), win_y + int(win_h*0.35), int(W*0.5), int(H*0.06), False, RED, WHITE)
                btn_start_arc = draw_btn("ЗАПУСТИТЬ АРКАДУ", W // 2 - int(W*0.3), win_y + int(win_h*0.55), int(W*0.6), int(H*0.09), False, ORANGE)
            else:
                draw_text(f"Уровни сложности [{sel_tab.upper()}]:", 22, WHITE, W // 2, win_y - int(H*0.03))
                SCREEN.set_clip(pygame.Rect(win_x + 3, win_y + 3, win_w - 6, win_h - 6))
                
                step_h = int(H * 0.11)
                btn_item_h = int(H * 0.08)
                for i, lvl in enumerate(LEVELS[sel_tab]):
                    lvl_btns.append((draw_btn(f"Уровень {lvl['num']} (Цель: {lvl['target']})", win_x + int(win_w*0.05), win_y + int(win_h*0.04) + (i * step_h) + scroll_y, int(win_w*0.9), btn_item_h, False), lvl))
                SCREEN.set_clip(None)
                
                total_content_h = len(LEVELS[sel_tab]) * step_h + int(win_h*0.08)
                slider_x = win_x + win_w - int(W*0.04)
                pygame.draw.rect(SCREEN, (40, 40, 40, 100), (slider_x, win_y + 10, int(W*0.025), win_h - 20), border_radius=6)
                handle_h = max(30, int((win_h / total_content_h) * win_h))
                scroll_ratio = -scroll_y / (total_content_h - win_h + 30) if total_content_h > win_h else 0
                handle_y = win_y + 10 + int(scroll_ratio * (win_h - handle_h - 20))
                mx, my = pygame.mouse.get_pos()
                handle_color = GRAY if pygame.Rect(slider_x, handle_y, int(W*0.025), handle_h).collidepoint((mx, my)) or is_dragging else WHITE
                pygame.draw.rect(SCREEN, handle_color, (slider_x, handle_y, int(W*0.025), handle_h), border_radius=6)
                if is_dragging:
                    relative_y = max(0, min(win_h - handle_h - 20, my - win_y - 10 - handle_h // 2))
                    scroll_y = int(-(relative_y / (win_h - handle_h - 20)) * (total_content_h - win_h + 30))
                max_scroll = -max(0, total_content_h - win_h + 30)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not sel_tab == "Arcade" and pygame.Rect(slider_x, handle_y, int(W*0.025), handle_h).collidepoint(event.pos): is_dragging = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1: is_dragging = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not is_dragging:
                    mx, my = event.pos
                    if btn_menu_back.collidepoint((mx, my)): game_state = MAIN_START_MENU
                    elif btn_t_easy.collidepoint((mx, my)): sel_tab = "Easy"; scroll_y = 0
                    elif btn_t_norm.collidepoint((mx, my)): sel_tab = "Normal"; scroll_y = 0
                    elif btn_t_hard.collidepoint((mx, my)): sel_tab = "Hard"; scroll_y = 0
                    elif btn_t_arc.collidepoint((mx, my)): sel_tab = "Arcade"; scroll_y = 0
                    if sel_tab == "Arcade":
                        if btn_start_arc and btn_start_arc.collidepoint(event.pos):
                            act_lvl = {"num": "Arcade", "target": 999999}
                            DIFFS["Arcade"]["speed"] = 3.5
                            bird, score, game_state = Bird(), 0, PLAYING; pipes = [Pipe()]
                        elif btn_reset_arc and btn_reset_arc.collidepoint(event.pos): game_state = CONFIRM_RESET
                    else:
                        if pygame.Rect(win_x, win_y, win_w, win_h).collidepoint(event.pos):
                            for btn_lvl, lvl in lvl_btns:
                                if btn_lvl.collidepoint(event.pos):
                                    act_lvl = lvl
                                    bird, score, game_state = Bird(), 0, PLAYING; pipes = [Pipe()]; break
# ЧАСТЬ 4Б: Игровой процесс, Финал и Точка запуска (Мобильная версия)
        elif game_state == CONFIRM_RESET:
            SCREEN.fill(SKY_BLUE)
            ov = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha(); ov.fill((0, 0, 0, 160)); SCREEN.blit(ov, (0, 0))
            pygame.draw.rect(SCREEN, (30, 30, 30), (int(W*0.1), H // 2 - int(H*0.15), int(W*0.8), int(H*0.25)), border_radius=12)
            pygame.draw.rect(SCREEN, RED, (int(W*0.1), H // 2 - int(H*0.15), int(W*0.8), int(H*0.25)), width=3, border_radius=12)
            draw_text("Хотите ли вы удалить", 22, WHITE, W // 2, H // 2 - int(H*0.08))
            draw_text("свой рекорд?", 22, WHITE, W // 2, H // 2 - int(H*0.03))
            btn_yes = draw_btn("ДА", W // 2 - int(W*0.25), H // 2 + int(H*0.03), int(W*0.2), int(H*0.06), False, RED, WHITE)
            btn_no = draw_btn("НЕТ", W // 2 + int(W*0.05), H // 2 + int(H*0.03), int(W*0.2), int(H*0.06), False, GREEN, WHITE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_yes.collidepoint(event.pos): reset_arcade_records(); hi_score = 0; game_state = IN_MENU
                    elif btn_no.collidepoint(event.pos): game_state = IN_MENU
                    
        elif game_state == PLAYING:
            draw_background(sel_tab, score=score)
            for p in pipes: p.draw(score_current=score)
            bird.draw()
            
            # Кнопка-квадрат для паузы в левом верхнем углу (без текста)
            pause_size = int(H * 0.055)
            btn_pause_menu = pygame.Rect(int(W * 0.04), int(H * 0.04), pause_size, pause_size)
            bg_col = GRAY if btn_pause_menu.collidepoint(pygame.mouse.get_pos()) else WHITE
            pygame.draw.rect(SCREEN, bg_col, btn_pause_menu, border_radius=8)
            pygame.draw.rect(SCREEN, DARK_GRAY, btn_pause_menu, width=2, border_radius=8)
            
            # Отрисовка двух вертикальных полосок значка паузы || внутри кнопки
            line_w = max(2, int(pause_size * 0.12))
            line_h = int(pause_size * 0.45)
            line_y = btn_pause_menu.centery - line_h // 2
            gap = max(4, int(pause_size * 0.15))
            
            pygame.draw.rect(SCREEN, (0, 0, 0), (btn_pause_menu.centerx - gap - line_w, line_y, line_w, line_h))
            pygame.draw.rect(SCREEN, (0, 0, 0), (btn_pause_menu.centerx + gap, line_y, line_w, line_h))
            
            lbl = f"Счет: {score} (Рекорд: {hi_score}) | Скр: {int(DIFFS['Arcade']['speed'])}" if sel_tab == "Arcade" else f"Счет: {score} / {act_lvl['target']} | Скр: {act_lvl['speed']}"
            draw_text(lbl, 26, WHITE, W // 2, int(H*0.06), bg_box=False)
            draw_text(f"Режим: {sel_tab.upper()}", 20, DIFFS[sel_tab]["color"], W // 2, int(H*0.12), bg_box=True)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_pause_menu.collidepoint(event.pos):
                        game_state = IN_PAUSE
                    else:
                        bird.jump()
                        
            hit_edge = bird.update()
            if hit_edge: bird.start_death(); game_state = DEATH_ANIMATION
            if len(pipes) == 0 or pipes[-1].x < DIFFS[sel_tab if sel_tab == "Arcade" else "Normal"]["dist"]: pipes.append(Pipe(last_top=pipes[-1].top if pipes else None))
            for pipe in pipes[:]:
                pipe.update()
                if pipe.collide(bird): bird.start_death(); game_state = DEATH_ANIMATION
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True; score += 1
                    if sel_tab == "Arcade":
                        DIFFS["Arcade"]["speed"] = min(15.0, DIFFS["Arcade"]["speed"] + 0.25)
                        for p in pipes: p.speed = DIFFS["Arcade"]["speed"]
                        if score > hi_score: hi_score = score
                    else:
                        if score >= act_lvl["target"]: game_state = WIN
                if pipe.x + pipe.width < 0: pipes.remove(pipe)
                
        elif game_state == IN_PAUSE:
            ov = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha(); ov.fill((0, 0, 0, 140)); SCREEN.blit(ov, (0, 0))
            pygame.draw.rect(SCREEN, (30, 30, 30), (int(W*0.1), H // 2 - int(H*0.16), int(W*0.8), int(H*0.32)), border_radius=15)
            pygame.draw.rect(SCREEN, GRAY, (int(W*0.1), H // 2 - int(H*0.16), int(W*0.8), int(H*0.32)), width=3, border_radius=15)
            
            draw_text("ПАУЗА ИГРЫ", 26, GOLD, W // 2, H // 2 - int(H*0.09))
            btn_resume = draw_btn("ПРОДОЛЖИТЬ", W // 2 - int(W*0.3), H // 2 - int(H*0.02), int(W*0.6), int(H*0.06), False, GREEN, WHITE)
            btn_quit_to_menu = draw_btn("ВЫЙТИ В МЕНЮ", W // 2 - int(W*0.3), H // 2 + int(H*0.06), int(W*0.6), int(H*0.06), False, RED, WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_resume.collidepoint(event.pos):
                        game_state = PLAYING
                    elif btn_quit_to_menu.collidepoint(event.pos):
                        game_state = IN_MENU 
                        
        elif game_state == DEATH_ANIMATION:
            draw_background(sel_tab, score=score)
            for p in pipes: p.draw(score_current=score)
            bird.draw()
            if bird.update() or bird.y > H + 50:
                game_state = GAME_OVER
                if sel_tab == "Arcade": save_arcade_progress(score, hi_score, DIFFS["Arcade"]["speed"]); hi_score = max(score, hi_score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
        elif game_state in [GAME_OVER, WIN]:
            draw_background(sel_tab, score=score)
            ov = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha(); ov.fill((0, 0, 0, 130)); SCREEN.blit(ov, (0, 0))
            title = "УРОВЕНЬ ПРОЙДЕН!" if game_state == WIN else "ИГРА ОКОНЧЕНА"
            sub = f"Результат в Аркаде: {score} (Рекорд: {hi_score})" if sel_tab == "Arcade" else f"Вы завершили Уровень {act_lvl['num']} ({sel_tab.upper()})"
            btn_t = "ПОПРОБОВАТЬ СНОВА" if (sel_tab == "Arcade" or game_state == GAME_OVER) else "СЛЕДУЮЩИЙ УРОВЕНЬ"
            draw_text(title, 44, GOLD if game_state == WIN else RED, W // 2, H // 2 - int(H * 0.12), bg_box=False)
            draw_text(sub, 22, WHITE, W // 2, H // 2 - int(H * 0.05), bg_box=False)
            btn_act = draw_btn(btn_t, W // 2 - int(W * 0.3), H // 2 + int(H * 0.03), int(W * 0.6), int(H * 0.07), False)
            btn_to_menu = draw_btn("В ГЛАВНОЕ МЕНЮ", W // 2 - int(W * 0.3), H // 2 + int(H * 0.13), int(W * 0.6), int(H * 0.07), False, GRAY)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_to_menu.collidepoint(event.pos): game_state = MAIN_START_MENU
                    elif btn_act.collidepoint(event.pos):
                        if game_state == GAME_OVER or sel_tab == "Arcade":
                            if sel_tab == "Arcade": DIFFS["Arcade"]["speed"] = 3.5
                            bird, score, game_state = Bird(), 0, PLAYING; pipes = [Pipe()]
                        elif game_state == WIN and sel_tab != "Arcade":
                            current_num = act_lvl["num"]
                            if current_num < len(LEVELS[sel_tab]):
                                act_lvl = LEVELS[sel_tab][current_num]
                                bird, score, game_state = Bird(), 0, PLAYING; pipes = [Pipe()]
                            else: game_state = IN_MENU

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
