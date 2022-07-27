from scene import *
from PIL import Image
import sound
import random

GAME_READY = 0
GAME_PLAY = 1
GAME_DYING = 2
GAME_DEAD = 3

BACK_IMGS = ['plf:Tile_Snow']


class GameEnvironment(object):
	def __init__(self, x, y, w, h):
		self.playfield = Rect(x, y, w, h)
		self.gravity =  int(h *-3.000)			
		self.scroll = int(h * 0.300)			
		self.float_max = int(h * 0.300)			
		self.float_min = int(h * 0.050)		
		self.jump = int(h * 0.800)		
		self.gap = int(h * 0.360)			
		self.ground_height = 0 			
		self.tower_width = int(h * 0.140)		
		self.tower_cap = int(h * 0.065)			
		self.tower_gap = (self.playfield.w - (self.tower_width * 2)) / 2
		self.tower_min_height = self.tower_cap
		self.tower_max_height = self.playfield.h - self.ground_height - self. tower_cap - self.tower_gap
		self.player_width = int(h * 0.09)			
		self.player_height = int(h * 0.09)			
		self.player_x = int(h * 0.200)			
		self.player_y = self.playfield.h / 2 + self.ground_height	
		self.back_min = int(h * 0.1)			
		self.back_max = int(h * 0.5)			
		self.text_x = w / 2
		self.text_1_y = 0.9 * h
		self.text_2_y = 0.6 * h
		self.text_3_y = 0.4 * h
		self.font_size = int(h * 0.064)			
		self.font = 'ChalkboardSE-Bold'
		self.score = 0
		self.best = 0
		self.crash = False
		self.gametime = 0
		self.deadtime = 0
		self.state = GAME_READY

class Player(object):
	def __init__(self, x, y, w, h):
		self.bounds = Rect(x, y, w, h)
		img = Image.open('emj:Baby_Chick_1').transpose(Image.FLIP_LEFT_RIGHT)
		self.img = load_pil_image(img)
		self.velocity = 0
		self.jumped = False

	def draw(self):
		tint(1.00, 1.00, 1.00)
		image(self.img, self.bounds.x, self.bounds.y, self.bounds.w, self.bounds.h)

class BackgroundSprite(object):
	def __init__(self, env):
		self.env = env
		self.velocity = env.scroll / 4
		self.set_random_bounds()
		self.set_random_image()

	def set_random_image(self):
		img = Image.open(BACK_IMGS[random.randint(0, len(BACK_IMGS) - 1)])
		self.velocity = random.randint(int(self.env.scroll / 4), int(self.env.scroll / 2))
		if(random.random() > 0.5):
			img = img.transpose(Image.FLIP_LEFT_RIGHT)
			self.velocity *= -1
		self.img = load_pil_image(img)

	def set_random_bounds(self):
		env = self.env
		size = random.randint(env.back_min, env.back_max)
		y = random.randint(env.ground_height, env.playfield.max_y)
		if self.velocity < 0:
			x = env.playfield.min_x
		else:
			x = env.playfield.max_x
		self.bounds = Rect(x, y, size, size)

	def draw(self):
		tint(1,1,1)
		image(self.img, self.bounds.x, self.bounds.y, self.bounds.w, self.bounds.h)

class Ground(object):
	def __init__(self, x, y, w, h):
		self.bounds = Rect(x, y, w, h)

	def draw(self):
		stroke_weight(4)
		stroke(0.00, 0.00, 0.00)
		fill(0.50, 0.25, 0.00)
		rect(self.bounds.x, self.bounds.y, self.bounds.w, self.bounds.h)

class Tower(object):
	def __init__(self, x, env):
		self.x = x
		self.env = env
		self.create_towers_and_caps()

	def set_x(self, x):
		self.x = x
		self.lower_tower.x = x + 6
		self.lower_cap.x = x
		self.upper_tower.x = x + 6
		self.upper_cap.x = x

	def right(self):
		return self.lower_tower.max_x

	def left(self):
		return self.lower_tower.min_x

	def create_towers_and_caps(self):
		self.passed = False
		height = random.randint(self.env.tower_min_height, self.env.tower_max_height)
		self.lower_tower = Rect(self.x + 6, self.env.ground_height, self.env.tower_width - 12, height)
		self.lower_cap = Rect(self.x, self.env.ground_height + height - self.env.tower_cap, self.env.tower_width, self.env.tower_cap)
		self.upper_tower =  Rect(self.x + 6, height + self.env.gap, self.env.tower_width - 12, self.env.playfield.h - height + self.env.gap)
		self.upper_cap = Rect(self.x, height + self.env.gap, self.env.tower_width, self.env.tower_cap)

	def intersects(self, r):
		return self.lower_tower.intersects(r) or self.upper_tower.intersects(r)

	def draw(self):
		stroke_weight(4)
		stroke(0.00, 0.50, 0.25)
		stroke(0.20, 0.20, 0.00)
		fill(0.35, 0.60, 0.00)
		rect(self.lower_tower.x, self.lower_tower.y, self.lower_tower.w, self.lower_tower.h)
		rect(self.lower_cap.x, self.lower_cap.y, self.lower_cap.w, self.lower_cap.h)
		rect(self.upper_tower.x, self.upper_tower.y, self.upper_tower.w, self.upper_tower.h)
		rect(self.upper_cap.x, self.upper_cap.y, self.upper_cap.w, self.upper_cap.h)

class Game(object):
	def __init__(self, x, y, w, h):
		self.env = GameEnvironment(x, y, w, h)
		self.game_setup()

	def game_setup(self):
		self.env.score = 0
		self.env.crash = False
		self.env.state = GAME_READY
		self.load_highscore()
		self.create_game_objects()
	
	def load_highscore(self):
		try:
			with open('.Flappy Chick_best', 'r') as f:
				self.env.best = int(f.read())
		except:
			self.env.best = 0
	
	def save_highscore(self):
		with open('.Flappy Chick_best', 'w') as f:
			f.write(str(self.env.best))

	def create_game_objects(self):
		self.player = Player(self.env.player_x, self.env.player_y, self.env.player_width, self.env.player_height)
		self.ground = Ground(self.env.playfield.x, self.env.playfield.y, self.env.playfield.w, self.env.ground_height)
		self.towers = []
		x = self.env.playfield.w * 2
		for t in range(3):
			self.towers.append(Tower(x, self.env))
			x += self.env.tower_width + self.env.tower_gap
		self.bubbles = []
		for t in range(10):
			d = random.randint(0, 20)
		self.background_sprites = []
		for t in range(3):
			self.background_sprites.append(BackgroundSprite(self.env))

	def move_player(self, dt):
		if(self.env.state == GAME_DEAD):
			return
		elif((self.env.state == GAME_READY) and (self.player.bounds.y < (self.env.playfield.h / 2)) or self.player.jumped):
			self.player.jumped = False
			self.player.velocity = self.env.jump
		else:
			self.player.velocity = self.player.velocity + self.env.gravity * dt
		self.player.bounds.y += self.player.velocity * dt

	def move_towers(self, dt):
		if(self.env.state == GAME_PLAY):
			move = self.env.scroll * dt
			for tower in self.towers:
				tower.set_x(tower.x - move)
				if tower.right() < self.env.playfield.x:
					tower.set_x(self.env.playfield.w + self.env.tower_gap)
					tower.create_towers_and_caps()

	def move_background_sprites(self, dt):
		if(self.env.state == GAME_READY) or (self.env.state == GAME_PLAY):
			for sprite in self.background_sprites:
				move = sprite.velocity * dt
				sprite.bounds.x -= move
				if(sprite.bounds.max_x < self.env.playfield.min_x) or (sprite.bounds.min_x > self.env.playfield.max_x):
					sprite.set_random_image()
					sprite.set_random_bounds()

	def update_score(self):
		if(self.env.state == GAME_PLAY):
			for tower in self.towers:
				if tower.passed == False:
					if tower.left() < self.player.bounds.max_x:
						tower.passed = True
						self.env.score += 1
						sound.play_effect('Coin_2')

	def player_dead(self):
		self.env.state = GAME_DEAD
		self.env.dead_time = self.env.game_time
		if self.env.score > self.env.best:
			self.env.best = self.env.score
			sound.play_effect('voice:female_new_highscore')
			self.save_highscore()
		else:
			sound.play_effect('voice:female_game_over')

	def collision_detect(self):
		if(self.env.state == GAME_PLAY):
			if self.player.bounds.min_y < self.ground.bounds.max_y:
				sound.play_effect('Crashing')
				self.env.crash = True
				self.player_dead()
		elif(self.env.state == GAME_DYING):
			if self.player.bounds.min_y < self.ground.bounds.max_y:
				self.player_dead()			
		if self.env.state == GAME_PLAY:
			if self.player.bounds.min_y > self.env.playfield.max_y:
					self.env.crash = True
					self.env.state = GAME_DYING
			else:
				for tower in self.towers:
					if tower.intersects(self.player.bounds):
						sound.play_effect('Crashing')
						self.env.crash = True
						self.env.state = GAME_DYING

	def text_shadow(self, s, y):
		tint(0, 0, 0)
		text(s, self.env.font, self.env.font_size, self.env.text_x + 4, y - 4)
		tint(1, 1, 1)
		text(s, self.env.font, self.env.font_size, self.env.text_x, y)

	def draw(self):
		if(self.env.crash):
			background(1, 1, 1)
			self.env.crash = False
		else:
			background(0.34, 0.75, 0.9)
			for sprite in self.background_sprites:
				sprite.draw()
			self.ground.draw()
			for tower in self.towers:
				tower.draw()
			self.player.draw()
			tint(0, 0, 0)
			if(self.env.state == GAME_READY):
				self.text_shadow("Tap for Start!", self.env.text_2_y)
			elif((self.env.state == GAME_PLAY) or (self.env.state == GAME_DYING) or (self.env.state == GAME_READY)):
				self.text_shadow(str(int(self.env.score)), self.env.text_1_y)
			elif(self.env.state == GAME_DEAD):
				self.text_shadow("Score : " + str(int(self.env.score)), self.env.text_2_y)
				self.text_shadow("Best  : " + str(int(self.env.best)), self.env.text_3_y)

	def loop(self, dt, t):
		self.env.game_time = t
		self.move_player(dt)
		self.move_towers(dt)
		self.move_background_sprites(dt)
		self.update_score()
		self.collision_detect()
		self.draw()

	def screen_tapped(self):
		if(self.env.state == GAME_READY):
			self.env.state = GAME_PLAY
		if(self.env.state == GAME_PLAY):
			self.player.jumped = True
			sound.play_effect('arcade:Jump_4')
		elif(self.env.state == GAME_DEAD):
			if(self.env.dead_time + 0.5 < self.env.game_time):
				self.game_setup()			
				
class MyScene(Scene):
	def setup(self):
		self.game = Game(self.bounds.x, self.bounds.y, self.bounds.w, self.bounds.h)

	def draw(self):
		self.game.loop(self.dt, self.t)

	def touch_began(self, touch):
		self.game.screen_tapped()

run(MyScene(), PORTRAIT)
