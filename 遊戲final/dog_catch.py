# 狗狗接球：升級版
import pygame, random, sys, time
from pygame.locals import *

#------------------------------ 設定常數 ------------------------------
WINDOWWIDTH  = 640
WINDOWHEIGHT = 480
TEXTCOLOR    = (255, 250, 250)
BACKGROUNDCOLOR = (137, 104, 205)
FPS = 100
ARTICLESIZE = 50
ARTICLEMINSPEED = 1
ARTICLEMAXSPEED = 3
ADDNEWARTICLERATE = 100  # 初始新增物件頻率 (數值越小越頻繁)
PLAYERMOVERATE = 5
LEVEL_THRESHOLD = 10   # 分數每達 10 分升一關
LEVEL_SPEED_FACTOR = 1.2  # 每升一關，物件速度乘上此因子
LEVEL_RATE_DECREASE = 10   # 每升一關，新增頻率減少此數值（最小不低於 20）

#------------------------------ 定義函式 ------------------------------
def terminate():
    pygame.quit()
    sys.exit()

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_SPACE:
                    return
                elif event.key == K_p:  # 若在等待畫面時也希望 P 鍵不作用，可拿掉這裡
                    return

def drawText(text, font, surface, x, y, align='center'):
    textobj = font.render(text, True, TEXTCOLOR)
    textrect = textobj.get_rect()
    if align == 'center':
        textrect.center = (x, y)
    elif align == 'left':
        textrect.topleft = (x, y)
    elif align == 'right':
        textrect.topright = (x, y)
    surface.blit(textobj, textrect)

#------------------------------ 初始化 pygame 和設定視窗 ------------------------------
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('狗狗接球')

#------------------------------ 設定字型 ------------------------------
font = pygame.font.SysFont(None, 32)

#------------------------------ 載入音效 ------------------------------
pygame.mixer.music.load('background.mp3')
getBallSound = pygame.mixer.Sound('sounds/catch.wav')
getBadBallSound = pygame.mixer.Sound('sounds/miss.wav')
gameSuccessSound = pygame.mixer.Sound('sounds/success.wav')
gameOverSound = pygame.mixer.Sound('sounds/gameover.wav')

#------------------------------ 載入圖片 ------------------------------
playerImage = pygame.image.load('images/dog.png').convert_alpha()
playerImage = pygame.transform.scale(playerImage, (70, 70))
playerRect = playerImage.get_rect()
tennisImage = pygame.image.load('images/tennis_ball.png').convert_alpha()
tennisImage = pygame.transform.scale(tennisImage, (40, 40))
badBallImage = pygame.image.load('images/bad_ball.png').convert_alpha()
badBallImage = pygame.transform.scale(badBallImage, (40, 40))
backgroundImage = pygame.image.load('images/park.png')
backgroundImage = pygame.transform.scale(backgroundImage, (WINDOWWIDTH, WINDOWHEIGHT))

#------------------------------ 起始畫面 ------------------------------
windowSurface.fill(BACKGROUNDCOLOR)
drawText('Catch the tennis balls!', font, windowSurface, WINDOWWIDTH//2, WINDOWHEIGHT//2 - 30)
drawText('Press SPACE to start', font, windowSurface, WINDOWWIDTH//2, WINDOWHEIGHT//2 + 20)
pygame.display.update()
waitForPlayerToPressKey()

#------------------------------ 主程式 ------------------------------
while True:
    GameTime = 2000
    score = 0
    level = 1
    tennis = []
    badBalls = []

    # 每一輪開始前重新定位角色
    playerRect.topleft = (WINDOWWIDTH // 2, WINDOWHEIGHT - 132)
    moveLeft = moveRight = False
    tennisAddCounter = 0
    badBallAddCounter = 0
    pygame.mixer.music.play(-1, 0.0)
    
    paused = False  # 暫停狀態

    while GameTime > 0:
        GameTime -= 1
        if score >= level * LEVEL_THRESHOLD:
            level += 1
            GameTime += 500  # 升一關，加 5 秒（500 / 100 = 5s）


        # 處理事件
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    moveRight = False
                    moveLeft = True
                elif event.key == K_RIGHT:
                    moveLeft = False
                    moveRight = True
                elif event.key == K_p:
                    paused = not paused  # 切換暫停狀態
                elif event.key == K_ESCAPE:
                    terminate()
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    moveLeft = False
                elif event.key == K_RIGHT:
                    moveRight = False
            if event.type == MOUSEMOTION:
                if 0 <= event.pos[0] <= WINDOWWIDTH:
                    playerRect.centerx = event.pos[0]

        # 檢查暫停
        if paused:
            drawText('PAUSED', font, windowSurface, WINDOWWIDTH//2, WINDOWHEIGHT//2)
            pygame.display.update()
            mainClock.tick(FPS)
            continue

        # 移動玩家
        if moveLeft and playerRect.left > 0:
            playerRect.move_ip(-PLAYERMOVERATE, 0)
        if moveRight and playerRect.right < WINDOWWIDTH:
            playerRect.move_ip(PLAYERMOVERATE, 0)

        # 根據目前關卡，調整新增頻率與物件速度
        currentAddRate = max(ADDNEWARTICLERATE - (level - 1) * LEVEL_RATE_DECREASE, 20)

        # 新增網球
        tennisAddCounter += 1
        if tennisAddCounter >= currentAddRate:
            tennisAddCounter = 0
            tennis_size = random.randint(30, 60)  # 隨機大小（建議30~60之間）
            newTennis = {
                'image': pygame.transform.scale(tennisImage, (tennis_size, tennis_size)),
                'rect': pygame.Rect(random.randint(0, WINDOWWIDTH - tennis_size), -tennis_size, tennis_size, tennis_size),
                'speed': random.randint(ARTICLEMINSPEED, ARTICLEMAXSPEED) * level
}

            tennis.append(newTennis)

        for t in tennis[:]:
            t['rect'].move_ip(0, t['speed'])
            if playerRect.colliderect(t['rect']):
                getBallSound.play()
                score += 1
                tennis.remove(t)
            elif t['rect'].top > WINDOWHEIGHT:
                tennis.remove(t)

        # 新增壞球
        badBallAddCounter += 1
        if badBallAddCounter >= currentAddRate:
            badBallAddCounter = 0
            bad_size = random.randint(30, 60)
            newBadBall = {
                'image': pygame.transform.scale(badBallImage, (bad_size, bad_size)),
                'rect': pygame.Rect(random.randint(0, WINDOWWIDTH - bad_size), -bad_size, bad_size, bad_size),
                'speed': random.randint(ARTICLEMINSPEED, ARTICLEMAXSPEED) * level
}

            badBalls.append(newBadBall)

        for b in badBalls[:]:
            b['rect'].move_ip(0, b['speed'])
            if playerRect.colliderect(b['rect']):
                getBadBallSound.play()
                if score > 0:
                    score -= 1
                badBalls.remove(b)
            elif b['rect'].top > WINDOWHEIGHT:
                badBalls.remove(b)

        # 判斷是否升級關卡，每達 LEVEL_THRESHOLD 分升一關
        if score >= level * LEVEL_THRESHOLD:
            level += 1

        # 畫面更新
        windowSurface.blit(backgroundImage, (0, 0))
        drawText(f'Time: {GameTime//100}', font, windowSurface, 10, 20, align='left')  # 左上
        drawText(f'Score: {score}', font, windowSurface, WINDOWWIDTH - 10, 20, align='right')  # 右上
        drawText(f'Level: {level}', font, windowSurface, WINDOWWIDTH // 2, 20)  # 中上

        for t in tennis:
            windowSurface.blit(t['image'], t['rect'])

        for b in badBalls:
            windowSurface.blit(b['image'], b['rect'])


        windowSurface.blit(playerImage, playerRect)
        pygame.display.update()
        mainClock.tick(FPS)

    # 結果畫面：停止背景音樂後顯示結果，並等待玩家按空白鍵重新開始
    pygame.mixer.music.stop()
    if score >= LEVEL_THRESHOLD:
        gameSuccessSound.play()
        drawText('Success!!', font, windowSurface, WINDOWWIDTH//2, WINDOWHEIGHT//2)
    else:
        gameOverSound.play()
        drawText('GAME OVER', font, windowSurface, WINDOWWIDTH//2, WINDOWHEIGHT//2)

    drawText('Press SPACE to play again', font, windowSurface, WINDOWWIDTH//2, WINDOWHEIGHT//2 + 40)
    pygame.display.update()
    waitForPlayerToPressKey()
    gameSuccessSound.stop()
    gameOverSound.stop()

