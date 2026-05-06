from djitellopy import Tello
import pygame
import time

tello = Tello()
tello.connect()
print("Battery:", tello.get_battery())
tello.takeoff()

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Tello Control")

speed = 50
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    lr = 0
    fb = 0
    ud = 0
    yaw = 0

    if keys[pygame.K_LEFT]:  lr = -speed
    if keys[pygame.K_RIGHT]: lr = speed
    if keys[pygame.K_UP]:    fb = speed
    if keys[pygame.K_DOWN]:  fb = -speed
    if keys[pygame.K_w]:     ud = speed
    if keys[pygame.K_s]:     ud = -speed
    if keys[pygame.K_a]:     yaw = -speed
    if keys[pygame.K_d]:     yaw = speed
    if keys[pygame.K_l]:
        tello.land()
        running = False

    tello.send_rc_control(lr, fb, ud, yaw)
    time.sleep(0.05)

tello.land()
pygame.quit()