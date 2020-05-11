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

pewsound   = pg.mixer.Sound('pew.wav')
diesound   = pg.mixer.Sound('die.wav')
owsound    = pg.mixer.Sound('ow.wav')
smashsound = pg.mixer.Sound('smash.wav')
pewsound.set_volume(0.4)
owsound.set_volume(0.3)
smashsound.set_volume(0.5)

size = width, height = 800, 600
speed = [1, 1] # x, y speed

black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0

screen = pg.display.set_mode(size)
pg.display.set_caption("Shitty Space Invaders")
# text
title       = pg.image.load("TitleCard.png")
titlerect   = title.get_rect()
mohtext     = pg.font.SysFont('Arial', 30).render('Code by MOHAMMED', True, white)
keegtext    = pg.font.SysFont('Arial', 30).render('Art by KEEGAN', True, white)
spacetocont = pg.font.SysFont('Arial', 20).render('Press space to start...', True, white)
entertoplay = pg.font.SysFont('Arial', 20).render('Press enter to play again...', True, white)
healthtext  = pg.font.SysFont('Arial', 20).render('Health: ', True, white)
timetext    = pg.font.SysFont('Arial', 20).render('Time: ', True, white)
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
alienspacing = (10, 10)
numbarriers = 3
barrierspacing = 250
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
			for b in range(0, numbarriers):
				row           = { 'name': 'Barrier' + str(int(b)) }
				row['type']   = 'barrier'
				row['img']    = pg.image.load(assetdir + 'barrier6.png')
				row['rect']   = row['img'].get_rect()
				row['rect'].x = 150 + b*barrierspacing
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
					imgs = [assetdir + 'Alien2.png']
					row['img']    = pg.image.load(random.choice(imgs))
					row['rect']   = row['img'].get_rect()
					row['rect'].x = j*(alienspacing[0]+row['rect'].width)  + alienoffset[0]
					row['rect'].y = k*(alienspacing[1]+row['rect'].height) + alienoffset[1]
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
	timescore  = pg.font.SysFont('Arial', 20).render(str(int(t/100)), True, white)

	for event in pg.event.get():
		if event.type == pg.QUIT: sys.exit()

	if started and not lost and not won: # main game
		# player (left) paddle
		keys = pg.key.get_pressed()
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
		aliensleft = len(assets[assets.type == 'alien'])
		for ai, alien in assets.loc[assets.type == 'alien'].iterrows():
			period = 0.001
			# amplitude = 5000 / (aliensleft) # 100
			amplitude = 100 # 100
			s = 1#(aliensx*aliensy) / aliensleft
			if alien['posy'] % 2 == 0:
				dx = amplitude*cos(period*t)
				assets.loc[ai, 'rect'].x = assets.loc[ai, 'xo'] + s*dx
			if alien['posy'] % 2 == 1:
				dx = amplitude*sin(period*t)
				assets.loc[ai, 'rect'].x = assets.loc[ai, 'xo'] + s*dx

		# aliens shoot
		pshoot = 0.001 + 0.019/aliensleft # 0.001
		for ai, alien in assets.loc[assets.type == 'alien'].iterrows():
			# each alien has a `pshoot` percent chance of shooting per tick
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

		# bullet collisions
		if len(assets[assets.type == 'wpn']) > 1:
			for bi, bullet in assets[assets.type == 'wpn'].iterrows():
				alienrects = assets.loc[assets.type == 'alien']['rect']
				collisioni = bullet['rect'].collidelist(alienrects)

				if collisioni > -1 and 'alien' not in bi:
					ai = assets.index[assets.type == 'alien'].tolist()[collisioni]
					diesound.play()
					try:
						assets = assets.drop(ai)
						assets = assets.drop(bi)
					except KeyError:
						pass

					if len(assets[assets.type == 'alien']) <= 0:
						won = True
					continue

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
					continue

				for bari, barrier in assets[assets.type == 'barrier'].iterrows():
					if barrier['rect'].colliderect(bullet['rect']):
						try:
							assets = assets.drop(bi)
						except KeyError:
							pass

						if 'alien' in bi:
							smashsound.play()
							assets.loc[bari, 'health'] -= 1
							if assets.loc[bari, 'health'] > 0:
								health = assets.loc[bari, 'health']
								assets.loc[bari, 'img'] = pg.image.load(assetdir + extradir + 'barrier{}.png'.format(int(health)))
							else:
								assets = assets.drop(bari)

		# draw
		screen.fill(black)
		screen.blit(healthtext, (0, height-25))
		screen.blit(timetext, (650, height-25))
		screen.blit(timescore, (700, height-25))
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
		screen.blit(entertoplay, (width/2-200, height/2+150))

		pg.display.flip()

		keys = pg.key.get_pressed()
		assets = setup()
		assets = assets.set_index('name')
		if keys[pg.K_RETURN]:
			pg.mixer.music.rewind()
			pg.mixer.music.play()
			t            = 0
			lastbullet_t = 0
			lost         = False
			won          = False

	elif started and won and not lost: # win screen
		screen.blit(wintext, (width/2-300, 300))
		screen.blit(entertoplay, (width/2-200, height/2+150))
		pg.display.flip()

		keys = pg.key.get_pressed()
		assets = setup()
		assets = assets.set_index('name')
		if keys[pg.K_RETURN]:
			pg.mixer.music.rewind()
			pg.mixer.music.play()
			t            = 0
			lastbullet_t = 0
			lost         = False
			won          = False
