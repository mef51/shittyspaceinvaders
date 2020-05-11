import pygame as pg
import sys, time, os
import random
import pandas as pd
from math import sin, cos

pg.init()
clock = pg.time.Clock()
pg.font.init()
assetdir = 'assets/'
extradir = 'extra/'

pg.mixer.init()
pg.mixer.music.load('music.mp3')
pg.mixer.music.play()

pewsound = pg.mixer.Sound('pew.wav')
pewsound.set_volume(0.4)
diesound = pg.mixer.Sound('die.wav')
owsound = pg.mixer.Sound('ow.wav')
owsound.set_volume(0.3)

size = width, height = 800, 600
speed = [1, 1] # x, y speed

black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0

screen = pg.display.set_mode(size)

# text
title       = pg.image.load("TitleCard.png")
titlerect   = title.get_rect()
mohtext     = pg.font.SysFont('Arial', 30).render('Code by MOHAMMED', True, white)
keegtext    = pg.font.SysFont('Arial', 30).render('Art by KEEGAN', True, white)
spacetocont = pg.font.SysFont('Arial', 20).render('Press space to start...', True, white)
spacetoplay = pg.font.SysFont('Arial', 20).render('Press space to play again...', True, white)
healthtext  = pg.font.SysFont('Arial', 20).render('Health: ', True, white)
losetext    = pg.font.SysFont('Arial Bold', 100).render('YOU LOSE BITCH', True, white)
wintext     = pg.font.SysFont('Arial Bold', 100).render('YOU WIN!!!!', True, white)

# title screen
screen.fill(black)
screen.blit(title, (0,0))
screen.blit(mohtext, (width/2-200, height/2))
screen.blit(keegtext, (width/2-200, height/2+50))
screen.blit(spacetocont, (width/2-200, height/2+150))
pg.display.flip()

bulletspeed = -0.5
aliensx, aliensy = 10, 5
alienoffset = (150, 50)
alienspacing = 10
bulletcount = 0
playerhealth = 3

def setup():
	global bulletspeed, aliensx, aliensy, alienspacing, alienoffset, bulletcount, playerhealth
	rows = []
	for i, asset in enumerate(os.listdir(assetdir)):
		if asset == 'extra':
			continue
		row = { 'name': asset.split('.')[0] }
		row['img'] = pg.image.load(assetdir + asset)
		row['rect'] = row['img'].get_rect()
		row['vx'] = 0
		row['vy'] = 0

		if row['name'] == 'Player':
			row['type'] = 'plyr'
			row['rect'].x = width/2
			row['rect'].y = height - row['rect'].height - 30
			row['vx'] = 1
			row['health'] = playerhealth
			rows.append(row)

		if row['name'] == 'Health':
			for h in range(0, playerhealth):
				row = { 'name': 'health' +  str(h) }
				row['img'] = pg.image.load(assetdir + asset)
				row['rect'] = row['img'].get_rect()
				row['type'] = 'indctr'
				row['rect'].x = 65 + h*(row['rect'].width + 5)
				row['rect'].y = height - row['rect'].height - 5
				rows.append(row)

		if row['name'] == 'bullet':
			row['name'] = 'bullet' + str(bulletcount)
			row['type'] = 'wpn'
			row['vy'] = bulletspeed
			bulletcount += 1
			rows.append(row)

		if 'barrier' in row['name']:
			row['name']   = 'Barrier' + str(1)
			row['type']   = 'barrier'
			row['img']    = pg.image.load(assetdir + 'barrier6.png')
			row['rect']   = row['img'].get_rect()
			row['rect'].x = width/2
			row['rect'].y = height-200
			row['health'] = 6
			rows.append(row)

		# if row['name'] == 'Alien1':
		# 	row['type'] = 'alien'

		if row['name'] == 'Alien2':
			for j in range(0, aliensx):
				for k in range(0, aliensy):
					row = { 'name': asset.split('.')[0] + str(j) + str(k)}
					row['type']   = 'alien'
					row['img']    = pg.image.load(assetdir + asset)
					row['rect']   = row['img'].get_rect()
					row['rect'].x = j*(alienspacing+row['rect'].width) + alienoffset[0]
					row['rect'].y = k*(alienspacing+row['rect'].height) + alienoffset[1]
					row['posx']   = j
					row['posy']   = k
					row['xo']     = row['rect'].x
					rows.append(row)

		# if row['name'] == 'Alien3':
		# 	row['type'] = 'alien'
	return pd.DataFrame(rows)

assets = setup()
assets = assets.set_index('name')
t = 0 # ms
bps = 2 # bullets per second
lastbullet_t = 0

# states
started = False
lost    = False
won     = False

def checkcollision(a, b):
	return (b.x <= a.x < b.x + b.width) and (b.y <= a.y < b.y + b.height)

while True:
	dt = clock.tick(60)
	t += dt
	for event in pg.event.get():
		if event.type == pg.QUIT: sys.exit()

	if started and not lost and not won: # main game
		# player (left) paddle
		keys = pg.key.get_pressed()
		if keys[pg.K_w]:
			won = True
		if keys[pg.K_r]:
			lost = True
		if keys[pg.K_LEFT]:
			assets.loc['Player', 'rect'] = assets.loc['Player', 'rect'].move(-1*dt, 0)
		if keys[pg.K_RIGHT]:
			assets.loc['Player', 'rect'] = assets.loc['Player', 'rect'].move(1*dt, 0)
		if keys[pg.K_SPACE] and (t > lastbullet_t + 1000/bps):
			pewsound.play()
			row = { 'name': 'bullet' + str(bulletcount) }
			row['img'] = pg.image.load(assetdir + 'bullet.png')
			row['rect'] = row['img'].get_rect()
			row['rect'].x = assets.loc['Player', 'rect'].x + assets.loc['Player', 'rect'].width/2 - 1
			row['rect'].y = assets.loc['Player', 'rect'].y - assets.loc['Player', 'rect'].height + 50
			row['vx'] = 0
			row['vy'] = bulletspeed
			row['type'] = 'wpn'
			df = pd.DataFrame([row])
			df = df.set_index('name')
			bulletcount += 1
			assets = pd.concat([assets, df])
			lastbullet_t = t

		# propagate bullets, delete when off screen
		for key, bullet in assets[assets.type == 'wpn'].iterrows():
			assets.loc[key, 'rect'] = assets.loc[key, 'rect'].move(0, assets.loc[key, 'vy']*dt)
			if assets.loc[key, 'rect'].y < -10 or assets.loc[key, 'rect'].y > height+10:
				assets = assets.drop(key)

		# gyrate aliens
		for ai, alien in assets.loc[assets.type == 'alien'].iterrows():
			if alien['posy'] % 2 == 0:
				dx = 100*cos(0.001*t)
				assets.loc[ai, 'rect'].x = assets.loc[ai, 'xo'] + dx
			if alien['posy'] % 2 == 1:
				dx = 100*sin(0.001*t)
				assets.loc[ai, 'rect'].x = assets.loc[ai, 'xo'] + dx

		# aliens shoot
		for ai, alien in assets.loc[assets.type == 'alien'].iterrows():
			# each alien has a `pshoot` percent chance of shooting per tick
			pshoot = 0.01 # 0.001
			if random.uniform(0, 1) < pshoot:
				pewsound.play()
				row = { 'name': 'alien_bullet' + str(bulletcount) }
				row['img'] = pg.image.load(assetdir + 'bullet.png')
				row['rect'] = row['img'].get_rect()
				row['rect'].x = assets.loc[ai, 'rect'].x + assets.loc[ai, 'rect'].width/2 - 1
				row['rect'].y = assets.loc[ai, 'rect'].y - assets.loc[ai, 'rect'].height + 50
				row['vx'] = 0
				row['vy'] = -bulletspeed
				row['type'] = 'wpn'
				df = pd.DataFrame([row])
				df = df.set_index('name')
				bulletcount += 1
				assets = pd.concat([assets, df])

		# check collision, super slow lol
		if len(assets[assets.type == 'wpn']) > 1:
			for ai, alien in assets.loc[assets.type == 'alien'].iterrows():
				for bi, bullet in assets[assets.type == 'wpn'].iterrows():
					# if checkcollision(bullet['rect'], alien['rect']) and 'alien' not in bi:
					if bullet['rect'].colliderect(alien['rect']) and 'alien' not in bi:
						diesound.play()
						try:
							assets = assets.drop(ai)
							assets = assets.drop(bi)
						except KeyError:
							pass

						if len(assets[assets.type == 'alien']) <= 0:
							won = True

					if assets.loc['Player', 'rect'].colliderect(bullet['rect']) and 'alien' in bi:
						owsound.play()
						assets.loc['Player', 'health'] -= 1
						try:
							assets = assets.drop(bi)
							assets = assets.drop('health' + str(int(assets.loc['Player', 'health'])))
						except KeyError:
							pass
						if assets.loc['Player', 'health'] <= 0:
							lost = True

					for bari, barrier in assets[assets.type == 'barrier'].iterrows():
						if barrier['rect'].colliderect(bullet['rect']) and 'alien' in bi:
							owsound.play()
							try:
								assets = assets.drop(bi)
							except KeyError:
								pass
							assets.loc[bari, 'health'] -= 1
							if assets.loc[bari, 'health'] > 0:
								health = assets.loc[bari, 'health']
								assets.loc[bari, 'img'] = pg.image.load(assetdir + extradir + 'barrier{}.png'.format(int(health)))
								assets.loc[bari, 'rect'] = assets.loc[bari, 'img'].get_rect()
								assets.loc[bari, 'rect'].x = width/2
								assets.loc[bari, 'rect'].y = height-200
							else:
								assets = assets.drop(bari)

		# draw
		screen.fill(black)
		screen.blit(healthtext, (0, height-25))
		for i, asset in assets.iterrows():
			screen.blit(asset['img'], asset['rect'])
		pg.display.flip()
	elif not started and not won and not lost: # title
		keys = pg.key.get_pressed()
		if keys[pg.K_SPACE]:
			started = True
	elif started and lost and not won: # lose screen
		pg.mixer.music.stop()
		screen.blit(losetext, (width/2-300, 300))
		screen.blit(spacetoplay, (width/2-200, height/2+150))

		pg.display.flip()

		keys = pg.key.get_pressed()
		assets = setup()
		assets = assets.set_index('name')
		if keys[pg.K_SPACE]:
			pg.mixer.music.rewind()
			pg.mixer.music.play()
			lost    = False
			won     = False
			started = False
	elif started and won and not lost: # win screen
		screen.blit(wintext, (width/2-300, 300))
		screen.blit(spacetoplay, (width/2-200, height/2+150))
		pg.display.flip()

		keys = pg.key.get_pressed()
		assets = setup()
		assets = assets.set_index('name')
		if keys[pg.K_SPACE]:
			pg.mixer.music.rewind()
			pg.mixer.music.play()
			lost    = False
			won     = False
			started = False
