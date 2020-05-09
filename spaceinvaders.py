import pygame as pg
import sys, time
import random

pg.init()

pg.font.init()


size = width, height = 800, 800
speed = [1, 1] # x, y speed

black = 0, 0, 0
white = 255, 255, 255

screen = pg.display.set_mode(size)

paddlewidth = 25
paddleheight = 200
ballrad = 5


leftpaddle  = pg.Rect(10, 150, paddlewidth, paddleheight)  # left, top, width, height
rightpaddle = pg.Rect(width-10-paddlewidth, 150, paddlewidth, paddleheight)  # left, top, width, height
ball = pg.draw.circle(screen, white, (400, 400), ballrad)

pad_speed = 0.8
padlvy = 0
padrvy = 0

ballvx, ballvy = -0.5, random.randint(0, 1)
clock = pg.time.Clock()

losetext    = pg.font.SysFont('Arial Bold', 100).render('YOU LOSE BITCH', True, white)
wintext    = pg.font.SysFont('Arial Bold', 100).render('YOU WIN!!!!', True, white)
spacetocont = pg.font.SysFont('Arial', 20).render('Space to continue', True, white)
lose = False
win = False
while True:
	dt = clock.tick(60)


	for event in pg.event.get():
		if event.type == pg.QUIT: sys.exit()

	# player (left) paddle
	keys = pg.key.get_pressed()
	if keys[pg.K_UP]:
		if leftpaddle.top > 0:
			leftpaddle = leftpaddle.move(0, -pad_speed*dt)
			padlvy = -pad_speed
	if keys[pg.K_DOWN]:
		if leftpaddle.top+100 < height:
			leftpaddle = leftpaddle.move(0, pad_speed*dt)
			padlvy = pad_speed
	else:
		padlvy = 0

	# cpu paddle
	rightpaddle = rightpaddle.move(0, -pad_speed*dt if ball.top < rightpaddle.top+paddleheight/2 else pad_speed*dt)

	# move ball
	ball = ball.move(ballvx*dt, ballvy*dt)
	if ball.colliderect(leftpaddle):
		ballvx *= -1
		ballvy += padlvy
	if ball.colliderect(rightpaddle):
		ballvx *= -1
		ballvy += padlvy

	# bounds
	if ball.top < 0:
		ballvy *= -1
	if ball.top+ball.width > height:
		ballvy *= -1

	if ball.left < 0:
		lose = True
	if ball.left > width+ball.width:
		win = True

	if win or lose:
		if keys[pg.K_SPACE]:
			ball = pg.draw.circle(screen, white, (400, 400), ballrad)
			ballvx, ballvy = -0.5, random.randint(0, 1)
			lose = False
			win = False

	screen.fill(black)
	# draw shit
	if lose:
		screen.blit(losetext, (width/2-300, 300))
		screen.blit(spacetocont, (width/2-200, 420))
		ballvx, ballvy = 0, 0
	if win:
		screen.blit(wintext, (width/2-300, 300))
		screen.blit(spacetocont, (width/2-200, 420))
		ballvx, ballvy = 0, 0

	pg.draw.rect(screen, white, leftpaddle)
	pg.draw.rect(screen, white, rightpaddle)
	pg.draw.circle(screen, white, ball.center, ball.width)
	pg.display.flip()

