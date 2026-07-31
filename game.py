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

SKY_BLUE = (173,216,230)
BROWN = (100,70,30)
WHITE = (255,255,255)


SPEEDUP_WIDTH = 90
SPEEDUP_HEIGHT = 64

PLAYER_SIZE = 80

COIN_SIZE = 56

PLAYER_SPEED = 4
COIN_SPEED = 2
SPEEDUP_SPEED = 3
SPEEDUP_MAX_TIME = 600

GROUND_SIZE = 64

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

player_gif = {
    "idle_left": load_gif_frames("sprites/player/idle_left.gif", PLAYER_SIZE, PLAYER_SIZE),
    "idle_right": load_gif_frames("sprites/player/idle_right.gif", PLAYER_SIZE, PLAYER_SIZE),
    "run_left": load_gif_frames("sprites/player/run_left.gif", PLAYER_SIZE, PLAYER_SIZE),
    "run_right": load_gif_frames("sprites/player/run_right.gif", PLAYER_SIZE, PLAYER_SIZE),
}
bg_img = load_image("bg.png", WIDTH, HEIGHT)
ground_img = load_image("ground.png", GROUND_SIZE, GROUND_SIZE)
speedup_icon_img = load_image("speedup_icon.png", 32, 32)

current_frame = 0
player_current_frame = 0
speedup_current_frame = 0
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
speedup = None
timer = 0

fps_per_coin = 120

def show_speedup_timer_ui(s, time):
    max_size = 180
    max_bar_size = max_size - 4
    pygame.draw.rect(s, "#ffffff", (WIDTH-(max_size + 20), 15, max_size, 20))
    pygame.draw.rect(s, "#ff0000", (WIDTH-(max_bar_size * (time / SPEEDUP_MAX_TIME) + 20), 17, max_bar_size * (time / SPEEDUP_MAX_TIME), 16))
    pygame.draw.circle(s, "#ffffff", (WIDTH -32, 25), 20)
    s.blit(speedup_icon_img, (WIDTH-45, 10))

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
    
    if speedup != None:
        speedup.y += SPEEDUP_SPEED
        if player.colliderect(speedup):
            speedup = None
            speedup_timer = SPEEDUP_MAX_TIME
        elif speedup.top > HEIGHT - SPEEDUP_HEIGHT - GROUND_SIZE:
            speedup = None

    if now - last_update > animation_speed:
        current_frame = (current_frame + 1) % len(coin_gif)
        player_current_frame = (player_current_frame + 1) % 4
        if speedup != None:
            speedup_current_frame = (speedup_current_frame + 1) % len(speedup_gif)
        last_update = now

    screen.blit(player_gif[player_current_state][player_current_frame], player)

    pygame.draw.rect(screen, BROWN, (0, HEIGHT-10, WIDTH, 10))
    for i in range(0, WIDTH, GROUND_SIZE):
        screen.blit(ground_img, (i, HEIGHT - GROUND_SIZE))
    for coin in coins:
        screen.blit(coin_gif[current_frame], coin)
    if speedup != None:
        screen.blit(speedup_gif[speedup_current_frame], speedup)
    score_text = font.render("Score: " + str(score), True, (255,255,0))
    screen.blit(score_text, (50, 50))

    if speedup_timer > 0:
        show_speedup_timer_ui(screen, speedup_timer)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()