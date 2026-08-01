import pygame
import random
import os
import sys
import serial

from PIL import Image

pygame.init()
pygame.font.init()

SERIAL_PORT = "/dev/tty.usbmodem1101"


if sys.platform.startswith("darwin"):
    # MacOS port
    SERIAL_PORT = "/dev/tty.usbmodem1101"
elif sys.platform.startswith("win"):
    # Windows Port
    SERIAL_PORT = "COM3"
elif sys.platform.startswith("linux"):
    # Linux Port
    SERIAL_PORT = "/dev/ttyUSB0"

ser = None
direction = "NEUTRAL"
port_available = False
print(sys.platform, SERIAL_PORT)

# try:
#     ser = serial.Serial(SERIAL_PORT, 115200)
#     port_available = True
#     print("Port is available: Using handbot.")
# except (serial.SerialException, OSError):
#     port_available = False
#     print("Port is not available: Using keyboards.")


WIDTH = 600
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HandBot Game")

font = pygame.font.SysFont(None, 48)

clock = pygame.time.Clock()

SPEEDUP_WIDTH = 90
SPEEDUP_HEIGHT = 64

BAT_WIDTH = 80
BAT_HEIGHT = 45

HEALTH = 50

PLAYER_SIZE = 80

COIN_SIZE = 56

HEALTH_SIZE = 56

PLAYER_SPEED = 4
COIN_SPEED = 2
SPEEDUP_SPEED = 3
HEALTH_SPEED = 3
BAT_SPEED = 5

SPEEDUP_MAX_TIME = 600

GROUND_SIZE = 64

hp = 10
score = 0

HERE = os.path.dirname(os.path.abspath(__file__))
running = True

def load_image(filename, width, height):
    path = os.path.join(HERE, filename)
    img = Image.open(path)
    img = img.convert("RGBA")
    img = img.resize((width, height))

    raw = img.tobytes()
    return pygame.image.fromstring(raw, img.size, "RGBA")

def load_gif_frames(filename, width, height):
    path = os.path.join(HERE, filename)
    img = Image.open(path)
    frames = []

    try:
        while True:
            frame_rgba = img.convert("RGBA")
            frame_bytes = frame_rgba.tobytes()

            pygame_surface = pygame.image.fromstring(
                frame_bytes, img.size, "RGBA"
            )
            frames.append(pygame_surface)
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    return [pygame.transform.scale(frame, (width, height)) for frame in frames]

coin_gif = load_gif_frames("coin_gif.gif", COIN_SIZE, COIN_SIZE)
speedup_gif = load_gif_frames("sprites/speedup/speedup.gif", SPEEDUP_WIDTH, SPEEDUP_HEIGHT)
bat_gif = load_gif_frames("sprites/bat/bat.gif", BAT_WIDTH, BAT_HEIGHT)

player_gif = {
    "idle_left": load_gif_frames("sprites/player/idle_left.gif", PLAYER_SIZE, PLAYER_SIZE),
    "idle_right": load_gif_frames("sprites/player/idle_right.gif", PLAYER_SIZE, PLAYER_SIZE),
    "run_left": load_gif_frames("sprites/player/run_left.gif", PLAYER_SIZE, PLAYER_SIZE),
    "run_right": load_gif_frames("sprites/player/run_right.gif", PLAYER_SIZE, PLAYER_SIZE),
}
bg_img = load_image("bg.png", WIDTH, HEIGHT)
ground_img = load_image("ground.png", GROUND_SIZE, GROUND_SIZE)
speedup_icon_img = load_image("speedup_icon.png", 32, 32)
hp_icon_img = load_image("hp.png", 26, 24)
health_img = load_image("hp.png", HEALTH_SIZE, HEALTH_SIZE)

current_frame = 0
player_current_frame = 0
speedup_current_frame = 0
bat_current_frame = 0
player_current_state = "idle_left"

speedup_timer = 0

animation_speed = 100
last_update = pygame.time.get_ticks()

player = pygame.Rect(
    WIDTH // 2 - PLAYER_SIZE // 2,
    HEIGHT - PLAYER_SIZE - GROUND_SIZE,
    PLAYER_SIZE,
    PLAYER_SIZE
)

coins = []
bats = []
speedup = None
health = None
timer = 0

fps_per_coin = 120

def show_speedup_timer_ui(s, time):
    max_size = 180
    max_bar_size = max_size - 4
    pygame.draw.rect(s, "#ffffff", (WIDTH-(max_size + 20), 15, max_size, 20))
    pygame.draw.rect(s, "#ff0000", (WIDTH-(max_bar_size * (time / SPEEDUP_MAX_TIME) + 20), 17, max_bar_size * (time / SPEEDUP_MAX_TIME), 16))
    pygame.draw.circle(s, "#ffffff", (WIDTH -32, 25), 20)
    s.blit(speedup_icon_img, (WIDTH-45, 10))

def show_health_bar(s, h):
    max_size = 144
    max_bar_size = 136
    pygame.draw.rect(s, "#ffffff", (40, 12, max_size, 22))
    pygame.draw.rect(s, "#ff0000", (45, 14, max_bar_size * (h / 10), 18))
    pygame.draw.circle(s, "#ffffff", (24, 23), 21)
    s.blit(hp_icon_img, (11, 12))
    

while running:
    screen.blit(bg_img, (0,0))
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    
    if port_available:
        # Using HandBot
        if (ser.in_waiting > 0):
            direction = ser.readline().decode().strip()

        if direction == "MOVED_LEFT":
            player_current_state = "run_right"
            if player.x - PLAYER_SPEED >= 0:
                player.x -= PLAYER_SPEED
        elif direction == "MOVED_RIGHT":
            player_current_state = "run_left"
            if player.x + PLAYER_SPEED <= WIDTH - PLAYER_SIZE:
                player.x += PLAYER_SPEED
        else:
            player_current_state = "idle_left"
    else:
        # Using keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_current_state = "run_right"
            if player.x - PLAYER_SPEED >= 0:
                player.x -= PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            player_current_state = "run_left"
            if player.x + PLAYER_SPEED <= WIDTH - PLAYER_SIZE:
                player.x += PLAYER_SPEED
        else:
            player_current_state = "idle_left"
    
    timer += 1
    if timer % fps_per_coin == 0:
        x = random.randint(0, WIDTH - COIN_SIZE)
        coin = pygame.Rect(x, -COIN_SIZE, COIN_SIZE, COIN_SIZE)
        coins.append(coin)
        COIN_SPEED + 0.1
        if fps_per_coin > 60:
            fps_per_coin -= 1
    
    if fps_per_coin < 75 and timer % (60 * 20) == 0:
        x = random.randint(0, WIDTH - SPEEDUP_WIDTH)
        speedup = pygame.Rect(x, -SPEEDUP_HEIGHT, SPEEDUP_WIDTH, SPEEDUP_HEIGHT)
    
    if fps_per_coin < 65 and timer % (60 * 40) == 0:
        x = random.randint(0, WIDTH - HEALTH_SIZE)
        health = pygame.Rect(x, -HEALTH_SIZE, HEALTH_SIZE, HEALTH_SIZE)

    if fps_per_coin < 100 and timer % (60 * 10) == 0:
        x = random.randint(0, WIDTH - BAT_WIDTH)
        bat = pygame.Rect(x, -BAT_WIDTH, BAT_WIDTH, BAT_HEIGHT)
        bats.append(bat)

    if speedup_timer > 0:
        speedup_timer -= 1
        PLAYER_SPEED = 10
    else:
        PLAYER_SPEED = 4 

    for coin in coins:
        coin.y += COIN_SPEED
        
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1
        elif coin.top > HEIGHT - COIN_SIZE - GROUND_SIZE:
            coins.remove(coin)

    for bat in bats:
        bat.y += BAT_SPEED

        if player.colliderect(bat):
            bats.remove(bat)
            hp -= 1
        elif bat.top > HEIGHT - BAT_HEIGHT - GROUND_SIZE:
            bats.remove(bat)
    
    if speedup != None:
        speedup.y += SPEEDUP_SPEED
        if player.colliderect(speedup):
            speedup = None
            speedup_timer = SPEEDUP_MAX_TIME
        elif speedup.top > HEIGHT - SPEEDUP_HEIGHT - GROUND_SIZE:
            speedup = None
    
    if health != None:
        health.y += HEALTH_SPEED
        if player.colliderect(health):
            health = None
            hp += (2 if hp + 2 <= 10 else 10 - hp)
        elif health.top > HEIGHT - HEALTH_SIZE - GROUND_SIZE:
            health = None

    if now - last_update > animation_speed:
        current_frame = (current_frame + 1) % len(coin_gif)
        player_current_frame = (player_current_frame + 1) % 4
        bat_current_frame = (bat_current_frame + 1) % len(bat_gif)
        if speedup != None:
            speedup_current_frame = (speedup_current_frame + 1) % len(speedup_gif)
        last_update = now

    screen.blit(player_gif[player_current_state][player_current_frame], player)

    for i in range(0, WIDTH, GROUND_SIZE):
        screen.blit(ground_img, (i, HEIGHT - GROUND_SIZE))
    for coin in coins:
        screen.blit(coin_gif[current_frame], coin)
    for bat in bats:
        screen.blit(bat_gif[bat_current_frame], bat)
    if speedup != None:
        screen.blit(speedup_gif[speedup_current_frame], speedup)
    if health != None:
        screen.blit(health_img, health)
    score_text = font.render("Score: " + str(score), True, (255,255,0))
    screen.blit(score_text, (50, 50))

    if speedup_timer > 0:
        show_speedup_timer_ui(screen, speedup_timer)
    show_health_bar(screen, hp)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()