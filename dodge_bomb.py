import os
import time
import random
import sys
import pygame as pg
import math

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
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False

    return yoko, tate
    
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

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    時間経過によってサイズが異なる爆弾Surfaceのリストと加速度リストを返す。
    戻り値: (爆弾Surfaceリスト, 加速度リスト)
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    引数で与えられた移動量の合計値に対応するこうかとんの向きを表す画像Surfaceを返す。
    引数：sum_mv - 移動量タプル（例：(5, 0)など）
    戻り値：移動方向に対応するこうかとんの画像Surface
    """
    kk_images = {
    (0, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -90, 1),  # 上
    (0, 5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 1),  # 下
    (-5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1),  # 左
    (5, 0): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1), True, False),  # 右（反転）
    (5, -5): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 1), True, False),  # 右上（反転）
    (-5, 5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 1),  # 左下
    (-5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 1),  # 左上
    (5, 5): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 1), True, False),  # 右下（反転）
}
    # sum_mvが指定されていない場合のデフォルト（上向き）
    return kk_images.get(sum_mv, pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1))

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    orgから見て、dstがどこにあるかを計算し、方向ベクトルを返す
    引数：org - 始点Rect
          dst - 終点Rect
          current_xy - 現在の移動速度ベクトル
    戻り値：方向ベクトル (vx, vy)
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    norm = math.sqrt(dx**2 + dy**2)  # ノルム（距離）
    if norm != 0:  # 距離が0でないときにのみ正規化
        vx = dx / norm * 5  # 速度調整（5は速度の係数）
        vy = dy / norm * 5
    else:
        vx, vy = 0, 0
    return vx, vy

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_imgs, bb_accs = init_bb_imgs()

    # 爆弾初期設定
    bb_rct = bb_imgs[0].get_rect()  # 爆弾rectの初期設定
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, -5  # 爆弾移動ベクトル

    # ゲームループ
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return

        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]

        kk_img = get_kk_img(tuple(sum_mv))
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # 爆弾サイズの変化
        bb_img = bb_imgs[min(tmr // 500, 9)]
        bb_acc = bb_accs[min(tmr // 500, 9)]  # 時間経過で爆弾の速度を変化
        avx = vx * bb_acc
        avy = vy * bb_acc
        bb_rct.move_ip(avx, avy)

        yoko, tate = check_bound(bb_rct)
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
