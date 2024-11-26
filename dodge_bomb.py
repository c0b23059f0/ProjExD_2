import os
import time
import random
import sys
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0,-5),
    pg.K_DOWN: (0,+5),
    pg.K_LEFT: (-5,0),
    pg.K_RIGHT: (+5,0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.rect) -> tuple[bool,bool]:
    """
    引数で与えたRectが画面の中か外かを判断する
    引数:こうかとんのRect or 爆弾Rect 
    戻り値：真理値タプル(横,縦)/画面内:True,画面外:False
    """
    yoko, tate = True,True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False

    return yoko,tate
    
def gameover(screen :pg.Surface) -> None:
    """
    ゲームオーバー時に画面に「Game Over」を表示し、泣いているこうかとんを描画する。
    引数：screen - 描画するスクリーンSurface
    """
    # ブラックアウト用の半透明Surface
    overlay = pg.Surface(screen.get_size())
    overlay.set_alpha(210)  # 半透明度設定
    overlay.fill((0, 0, 0))  # 黒色で塗りつぶす
    screen.blit(overlay, (0, 0))  # 画面に重ねる
    
    # "Game Over" テキストの描画
    font = pg.font.Font(None, 80)
    text = font.render("GAME OVER", True, (255, 255, 255))
    
    # 泣いているこうかとん画像（8.png）を読み込む
    crying_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    # 左右にこうかとんを表示する座標
    left_pos = (WIDTH // 4 - crying_kk_img.get_width() // 2, HEIGHT // 2 - crying_kk_img.get_height() // 2)
    right_pos = (3 * WIDTH // 4 - crying_kk_img.get_width() // 2, HEIGHT // 2 - crying_kk_img.get_height() // 2)
    # ブラックアウトのための半透明Surface
    blackout = pg.Surface((WIDTH, HEIGHT))
    blackout.fill((0, 0, 0))
    blackout.set_alpha(210)
    # 半透明の黒い四角を画面に描画（ブラックアウト）
    screen.blit(blackout, (0, 0))
    # ブラックアウト後にこうかとんとテキストを描画
    screen.blit(crying_kk_img, left_pos)
    screen.blit(crying_kk_img, right_pos)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 40))
    # 描画を更新して5秒間表示
    pg.display.update()
    time.sleep(5)  # 5秒間停止


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20,20))  # 爆弾surface
    pg.draw.circle(bb_img, (255,0,0),(10,10),10)  # 爆弾円を描く
    bb_rct = bb_img.get_rect()  # 爆弾rectの抽出
    bb_rct.centerx = random.randint(0,WIDTH)
    bb_rct.centery  = random.randint(0,HEIGHT)
    bb_img.set_colorkey((0,0,0))  # 四隅の黒を透過
    vx, vy = +5,-5  # 爆弾移動ベクトル
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key,tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True,True):
            kk_rct.move_ip(-sum_mv[0],-sum_mv[1])
        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(vx,vy)
        yoko,tate = check_bound(bb_rct)
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()