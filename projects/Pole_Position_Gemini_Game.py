"""
Pole Position Arcade Remake (High-Speed Difficulty Edition)
Includes: 2-Speed Gearbox, Boosted Speeds, Explosion Animations, Roadside Billboards,
Engine Audio, and Classic Arcade HUD/Scoring.
"""

import math
import random
import sys
import pygame

# Initialize Pygame and Mixer for Audio
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# --- CONFIGURATION & CONSTANTS ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 640
HORIZON_Y = 210
ROAD_BOTTOM = SCREEN_HEIGHT - 20
MAX_VIEW_DISTANCE = 2200

# Highly boosted speeds for an extreme arcade challenge
MAX_SPEED_LOW = 280
MAX_SPEED_HIGH = 520
ACCEL_LOW = 210
ACCEL_HIGH = 150
BRAKING = 340
DECEL_COAST = 45

FINISH_DISTANCE = 25000
RACE_TIME = 50.0  # Tighter time limit to match higher speeds

# Colors matching arcade palette
SKY_TOP = (0, 112, 236)
SKY_BOTTOM = (140, 204, 255)
GRASS_DARK = (0, 144, 0)
GRASS_LIGHT = (16, 176, 16)
ROAD_COLOR = (104, 104, 104)
ROAD_EDGE_COLOR = (240, 240, 240)
CURB_RED = (216, 0, 0)
PLAYER_COLOR = (236, 28, 36)
RIVAL_COLORS = [(0, 120, 240), (248, 184, 0), (224, 224, 224), (200, 76, 12)]
BILLBOARD_COLORS = [(240, 24, 24), (240, 216, 0), (0, 80, 200), (240, 240, 240)]


def generate_engine_sound():
    """Generate a procedural low-frequency engine buzz sound."""
    sample_rate = 22050
    duration = 0.1
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n_samples):
        t = float(i) / sample_rate
        val = 127 if math.sin(2 * math.pi * 75 * t) > 0 else -128
        buf.append(val & 0xFF)
    return pygame.mixer.Sound(buffer=bytes(buf))


try:
    ENGINE_SOUND = generate_engine_sound()
    ENGINE_SOUND.set_volume(0.15)
except Exception:
    ENGINE_SOUND = None


def create_game():
    scenery = []
    for distance in range(250, FINISH_DISTANCE + MAX_VIEW_DISTANCE, 300):
        side = random.choice([-1, 1])
        scenery.append({
            "distance": distance,
            "side": side,
            "kind": random.choice(["billboard", "billboard", "sign"]),
            "color": random.choice(BILLBOARD_COLORS),
            "text": random.choice(["NAMCO", "POLE POS", "ATARI", "GP 1982"])
        })

    return {
        "mode": "title",
        "distance": 0.0,
        "speed": 0.0,
        "lane": 0.0,
        "gear": "LOW",
        "score": 0,
        "time_left": RACE_TIME,
        "traffic": [],
        "explosions": [],
        "spawn_timer": 0.4,
        "scenery": scenery,
        "crash_timer": 0.0,
    }


def road_curve(world_distance):
    bend1 = math.sin(world_distance * 0.0006) * 180
    bend2 = math.cos(world_distance * 0.0013) * 85
    return bend1 + bend2


def perspective_at_y(screen_y):
    if screen_y <= HORIZON_Y:
        return 0.0
    return min(1.0, (screen_y - HORIZON_Y) / (ROAD_BOTTOM - HORIZON_Y))


def road_values_at_y(screen_y, game):
    perspective = perspective_at_y(screen_y)
    look_ahead = (1.0 - perspective) * 900
    center = SCREEN_WIDTH / 2 + road_curve(game["distance"] + look_ahead) * (0.2 + perspective * 0.8)
    half_width = 38 + (perspective ** 1.5) * 320
    return center, half_width


def project_distance(world_distance, game):
    depth = world_distance - game["distance"]
    if depth < 0 or depth > MAX_VIEW_DISTANCE:
        return None
    perspective = 1.0 - (depth / MAX_VIEW_DISTANCE)
    screen_y = HORIZON_Y + (perspective ** 2.1) * (ROAD_BOTTOM - HORIZON_Y)
    return screen_y, perspective


def draw_sky_and_mountains(screen, game):
    for row in range(HORIZON_Y):
        blend = row / HORIZON_Y
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * blend)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * blend)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * blend)
        pygame.draw.line(screen, (r, g, b), (0, row), (SCREEN_WIDTH, row))

    fuji_center = SCREEN_WIDTH // 2 - int(road_curve(game["distance"] * 0.2) * 0.5)
    mountain_pts = [
        (fuji_center - 260, HORIZON_Y),
        (fuji_center - 80, HORIZON_Y - 75),
        (fuji_center + 80, HORIZON_Y - 75),
        (fuji_center + 260, HORIZON_Y)
    ]
    pygame.draw.polygon(screen, (70, 90, 130), mountain_pts)
    snow_pts = [
        (fuji_center - 80, HORIZON_Y - 75),
        (fuji_center - 40, HORIZON_Y - 50),
        (fuji_center + 40, HORIZON_Y - 50),
        (fuji_center + 80, HORIZON_Y - 75)
    ]
    pygame.draw.polygon(screen, (240, 240, 255), snow_pts)

    stripe = int(game["distance"] // 40) % 2
    for row in range(HORIZON_Y, SCREEN_HEIGHT, 16):
        color = GRASS_DARK if (row // 16 + stripe) % 2 == 0 else GRASS_LIGHT
        pygame.draw.rect(screen, color, (0, row, SCREEN_WIDTH, 16))


def draw_road(screen, game):
    road_pts = []
    rows = list(range(HORIZON_Y, SCREEN_HEIGHT + 8, 6))
    for row in rows:
        center, half_w = road_values_at_y(row, game)
        road_pts.append((center - half_w, row))
    for row in reversed(rows):
        center, half_w = road_values_at_y(row, game)
        road_pts.append((center + half_w, row))

    pygame.draw.polygon(screen, ROAD_COLOR, road_pts)

    for row in range(HORIZON_Y + 1, SCREEN_HEIGHT, 6):
        center, half_w = road_values_at_y(row, game)
        p = perspective_at_y(row)
        curb_w = max(2, int(10 * p))
        stripe_idx = int((game["distance"] + (1 - p) * 900) // 30)
        c_color = CURB_RED if stripe_idx % 2 == 0 else ROAD_EDGE_COLOR

        pygame.draw.rect(screen, c_color, (int(center - half_w), row, curb_w, 6))
        pygame.draw.rect(screen, c_color, (int(center + half_w - curb_w), row, curb_w, 6))

    for dash_d in range(70, MAX_VIEW_DISTANCE, 160):
        proj = project_distance(game["distance"] + dash_d, game)
        if proj:
            sy, p = proj
            center, _ = road_values_at_y(sy, game)
            dh = max(2, int(24 * p))
            dw = max(2, int(6 * p))
            pygame.draw.rect(screen, (240, 240, 240), (int(center - dw / 2), int(sy), dw, dh))


def draw_billboard(screen, x, y, scale, item):
    w = max(16, int(70 * scale))
    h = max(10, int(35 * scale))
    post_h = max(8, int(30 * scale))

    pygame.draw.rect(screen, (160, 160, 160), (int(x - w / 4), int(y - post_h), max(2, int(4 * scale)), post_h))
    pygame.draw.rect(screen, (160, 160, 160), (int(x + w / 4), int(y - post_h), max(2, int(4 * scale)), post_h))

    board_rect = pygame.Rect(int(x - w / 2), int(y - post_h - h), w, h)
    pygame.draw.rect(screen, item["color"], board_rect)
    pygame.draw.rect(screen, (255, 255, 255), board_rect, max(1, int(2 * scale)))


def draw_scenery(screen, game):
    objs = []
    for s in game["scenery"]:
        proj = project_distance(s["distance"], game)
        if proj:
            objs.append((proj[1], s, proj[0]))
    objs.sort(key=lambda o: o[0])

    for scale, item, sy in objs:
        center, half_w = road_values_at_y(sy, game)
        x = center + item["side"] * (half_w + 35 * scale + 25)
        draw_billboard(screen, x, sy, scale, item)


def get_car_rect(x, y, scale):
    w = max(14, int(44 * scale))
    h = max(16, int(54 * scale))
    return pygame.Rect(int(x - w / 2), int(y - h), w, h)


def draw_car(screen, x, y, scale, color, player=False):
    rect = get_car_rect(x, y, scale)
    w, h = rect.width, rect.height

    tw = max(3, int(8 * scale))
    th = max(5, int(14 * scale))
    pygame.draw.rect(screen, (10, 10, 10), (rect.left - tw // 2, rect.top + int(h * 0.2), tw, th))
    pygame.draw.rect(screen, (10, 10, 10), (rect.right - tw // 2, rect.top + int(h * 0.2), tw, th))
    pygame.draw.rect(screen, (10, 10, 10), (rect.left - tw // 2, rect.bottom - th, tw, th))
    pygame.draw.rect(screen, (10, 10, 10), (rect.right - tw // 2, rect.bottom - th, tw, th))

    pygame.draw.rect(screen, color, rect, border_radius=max(2, int(4 * scale)))
    cp_w = max(4, int(w * 0.5))
    cp_h = max(4, int(h * 0.3))
    pygame.draw.rect(screen, (30, 40, 50), (rect.centerx - cp_w // 2, rect.top + int(h * 0.25), cp_w, cp_h))

    if player:
        pygame.draw.rect(screen, (240, 240, 240), (rect.left, rect.bottom - max(4, int(6 * scale)), w, max(3, int(5 * scale))))
    return rect


def trigger_explosion(game, x, y):
    game["explosions"].append({"x": x, "y": y, "radius": 10, "max_radius": 45, "life": 0.4})


def update_explosions(game, dt):
    survivors = []
    for exp in game["explosions"]:
        exp["life"] -= dt
        exp["radius"] += dt * 90
        if exp["life"] > 0:
            survivors.append(exp)
    game["explosions"] = survivors


def draw_explosions(screen, game):
    for exp in game["explosions"]:
        r = int(exp["radius"])
        pygame.draw.circle(screen, (255, 200, 0), (int(exp["x"]), int(exp["y"])), r)
        pygame.draw.circle(screen, (230, 40, 0), (int(exp["x"]), int(exp["y"])), max(2, int(r * 0.6)))
        pygame.draw.circle(screen, (255, 255, 200), (int(exp["x"]), int(exp["y"])), max(1, int(r * 0.3)))


def spawn_traffic(game):
    game["spawn_timer"] -= 1 / 60.0
    if game["spawn_timer"] <= 0:
        lane = random.choice([-0.65, -0.25, 0.25, 0.65])
        game["traffic"].append({
            "distance": game["distance"] + random.randint(1100, 1600),
            "lane": lane,
            "speed": random.randint(140, 260),  # Rival cars are also faster!
            "color": random.choice(RIVAL_COLORS)
        })
        game["spawn_timer"] = random.uniform(0.6, 1.2)


def update_traffic(game, dt):
    player_sy = ROAD_BOTTOM - 10
    pc, pw = road_values_at_y(player_sy, game)
    px = pc + game["lane"] * pw * 0.78
    p_body = get_car_rect(px, SCREEN_HEIGHT - 20, 1.0)

    survivors = []
    for rival in game["traffic"]:
        rival["distance"] += rival["speed"] * dt * 1.3
        rel_d = rival["distance"] - game["distance"]
        if rel_d <= 0:
            game["score"] += 250
            continue

        proj = project_distance(rival["distance"], game)
        if proj is None:
            survivors.append(rival)
            continue

        sy, scale = proj
        rc, rw = road_values_at_y(sy, game)
        rx = rc + rival["lane"] * rw * 0.78
        r_body = get_car_rect(rx, sy, scale)

        if game["mode"] == "racing" and r_body.colliderect(p_body):
            trigger_explosion(game, px, SCREEN_HEIGHT - 40)
            game["speed"] = 0
            game["mode"] = "crashed"
            game["crash_timer"] = 1.0
            game["time_left"] = max(0, game["time_left"] - 3.5)
            continue
        survivors.append(rival)
    game["traffic"] = survivors


def update_race(game, dt):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT]:
        game["gear"] = "HIGH"
    else:
        game["gear"] = "LOW"

    max_spd = MAX_SPEED_LOW if game["gear"] == "LOW" else MAX_SPEED_HIGH
    accel = ACCEL_LOW if game["gear"] == "LOW" else ACCEL_HIGH

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        game["speed"] = min(max_spd, game["speed"] + accel * dt)
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        game["speed"] = max(0, game["speed"] - BRAKING * dt)
    else:
        game["speed"] = max(0, game["speed"] - DECEL_COAST * dt)

    steering = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
    game["lane"] += steering * (0.85 + game["speed"] / MAX_SPEED_HIGH) * dt

    if abs(game["lane"]) > 0.85:
        game["speed"] = max(0, game["speed"] - 180 * dt)

    game["lane"] = max(-1.1, min(1.1, game["lane"]))
    # Significantly faster world movement multiplier
    game["distance"] += game["speed"] * dt * 2.8
    game["score"] += int(game["speed"] * dt * 0.7)
    game["time_left"] -= dt

    spawn_traffic(game)
    update_traffic(game, dt)

    if game["distance"] >= FINISH_DISTANCE:
        game["mode"] = "won"
        game["score"] += int(max(0, game["time_left"]) * 300)
    elif game["time_left"] <= 0:
        game["mode"] = "lost"


def draw_hud(screen, font, title_font, game):
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, 42))

    score_txt = font.render(f"SCORE  {game['score']:06d}", True, (255, 255, 255))
    speed_txt = font.render(f"SPEED  {int(game['speed']):03d} km/h", True, (255, 220, 0))
    time_txt = font.render(f"TIME  {max(0, game['time_left']):04.1f}", True, (255, 60, 60))
    gear_color = (80, 220, 255) if game["gear"] == "HIGH" else (255, 180, 50)
    gear_txt = font.render(f"GEAR  {game['gear']}", True, gear_color)

    screen.blit(score_txt, (20, 10))
    screen.blit(speed_txt, (250, 10))
    screen.blit(gear_txt, (480, 10))
    screen.blit(time_txt, (SCREEN_WIDTH - 180, 10))


def draw_game(screen, font, title_font, game):
    draw_sky_and_mountains(screen, game)
    draw_road(screen, game)
    draw_scenery(screen, game)

    for rival in sorted(game["traffic"], key=lambda c: c["distance"], reverse=True):
        proj = project_distance(rival["distance"], game)
        if proj:
            sy, scale = proj
            rc, rw = road_values_at_y(sy, game)
            rx = rc + rival["lane"] * rw * 0.78
            draw_car(screen, rx, sy, scale, rival["color"])

    if game["mode"] != "crashed":
        pc, pw = road_values_at_y(ROAD_BOTTOM - 10, game)
        px = pc + game["lane"] * pw * 0.78
        draw_car(screen, px, SCREEN_HEIGHT - 20, 1.0, PLAYER_COLOR, player=True)

    draw_explosions(screen, game)
    draw_hud(screen, font, title_font, game)

    if game["mode"] == "title":
        t_surf = title_font.render("POLE POSITION (EXtreme)", True, (255, 215, 0))
        sub_surf = font.render("PRESS ENTER TO RACE - HOLD SPACE FOR HIGH GEAR (520 KM/H)", True, (255, 255, 255))
        screen.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 280)))
        screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 350)))

    elif game["mode"] in ("won", "lost"):
        txt = "FINISH!" if game["mode"] == "won" else "TIME'S UP"
        col = (255, 215, 0) if game["mode"] == "won" else (255, 60, 60)
        res_surf = title_font.render(txt, True, col)
        sc_surf = font.render(f"FINAL SCORE: {game['score']}", True, (255, 255, 255))
        rst_surf = font.render("PRESS ENTER TO RESTART", True, (200, 200, 200))
        screen.blit(res_surf, res_surf.get_rect(center=(SCREEN_WIDTH // 2, 270)))
        screen.blit(sc_surf, sc_surf.get_rect(center=(SCREEN_WIDTH // 2, 330)))
        screen.blit(rst_surf, rst_surf.get_rect(center=(SCREEN_WIDTH // 2, 380)))

    pygame.display.flip()


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pole Position - Extreme High Speed Edition")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    title_font = pygame.font.Font(None, 64)

    game = create_game()
    running = True

    while running:
        dt = min(clock.tick(60) / 1000.0, 0.04)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if game["mode"] in ("title", "won", "lost"):
                    game = create_game()
                    game["mode"] = "racing"

        if game["mode"] == "racing":
            update_race(game, dt)
        elif game["mode"] == "crashed":
            game["crash_timer"] -= dt
            if game["crash_timer"] <= 0:
                game["mode"] = "racing"

        update_explosions(game, dt)
        draw_game(screen, font, title_font, game)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()