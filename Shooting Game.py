from scene import *
import random
import sound
import time
import threading
from game_menu import MenuScene
from math import sin, cos, pi
A = Action


normal_texture = Texture('spc:PlayerShip2Green')
hit_texture = Texture('spc:PlayerShip3Damage2')
laser_texture1 = Texture('spc:LaserRed13')
laser_texture2 = Texture('spc:LaserRed5')
laser_texture3 = Texture('spc:LaserRed3')


class Meteor (SpriteNode):
	def __init__(self, r=8, **kwargs):
		img = random.choice(['spc:MeteorBrownBig1', 'spc:MeteorBrownBig2'])
		SpriteNode.__init__(self, img, **kwargs)
		self.size = (r*10,r*10)
		self.destroyed = False
		self.coined = False

class bigMeteor(SpriteNode):
	def __init__(self, r=11, **kwargs):
		img = random.choice(['spc:MeteorGrayBig1', 'spc:MeteorGrayBig2'])
		SpriteNode.__init__(self, img, **kwargs)
		self.size = (r*15,r*15)
		self.destroyed = False
		self.hitNumber = 0
						
class Coin (SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, 'spc:StarGold', **kwargs)

class Enemy (SpriteNode):	
	def __init__(self, r=11, **kwargs):
		img = random.choice(['spc:EnemyBlack1', 'spc:EnemyBlack4'])
		SpriteNode.__init__(self, img, **kwargs)
		self.size = (r*6,r*6)
		self.destroyed = False
	
class enemyLaser(SpriteNode):
		def __init__(self, **kwargs):
			SpriteNode.__init__(self, laser_texture2, **kwargs)
		
class shootingStar(SpriteNode):
	def __init__(self, r=11, **kwargs):
			SpriteNode.__init__(self, 'spc:Fire18', **kwargs)
			self.size = (r*0.7,r*11)
	
class Point(SpriteNode):
	def __init__(self, r=11, **kwargs):
			SpriteNode.__init__(self, 'spc:TurretBaseSmall', **kwargs)
			self.size = (r*3,r*3)
	
class Game(Scene):
	def setup(self):
		self.background_color = '#153066'
		self.player = SpriteNode(normal_texture)
		self.player.position = (self.size.w/2, 70)
		self.add_child(self.player)
		self.items = []
		self.lasersStop = False
		self.lasersNum = 1
		self.point = Point(parent=self)
		self.point.position = (self.player.position.x,self.player.position.y-10)
		self.add_child(self.point)
		score_font = ('Futura', 40)
		self.score_label = LabelNode('0', score_font, parent=self)
		self.score_label.position = (self.size.w/2, self.size.h - 70)
		self.score = 0
		self.hud_hearts = [SpriteNode('spc:PlayerLife2Green', position = (565 + i * 32, self.size.h - 110), scale=0.7, parent=self) for i in range(3)]
		self.pause_button = SpriteNode('iow:pause_32', position=(32, self.size.h-32), parent=self)
		self.load_highscore()
		self.show_start_menu()
		
	def load_highscore(self):
		try:
			with open('.Star War_highscore', 'r') as f:
				self.highscore = int(f.read())
		except:
			self.highscore = 0
	
	def save_highscore(self):
		with open('.Star War_highscore', 'w') as f:
			f.write(str(self.highscore))
		
	def new_game(self):
		for item in self.items:
			item.remove_from_parent()
		self.items = []
		self.lasers = []
		self.lasersStop = False
		self.super = False
		self.lasersNum = 1
		self.score = 0
		self.score_label.text = '0'
		self.player.position = (self.size.w/2, 70)
		self.player.texture = normal_texture
		self.lives_left = 3
		for h in self.hud_hearts:
			h.alpha = 1
		self.speed = 1.0
		self.point.position = (self.player.position.x,self.player.position.y-10)		
		
	def continue_game(self):
		temp = 0
		for item in self.items:
			for item in self.items:
				if isinstance(item, shootingStar):
					pass
				else:
					if temp <= 20:
						item.remove_from_parent()
						self.destroy_bigMeteor(item)
						temp += 1
					else:
						item.remove_from_parent()					
		self.items = []
		self.lasers = []
		self.lasersStop = False
		self.super = False
		self.player.texture = normal_texture
		self.speed = 1.0
		temp = 0
			
	def update(self):
		self.check_item_collisions()
		self.check_laser_collisions()
		if random.random() < 0.07:
			self.spawn_item()
			
	def touch_began(self, touch):
		x, y = touch.location
		if x < 48 and y > self.size.h - 48:
			self.show_pause_menu()
			
	def touch_moved(self, touch):
		self.player.position = touch.location
		self.point.position = (self.player.position.x,self.player.position.y-10)
		if random.random() < 0.15:
			self.shoot_laser()
			if random.random() < 0.25:
				sound.play_effect('digital:Laser1')
	
	def check_item_collisions(self):
		player_hitbox = Rect(self.point.position.x, self.point.position.y, 10, 10)
		for item in list(self.items):
			if item.frame.intersects(player_hitbox):
				if isinstance(item, Coin):
					self.collect_item(item)
					sound.play_effect('digital:PowerUp4')
				elif isinstance(item, Meteor):
					if item.destroyed:
						if item.coined:
							self.collect_item(item, 10)
							sound.play_effect('digital:PowerUp8')
						else:
							continue
					else:
						self.player_hit()
				elif isinstance(item, bigMeteor):
					if item.destroyed:
						item.remove_from_parent()
						self.items.remove(item)
						if self.lasersNum < 4:
							self.lasersNum += 1
						sound.play_effect('digital:PowerUp12')
					else:
						self.player_hit()
				elif isinstance(item, enemyLaser):
					self.player_hit()
				elif not item.parent:
					item.remove_from_parent()
					self.items.remove(item)
					
	def check_laser_collisions(self):
		for laser in list(self.lasers):
				if not laser.parent:
					self.lasers.remove(laser)
					continue
				for item in self.items:
					if isinstance(item, Coin) or isinstance(item, shootingStar) or isinstance(item, enemyLaser):
						continue
					if item.destroyed:
								continue
					if laser.position in item.frame:
						if isinstance(item, Meteor):
							self.destroy_meteor(item)
							self.lasers.remove(laser)
							laser.remove_from_parent()
							break
						if isinstance(item, Enemy):
							self.destroy_enemy(item)
							self.lasers.remove(laser)
							laser.remove_from_parent()
							break
						if isinstance(item, bigMeteor):
							if item.hitNumber > 5 * self.lasersNum:
								self.destroy_bigMeteor(item)
								self.lasers.remove(laser)
								laser.remove_from_parent()
								break
							else:
								self.lasers.remove(laser)
								laser.remove_from_parent()
								item.hitNumber += 1
								break																		
						
	def destroy_meteor(self, meteor):
		sound.play_effect('game:Crashing')
		meteor.destroyed = True
		if random.random() < 0.25:
			meteor.texture = Texture('plf:HudCoin')
			meteor.coined = True
		else:
			meteor.remove_from_parent()
		for i in range(5):
			m = SpriteNode('spc:MeteorBrownMed1', parent=self)
			m.position = meteor.position + (random.uniform(-20, 20), random.uniform(-20, 20))
			angle = random.uniform(0, pi*2)
			dx, dy = cos(angle) * 80, sin(angle) * 80
			m.run_action(A.move_by(dx, dy, 0.6, TIMING_EASE_OUT))
			m.run_action(A.sequence(A.scale_to(0, 0.6), A.remove()))
			
	def destroy_bigMeteor(self, bigMeteor):
		sound.play_effect('game:Crashing')
		bigMeteor.destroyed = True
		if self.lasersNum < 4 or random.random() < 0.25:
			bigMeteor.texture = Texture('spc:PowerupBlueBolt')
		else:
			bigMeteor.remove_from_parent()
		for i in range(5):
			m = SpriteNode('spc:MeteorGrayMed1', parent=self)
			m.position = bigMeteor.position + (random.uniform(-20, 20), random.uniform(-20, 20))
			angle = random.uniform(0, pi*2)
			dx, dy = cos(angle) * 80, sin(angle) * 80
			m.run_action(A.move_by(dx, dy, 0.6, TIMING_EASE_OUT))
			m.run_action(A.sequence(A.scale_to(0, 0.6), A.remove()))
			
	def destroy_enemy(self, enemy):
		sound.play_effect('game:Crashing')
		enemy.destroyed = True
		self.score += 5
		self.score_label.text = str(self.score)
		enemy.remove_from_parent()
		for i in range(5):
			m = SpriteNode('spc:MeteorGrayTiny2', parent=self)
			m.position = enemy.position + (random.uniform(-20, 20), random.uniform(-20, 20))
			angle = random.uniform(0, pi*2)
			dx, dy = cos(angle) * 80, sin(angle) * 80
			m.run_action(A.move_by(dx, dy, 0.6, TIMING_EASE_OUT))
			m.run_action(A.sequence(A.scale_to(0, 0.6), A.remove()))		
	
	def player_hit(self):
		if self.super == True:
			return 
		else:
			self.super = True
			self.lasersStop = True
			self.lives_left -= 1
			for i, heart in enumerate(self.hud_hearts):
				heart.alpha = 1 if self.lives_left > i else 0
			if self.lives_left <= 0:
				self.point.remove_from_parent()
				self.game_over()
			else:
				sound.play_effect('game:Crashing')
				self.player.run_action(A.move_by(0, -150))
				self.point.run_action(A.move_by(0, -150))
				self.run_action(A.sequence(A.wait(2*self.speed)))
				self.continue_game()
		
	def game_over(self):
		self.player.texture = hit_texture
		if self.score > self.highscore:
			self.highscore = self.score
			sound.play_effect('voice:female_new_highscore')
			self.save_highscore()
		else:
			sound.play_effect('voice:female_game_over')
		self.paused = True
		self.menu = MenuScene('Game Over', 'Highscore: %i' % self.highscore, ['New Game'])
		self.present_modal_scene(self.menu)
		
	def spawn_item(self):
		star = shootingStar(parent=self)
		star.z_position = -1
		star.position = (random.uniform(20, self.size.w-20), self.size.h + 30)
		d = random.uniform(1.0,1.5)
		actions = [A.move_by(0, -(self.size.h + 60), d-0.9), A.remove()]
		star.run_action(A.sequence(actions))
			
		if random.random() < 0.017:
			big_meteor = bigMeteor(parent=self)
			big_meteor.position = (random.uniform(20, self.size.w-20), self.size.h + 30)
			d = random.uniform(2.0, 4.0)
			actions = [A.move_to(random.uniform(0, self.size.w), -100, d), A.remove()]
			big_meteor.run_action(A.sequence(actions))
			self.items.append(big_meteor)
			
		elif random.random() < 0.15:
			enemy = Enemy(parent=self)
			enemy.position = (random.uniform(20, self.size.w-20), self.size.h + 30)
			d = random.uniform(2.0, 4.0)
			actions = [A.move_by(0, -(self.size.h + 60), d), A.remove()]
			enemy.run_action(A.sequence(actions))
			self.items.append(enemy)			
			enemy_laser = enemyLaser(parent=self)
			enemy_laser.position = (enemy.position.x, enemy.position.y -60)
			actions2 = [A.move_by(0, -(self.size.h + 60), d-1.0), A.remove()]
			enemy_laser.run_action(A.sequence(actions2))
			self.items.append(enemy_laser)
		
		elif random.random() < 0.35:
			meteor = Meteor(parent=self)
			meteor.position = (random.uniform(20, self.size.w-20), self.size.h + 30)
			d = random.uniform(2.0, 4.0)
			actions = [A.move_to(random.uniform(0, self.size.w), -100, d), A.remove()]
			meteor.run_action(A.sequence(actions))
			self.items.append(meteor)
				
		elif random.random() < 0.85:
			coin = Coin(parent=self)
			coin.position = (random.uniform(20, self.size.w-20), self.size.h-10)
			d = random.uniform(2.0, 4.0)
			actions = [A.move_by(0, -(self.size.h + 60), d), A.remove()]
			coin.run_action(A.sequence(actions))
			self.items.append(coin)
		self.speed = min(3, self.speed + 0.005)
	
	def shoot_laser(self):
		if self.lasersStop == True:
			return
		if self.lasersNum > 0:
			if self.lasersNum == 1:	
				laser = SpriteNode('spc:LaserGreen10', parent=self)
			else:
				laser = SpriteNode('spc:LaserGreen9', parent=self)
			laser.position = self.player.position + (0, 20)
			laser.z_position = 0
			actions = [A.move_by(0, self.size.h,0.7 * self.speed), A.remove()]
			laser.run_action(A.sequence(actions))
			self.lasers.append(laser)
		
		if self.lasersNum > 1:
			laser = SpriteNode('spc:LaserGreen9', parent=self)
			laser.position = self.player.position + (45, 0)
			laser.z_position = 0
			actions = [A.move_by(0, self.size.h,0.7 * self.speed), A.remove()]
			laser.run_action(A.sequence(actions))
			self.lasers.append(laser)
		
			laser = SpriteNode('spc:LaserGreen9', parent=self)
			laser.position = self.player.position + (-45, 0)
			laser.z_position = 0
			actions = [A.move_by(0, self.size.h,0.7 * self.speed), A.remove()]
			laser.run_action(A.sequence(actions))
			self.lasers.append(laser)
		
		if self.lasersNum > 2:
			laser = SpriteNode('spc:LaserBlue7', parent=self)
			laser.position = self.player.position + (0, 20)
			laser.z_position = 0
			actions = [A.move_by(-230, self.size.h,0.7 * self.speed), A.remove()]
			laser.run_action(A.sequence(actions))
			self.lasers.append(laser)
			
			laser = SpriteNode('spc:LaserBlue7', parent=self)
			laser.position = self.player.position + (0, 20)
			laser.z_position = 0
			actions = [A.move_by(230, self.size.h,0.7* self.speed), A.remove()]
			laser.run_action(A.sequence(actions))
			self.lasers.append(laser)		
	
	def collect_item(self, item, value=1):
		item.remove_from_parent()
		self.items.remove(item)
		self.score += 1
		self.score_label.text = str(self.score)	
	
	def show_start_menu(self):
		self.paused = True
		sound.play_effect('digital:ThreeTone2')
		self.menu = MenuScene('Star War', 'Highscore: %i' % self.highscore, ['Play'])
		self.present_modal_scene(self.menu)
	
	def show_pause_menu(self):
		self.paused = True
		sound.play_effect('digital:ThreeTone2')
		self.menu = MenuScene('Paused', 'Highscore: %i' % self.highscore, ['Continue', 'New Game'])
		self.present_modal_scene(self.menu)
	
	def menu_button_selected(self, title):
		if title in ('Continue', 'New Game', 'Play'):
			sound.play_effect('digital:PowerUp7')
			self.dismiss_modal_scene()
			self.menu = None
			self.paused = False
			if title in ('New Game', 'Play'):
				self.new_game()

				
if __name__ == '__main__':
	run(Game(), PORTRAIT, show_fps=True)
