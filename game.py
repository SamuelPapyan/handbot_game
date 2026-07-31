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
port_available = True
print(sys.platform, SERIAL_PORT)

try:
    ser = serial.Serial(SERIAL_PORT, 115200)
    print("Port is available: Using handbot.")
except (serial.SerialException, OSError):
    port_available = False
    print("Port is not available: Using keyboards.")


WIDTH = 600
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HandBot Game")

font = pygame.font.SysFont(None, 48)

clock = pygame.time.Clock()

SKY_BLUE = (173,216,230)
BROWN = (100,70,30)
WHITE = (255,255,255)


HAND_WIDTH = 120
HAND_HEIGHT = 75

COIN_SIZE = 75

HAND_SPEED = 4
COIN_SPEED = 2

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
            frame_size = img.resize((width, height))
            frame_bytes = frame_rgba.tobytes()

            pygame_surface = pygame.image.fromstring(
                frame_bytes, img.size, "RGBA"
            )
            frames.append(pygame_surface)
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    return frames

hand_image = load_image("hand.png", HAND_WIDTH, HAND_HEIGHT)
coin_image = load_image("coin_gif.gif", COIN_SIZE, COIN_SIZE)
raw_frames = load_gif_frames("coin_gif.gif", COIN_SIZE, COIN_SIZE)
coin_gif = [pygame.transform.scale(frame, (COIN_SIZE, COIN_SIZE)) for frame in raw_frames]

current_frame = 0
animation_speed = 100
last_update = pygame.time.get_ticks()

hand_image.set_colorkey(WHITE)
coin_image.set_colorkey((252, 237, 187))

player = pygame.Rect(
    WIDTH // 2 - HAND_WIDTH // 2,
    HEIGHT - HAND_HEIGHT - 10,
    HAND_WIDTH,
    HAND_HEIGHT
)

coins = []
timer = 0

while running:
    screen.fill(SKY_BLUE)
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    
    if port_available:
        # Using HandBot
        if (ser.in_waiting > 0):
            direction = ser.readline().decode().strip()

        if direction == "MOVED_LEFT":
            if player.x - HAND_SPEED >= 0:
                player.x -= HAND_SPEED
        elif direction == "MOVED_RIGHT":
            if player.x + HAND_SPEED <= WIDTH - HAND_WIDTH:
                player.x += HAND_SPEED
    else:
        # Using keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if player.x - HAND_SPEED >= 0:
                player.x -= HAND_SPEED
        elif keys[pygame.K_RIGHT]:
            if player.x + HAND_SPEED <= WIDTH - HAND_WIDTH:
                player.x += HAND_SPEED
    
    timer += 1
    if timer % 120 == 0:
        x = random.randint(0, WIDTH - COIN_SIZE)
        coin = pygame.Rect(x, -COIN_SIZE, COIN_SIZE, COIN_SIZE)
        coins.append(coin)

    for coin in coins:
        coin.y += COIN_SPEED
        
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1
        elif coin.top > HEIGHT - COIN_SIZE - 10:
            coins.remove(coin)

    if now - last_update > animation_speed:
        current_frame = (current_frame + 1) % len(coin_gif)
        last_update = now

    screen.blit(hand_image, player)

    pygame.draw.rect(screen, BROWN, (0, HEIGHT-10, WIDTH, 10))
    for coin in coins:
        screen.blit(coin_gif[current_frame], coin)
    score_text = font.render("Score: " + str(score), True, (255,255,0))
    screen.blit(score_text, (50, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()