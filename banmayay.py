import pygame #cho phép bạn sử dụng các module trong thư viện Pygame để xây dựng game.
from pygame import mixer #cho phép bạn truy cập trực tiếp module đó mà không cần viết pygame.mixe
from pygame.locals import * #nhập tất cả các hằng số (constants) và đối tượng cục bộ từ pygame.locals
import random # có thể được sử dụng để tạo các số ngẫu nhiên hoặc các yếu tố ngẫu nhiên khác trong game (như vị trí đối tượng, tốc độ, v.v.).

pygame.mixer.pre_init(44100, -16, 2, 512) # Dòng này định cấu hình các thông số của bộ trộn âm thanh trước khi Pygame được khởi tạo
mixer.init() # Khởi tạo mixer.init() để xử lý âm thanh
pygame.init() # Khởi tạo toàn bộ Pygame

clock = pygame.time.Clock()
fps = 60 #Thiết lập thông số FPS

screen_width = 600
screen_height = 800 #Đặt thông số màn hình
screen = pygame.display.set_mode((screen_width, screen_height)) #Khởi tạo màn hình
pygame.display.set_caption('Space War') #Đặt tiêu đề cửa sổ

#Tạo font chữ
font30 = pygame.font.SysFont('Constantia', 30) #dùng cho các văn bản nhỏ như điểm số hoặc trạng thái.
font40 = pygame.font.SysFont('Constantia', 40) # Dùng cho tiêu đề hoặc thông báo lớn hơn.

#upload âm thanh
explosion_fx = pygame.mixer.Sound("explosion.mp3")
explosion_fx.set_volume(0.25) # Điều chỉnh âm lượng của âm thanh.
explosion2_fx = pygame.mixer.Sound("explosion2.mp3")
explosion2_fx.set_volume(0.25)
laser_fx = pygame.mixer.Sound("laser.mp3")
laser_fx.set_volume(0.25) 

#Xác định các biến trò chơi
rows = 5 #Số hàng
cols = 5 #Số cột
alien_cooldown = 1000 #thời gian hồi chiêu của viên đạn (ms)
last_alien_shot = pygame.time.get_ticks() # Lưu thời điểm cuối cùng mà kẻ thù đã bắn đạn

#Đồng hồ đếm ngược 
countdown = 3 # Dùng để hiển thị một bộ đếm (3, 2, 1) trước khi trò chơi bắt đầu
last_count = pygame.time.get_ticks() # Lưu thời gian gần nhất mà bộ đếm được cập nhật

#Trạng thái kết thúc game
game_over = 0 # Lưu trạng thái của trò chơi: 0: chưa kết thúc, 1: thắng,  -1: thua

#Xác định màu sắc
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

#Tải hình ảnh lên
bg = pygame.image.load("bg.jpg")
scaled_bg = pygame.transform.scale(bg, (screen.get_width(), screen.get_height())) # Thay đổi kích thước hình nền để phù hợp màn hình
def draw_bg():
	screen.blit(scaled_bg, (0, 0)) # Vẽ hình ảnh đã tải lên màn hình.

#Hàm để tạo văn bản
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col) # Kết xuất văn bản thành một hình ảnh (Surface) có thể vẽ lên màn hình; Tham số True bật tính năng khử răng cưa (antialiasing) cho văn bản; Văn bản được vẽ với màu được chỉ định (text_col).
	screen.blit(img, (x, y)) #Vẽ hình ảnh văn bản (img) lên màn hình tại vị trí (x, y).

#Tạo lớp tàu vũ trụ
#Tạo lớp tàu vũ trụ
class Spaceship(pygame.sprite.Sprite): # Khởi tạo đối tượng Spaceship
	def __init__(self, x, y, health):
		pygame.sprite.Sprite.__init__(self)
		original_image = pygame.image.load("spaceship.png")  # Tải ảnh gốc
		scaled_width, scaled_height = 90, 90  # Kích thước mong muốn (có thể chỉnh lại)
		self.image = pygame.transform.scale(original_image, (scaled_width, scaled_height))  # Thay đổi kích thước

		#Đặt vị trí tàu vũ trụ
		self.rect = self.image.get_rect() # get_rect() trả về một đối tượng Rect chứa thông tin về vị trí và kích thước của hình ảnh.
		self.rect.center = [x, y] # Đặt tọa độ của trung tâm hình ảnh tại vị trí (x, y) được truyền vào.

		#Thiết lập chỉ số sức khoẻ 
		self.health_start = health # Lưu trữ số lượng sức khỏe ban đầu của tàu vũ trụ.
		self.health_remaining = health # Lưu trữ số lượng sức khỏe hiện tại của tàu vũ trụ.

		# Thiết lập thời gian bắn
		self.last_shot = pygame.time.get_ticks() # kiểm tra thời gian giữa các lần bắn của tàu vũ trụ.
	# cập nhật trạng thái của đối tượng mỗi khung hình


	def update(self):
		# Xác định tốc độ di chuyển của tàu.
		speed = 8
		#Thời gian cooldown giữa các lần bắn (ms).
		cooldown = 500 
		game_over = 0 #Biến dùng để kiểm tra trạng thái kết thúc game.


		#Nhận phím bấm
		key = pygame.key.get_pressed() #Lấy trạng thái của tất cả các phím trên bàn phím trong một thời điểm nhất định.
		if key[pygame.K_LEFT] and self.rect.left > 0:#Kiểm tra xem người chơi có nhấn phím mũi tên trái và tàu vũ trụ không bị chạm vào cạnh trái của màn hình.
			self.rect.x -= speed #Di chuyển tàu vũ trụ sang trái.
		if key[pygame.K_RIGHT] and self.rect.right < screen_width: #Kiểm tra xem người chơi có nhấn phím mũi tên phải và tàu vũ trụ không bị chạm vào cạnh phải của màn hình.
			self.rect.x += speed#Di chuyển tàu vũ trụ sang phải.
		if key[pygame.K_UP] and self.rect.top > 0: 
			self.rect.y -= speed  # Di chuyển tàu vũ trụ lên
		if key[pygame.K_DOWN] and self.rect.bottom < screen_height:
			self.rect.y += speed  # Di chuyển tàu vũ trụ xuống
		#ghi nhận lại thời gian hiện tại
		time_now = pygame.time.get_ticks()
		#Kiểm tra xem người chơi có nhấn phím Space (bắn đạn) và thời gian cooldown đã trôi qua đủ lâu chưa.
		if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
			laser_fx.play() #Phát âm thanh khi bắn đạn.
			bullet = Bullets(self.rect.centerx, self.rect.top) #Tạo một đối tượng đạn mới.
			bullet_group.add(bullet)#Thêm đạn vào nhóm các đối tượng đạn
			self.last_shot = time_now#Cập nhật thời gian của lần bắn hiện tại.


		#Tạo một mask từ hình ảnh của đối tượng Spaceship để sử dụng trong việc kiểm tra va chạm.
		self.mask = pygame.mask.from_surface(self.image)


		#rút thanh sức khoẻ
		pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15)) #Vẽ một thanh sức khỏe cơ bản với màu đỏ (mô phỏng cho phần sức khỏe bị mất).
		if self.health_remaining > 0: #Kiểm tra xem tàu vũ trụ còn sức khỏe không (nếu sức khỏe còn thì vẽ thanh sức khỏe).
			pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15)) #Vẽ phần sức khỏe còn lại với màu xanh.
		elif self.health_remaining <= 0: #Nếu sức khỏe của tàu vũ trụ bằng 0 hoặc nhỏ hơn, tàu bị tiêu diệt.
			explosion = Explosion(self.rect.centerx, self.rect.centery, 3) #Tạo một đối tượng vụ nổ khi tàu vũ trụ chết.			explosion_group.add(explosion) #Thêm vụ nổ vào nhóm đối tượng vụ nổ (explosion_group), để có thể cập nhật và vẽ nó lên màn hình.
			self.kill() #Xóa đối tượng tàu vũ trụ khỏi tất cả các nhóm sprite mà nó thuộc về.
			game_over = -1 #Đặt giá trị của game_over thành -1 để báo hiệu rằng người chơi đã thua (tàu vũ trụ bị tiêu diệt).
		return game_over #Trả về giá trị game_over sau khi cập nhật tình trạng trò chơi.

#Tạo lớp Bullets
class Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)#khởi tạo của lớp pygame.sprite.Sprite
		scaled_width, scaled_height = 10, 10 #định nghĩa kích thước của đạn (chiều rộng và chiều cao)
		original_image = pygame.image.load("bullet.png")
		self.image = pygame.transform.scale(original_image, (scaled_width, scaled_height))#thay đổi kích thước của hình ảnh gốc (original_image) thành kích thước mà đã định nghĩa ở trên (10x10 pixel).
		self.rect = self.image.get_rect() #tạo ra một đối tượng Rect (hình chữ nhật) bao quanh hình ảnh của đạn
		self.rect.center = [x, y] #xác định vị trí của đạn trên màn hình, nơi mà bạn muốn đạn xuất hiện khi được bắn ra

	def update(self):
		self.rect.y -= 5 #di chuyển đạn lên trên màn hình.
		if self.rect.bottom < 0: #kiểm tra nếu đạn đã ra ngoài màn hình
			self.kill()
		if pygame.sprite.spritecollide(self, alien_group, True): #kiểm tra va chạm giữa đạn (self) và các đối tượng trong nhóm alien_group.
			self.kill()#Xóa đạn khỏi trò chơi 
			explosion_fx.play() #Phát âm thanh vụ nổ mỗi khi đạn va chạm với quái vật.
			explosion = Explosion(self.rect.centerx, self.rect.centery, 2) #Tạo một đối tượng Explosion tại vị trí trung tâm của đạn (self.rect.centerx, self.rect.centery)
			explosion_group.add(explosion) #Thêm đối tượng Explosion vào nhóm explosion_group


#create Aliens class
class Aliens(pygame.sprite.Sprite): #khai báo của lớp Aliens
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self) #Khởi tạo lớp cha Sprite
		original_image = pygame.image.load("alien" + str(random.randint(1, 5)) + ".png")
		scaled_width, scaled_height = 40, 40 #xác định kích thước mới cho quái vật (40x40 pixel).
		self.image = pygame.transform.scale(original_image, (scaled_width, scaled_height)) #thay đổi kích thước của hình ảnh original_image thành kích thước mới
		self.rect = self.image.get_rect() #tạo ra một đối tượng Rect bao quanh hình ảnh của quái vật.
		self.rect.center = [x, y] #đặt vị trí của đối tượng rect (vị trí và hình dạng bao quanh quái vật) sao cho trung tâm của nó nằm tại tọa độ [x, y]
		self.move_counter = 0 #biến dùng để theo dõi số bước mà quái vật đã di chuyển
		self.move_direction = 1 #xác định hướng di chuyển của quái vật


	def update(self):
		self.rect.x += self.move_direction #di chuyển quái vật sang trái hoặc sang phải theo hướng đã được xác định
		self.move_counter += 1 #quyết định khi nào quái vật cần thay đổi hướng di chuyển.
		if abs(self.move_counter) > 75:  #nếu quái vật đã di chuyển qua 75 bước, nó sẽ thay đổi hướng di chuyển.
			self.move_direction *= -1 #Sau khi quái vật di chuyển qua 75 bước, hướng di chuyển sẽ bị đảo ngược.
			self.move_counter *= self.move_direction #đặt lại giá trị của self.move_counter sao cho bộ đếm sẽ tiếp tục tăng từ giá trị 0 theo hướng mới.

class Alien_Bullets(pygame.sprite.Sprite): #Khai báo lớp Alien_Bullets
	def __init__(self, x, y): #Phương thức khởi tạo __init__
		pygame.sprite.Sprite.__init__(self) #Khởi tạo lớp cha Sprite
		scaled_width, scaled_height = 10, 10
		original_image = pygame.image.load("alien_bullet.png") #Tải hình ảnh viên đạn của quái vật
		self.image = pygame.transform.scale(original_image, (scaled_width, scaled_height)) #Thay đổi kích thước hình ảnh viên đạn
		self.rect = self.image.get_rect() #Tạo đối tượng rect cho viên đạn
		self.rect.center = [x, y] #Đặt vị trí của viên đạn


	def update(self):
		self.rect.y += 2 # Di chuyển viên đạn xuống dưới
		if self.rect.top > screen_height: # Kiểm tra nếu viên đạn ra khỏi màn hình
			self.kill()
		# Kiểm tra va chạm với tàu vũ trụ
		if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask): 
			self.kill()
			explosion2_fx.play()
			#reduce spaceship health
			spaceship.health_remaining -= 1
			explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
			explosion_group.add(explosion)

#Tạo lớp nổ
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, size):
		pygame.sprite.Sprite.__init__(self) #Khởi tạo đối tượng Sprite
		self.images = [] #Khởi tạo danh sách lưu trữ hình ảnh vụ nổ
		#Lặp qua các ảnh vụ nổ
		for num in range(1, 6):
			img = pygame.image.load(f"exp{num}.png")
		#Thay đổi kích thước hình ảnh dựa trên kích thước vụ nổ
			if size == 1:
				img = pygame.transform.scale(img, (20, 20))
			if size == 2:
				img = pygame.transform.scale(img, (40, 40))
			if size == 3:
				img = pygame.transform.scale(img, (160, 160))
		self.images.append(img) #Thêm hình ảnh vào danh sách self.images
		self.index = 0 ##Thiết lập chỉ số ảnh ban đầu
		self.image = self.images[self.index] #Thiết lập hình ảnh của vụ nổ
		self.rect = self.image.get_rect() #Tạo đối tượng rect cho vụ nổ
		self.rect.center = [x, y]
		self.counter = 0 # Thuộc tính để kiểm soát tiến trình vụ nổ



	def update(self):
		explosion_speed = 3 # Khởi tạo tốc độ hoạt ảnh
		#Cập nhật hoạt hình vụ nổ 
		self.counter += 1 # Cập nhật bộ đếm
		#Kiểm tra thời gian và chuyển khung hình
		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]


		#Kiểm tra hoàn thành hoạt ảnh và xóa vụ nổ
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			self.kill()

spaceship_group = pygame.sprite.Group() #Tạo nhóm sprite cho tàu vũ trụ
bullet_group = pygame.sprite.Group() #Tạo nhóm sprite cho đạn
alien_group = pygame.sprite.Group() #Tạo nhóm sprite cho kẻ thù 
alien_bullet_group = pygame.sprite.Group() #Tạo nhóm sprite cho đạn của kẻ thù
explosion_group = pygame.sprite.Group() #Tạo nhóm sprite cho các vụ nổ

def create_aliens(): 
	for row in range(rows): # Duyệt qua các hàng
		for item in range(cols): #Duyệt qua các cột
			alien = Aliens(100 + item * 100, 100 + row * 70) #Tạo kẻ thù 
			alien_group.add(alien) #Thêm kẻ thù vào nhóm alien_group

create_aliens()

#Khởi tạo nhân vật người chơi
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

run = True
def reset_game():
    global game_over, countdown, last_count, spaceship, alien_group, alien_bullet_group, bullet_group, explosion_group
    game_over = 0 #Đặt lại trạng thái trò chơi 
    countdown = 3#Đặt lại bộ đếm thời gian đếm ngược trước khi bắt đầu.
    last_count = pygame.time.get_ticks() #Xóa tất cả các đối tượng tàu vũ trụ trong nhóm.

    # Đặt lại tàu vũ trụ
    spaceship_group.empty() #Xóa tất cả các đối tượng tàu vũ trụ trong nhóm.
    spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3) #Tạo lại tàu vũ trụ mới tại vị trí bắt đầu với 3 điểm máu.
    spaceship_group.add(spaceship)

        # Đặt lại người ngoài hành tinh
    alien_group.empty() #Xóa tất cả các đối tượng alien trong nhóm
    create_aliens() #Tạo lại các alien mới

    # Xóa tất cả các viên đạn và vụ nổ trong các nhóm tương ứng.
    bullet_group.empty()
    alien_bullet_group.empty()
    explosion_group.empty()

	#Vòng lặp chính của trò chơi
while run:

	clock.tick(fps) #Giới hạn tốc độ của trò chơi bằng cách đặt tần số quét

	#Vẽ nền và xử lý đếm ngược
	draw_bg()

	if countdown == 0:
		#Tạo đạn ngoài hành tinh ngẫu nhiên
		#Ghi lại thời gian hiện tại

		time_now = pygame.time.get_ticks()
		#Tạo và bắn đạn từ kẻ thù
		if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0: #Nếu thời gian trôi qua kể từ lần bắn trước của kẻ thù lâu hơn thời gian làm mát; Nếu số lượng viên đạn của kẻ thù ít hơn 5 viên và Chọn ngẫu nhiên một kẻ thù từ nhóm alien_group.
			attacking_alien = random.choice(alien_group.sprites())
			alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom) #Tạo viên đạn từ kẻ thù đã chọn.
			alien_bullet_group.add(alien_bullet) #Thêm viên đạn vào nhóm alien_bullet_group.
			last_alien_shot = time_now #Cập nhật thời gian bắn đạn cuối cùng của kẻ thù

		#Kiểm tra xem tất cả alien đã bị tiêu diệt chưa
		if len(alien_group) == 0:
			game_over = 1

		if game_over == 0:
			#Cập nhật và vẽ các đối tượng
			game_over = spaceship.update()
			#Cập nhật trạng thái tàu vũ trụ
			#update sprite groups
			bullet_group.update()
			alien_group.update()
			alien_bullet_group.update()
			#Cập nhật các nhóm đạn, kẻ thù, và đạn của kẻ thù
		#Hiển thị kết quả

		else:
			if game_over == -1: #Hiển thị thông báo "GAME OVER".
				draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
			if game_over == 1: #Hiển thị thông báo "YOU WIN".
				draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
 		#Xử lý đếm ngược (GET READY)
	if countdown > 0: #Vẽ thông báo "GET READY!" và số đếm ngược
		draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
		draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
		count_timer = pygame.time.get_ticks()
		if count_timer - last_count > 1000:
			countdown -= 1
			last_count = count_timer


	#Cập nhật và vẽ các vụ nổ
	explosion_group.update()


	# Vẽ tất cả các nhóm sprite
	spaceship_group.draw(screen)
	bullet_group.draw(screen)
	alien_group.draw(screen)
	alien_bullet_group.draw(screen)
	explosion_group.draw(screen)

	# Xử lý sự kiện
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN and game_over != 0:
				reset_game()

	pygame.display.update() # Cập nhật màn hình

pygame.quit() # Thoát trò chơi
