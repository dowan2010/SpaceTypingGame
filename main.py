import tkinter as tk
import random as r
import time
from PIL import Image, ImageTk
start_time = None

# 게임에서 떨어질 단어 목록 (파이썬 / 자바스크립트 / 자바)
pure_keywords = [
    # 파이썬
    "print", "len", "input", "type", "int", "str", "append", "def", "return", "except",
    # 자바스크립트
    "console", "alert", "let", "const", "push", "length", "Math", "function", "catch",
    # 자바
    "System", "String", "boolean", "double", "import", "break", "public", "static",
    # 공통
    "class", "try",
]

# 창 만들고 화면 꽉 채우기
root = tk.Tk()
root.title("우타")
root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.geometry(f"{screen_w}x{screen_h}+0+0")

# 실제 창 크기를 정확히 읽어오기 위해 한 번 더 update..
root.update()
screen_w = root.winfo_width()
screen_h = root.winfo_height()

# 모든 그래픽 요소를 여기에 그림
canvas = tk.Canvas(root, width=screen_w, height=screen_h, bg="black")
canvas.pack(fill="both", expand=True)

# 게임 상태 변수들
words = []  # 현재 화면에 떨어지고 있는 단어 목록
life = 3  # 남은 생명
score = 0  # 현재 점수
target_score = 500  # 목표 점수
fall_speed = 5  # 낙하 속도
speed_increment = 0.3  # 5초마다 증가할 속도값
hud_id = None          # 점수/생명/속도 텍스트의 캔버스 ID
spawn_timer = None  # 단어 생성 타이머 ID
speed_timer = None  # 속도 증가 타이머 ID
game_loop_timer = None  # 게임 루프 타이머 ID

# 이미지는 미리 로드해둠.. 함수 안에서 매번 열면 느려짐 ㅎㅎ
exp_img = Image.open(
    "—Pngtree—red spark explosion effect wake_4671546.png").resize((100, 100))
explosion_photo = ImageTk.PhotoImage(exp_img)

meteor_img = Image.open(
    "cartoon-space-meteorite-with-craters-bumps-vector-isolated-stone_364586-2655-removebg-preview.png").resize((80, 80))
meteor_photo = ImageTk.PhotoImage(meteor_img)

# 입력창.. 엔터 누르면 check_input 실행
name_entry = tk.Entry(root, font=("맑은 고딕", 20), width=50)
name_entry.bind("<Return>", lambda e: check_input(e))

# 어디서든 엔터 누르면 입력창으로 포커스 이동
root.bind("<Return>", lambda e: name_entry.focus_set())


def load_bg():
    # 배경 이미지를 화면 크기에 맞게 늘려서 캔버스에 깔기
    bg_image = Image.open(
        "photo-1520034475321-cbe63696469a.png").resize((screen_w, screen_h))
    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0, 0, anchor="nw", image=bg_photo)
    canvas.bg_photo = bg_photo  # 참조 안 유지하면 이미지가 사라짐..


def show_start():
    # 시작 화면.. 타이틀이랑 목표 점수 안내, 시작 버튼
    canvas.delete("all")
    load_bg()
    canvas.create_text(screen_w//2, screen_h//2, text="우타",
                       fill="white", font=("맑은 고딕", 40, "bold"))
    canvas.create_text(screen_w//2, screen_h//2 + 60, text=f"목표 점수: {target_score}점",
                       fill="yellow", font=("맑은 고딕", 20))
    canvas.create_text(screen_w//2, screen_h//2 + 100, text="엔터키로 입력",
                       fill="white", font=("맑은 고딕", 15))
    btn = tk.Button(root, text="시작", command=show_difficulty_selection)
    canvas.create_window(screen_w//2, int(screen_h * 0.66), window=btn)


def show_difficulty_selection():
    # 난이도 선택 화면.. 쉬움 / 보통 / 어려움
    canvas.delete("all")
    load_bg()
    canvas.create_text(screen_w//2, screen_h//2 - 80, text="난이도 선택",
                       fill="white", font=("맑은 고딕", 30, "bold"))
    btn1 = tk.Button(root, text="쉬움", command=lambda: start_game("easy"))
    canvas.create_window(screen_w//2, screen_h//2, window=btn1)
    btn2 = tk.Button(root, text="보통", command=lambda: start_game("normal"))
    canvas.create_window(screen_w//2, screen_h//2 + 50, window=btn2)
    btn3 = tk.Button(root, text="어려움", command=lambda: start_game("hard"))
    canvas.create_window(screen_w//2, screen_h//2 + 100, window=btn3)


def start_game(difficulty):
    # 게임 시작 전 상태 초기화/난이도에 따라 속도 설정
    global fall_speed, speed_increment, score, life, words, hud_id, spawn_timer, speed_timer, game_loop_timer, start_time
    start_time = time.time()
    score = 0
    life = 3
    words = []

    if difficulty == "easy":
        fall_speed = 3
        speed_increment = 0.4
    elif difficulty == "normal":
        fall_speed = 4.5
        speed_increment = 0.7
    elif difficulty == "hard":
        fall_speed = 6
        speed_increment = 0.9

    # 재시작할 때 이전 타이머가 남아있으면 끊어줌.. 안 끊으면 단어가 두 배로 생김 ㅎㅎ
    if spawn_timer:
        root.after_cancel(spawn_timer)
        spawn_timer = None
    if speed_timer:
        root.after_cancel(speed_timer)
        speed_timer = None
    if game_loop_timer:
        root.after_cancel(game_loop_timer)
        game_loop_timer = None

    canvas.delete("all")
    load_bg()

    # 우주선 이미지 로드 후 화면 하단 중앙에 고정
    ship_img = Image.open(
        "_Pngtree_aerospace_rocket_illustration_4567316-removebg-preview.png").resize((100, 100))
    ship_photo = ImageTk.PhotoImage(ship_img)
    canvas.create_image(screen_w//2, screen_h - 100, image=ship_photo)
    canvas.ship_photo = ship_photo

    # HUD 텍스트 생성.. 좌상단에 점수/생명/속도 표시
    hud_id = canvas.create_text(10, 10, anchor="nw",
                                text=f"점수: {score} / {target_score}  생명: {life}  속도: {fall_speed:.1f}",
                                fill="white", font=("맑은 고딕", 25))

    # 입력창 화면 맨 아래에 배치
    canvas.create_window(screen_w//2, screen_h - 30, window=name_entry)
    name_entry.delete(0, tk.END)
    name_entry.focus_set()

    spawn_word()
    increase_speed()
    game_loop()


def spawn_word():
    # 랜덤 단어 하나를 골라 화면 위쪽 랜덤한 x 위치에 운석+텍스트로 생성
    global spawn_timer
    w = r.choice(pure_keywords)
    x = r.randint(50, screen_w - 50)
    meteor_id = canvas.create_image(
        x, 50, image=meteor_photo)  # 운석 먼저 그려야 텍스트가 위에 뜸
    item_id = canvas.create_text(
        x, 50, text=w, fill="white", font=("맑은 고딕", 30))
    words.append({"text": w, "id": item_id, "meteor_id": meteor_id})
    spawn_timer = root.after(2000, spawn_word)  # 2초 뒤에 또 하나 생성


def increase_speed():
    # 5초마다 낙하 속도를 speed_increment만큼 올림..
    global fall_speed, speed_timer
    fall_speed += speed_increment
    speed_timer = root.after(5000, increase_speed)


def game_loop():
    # 50ms마다 반복.. 단어 낙하 처리 + HUD 갱신 + 종료 조건 확인
    global life, game_loop_timer
    for data in words[:]:  # 복사본으로 순회해야 중간에 삭제해도 오류 안 남
        canvas.move(data["id"], 0, fall_speed)
        canvas.move(data["meteor_id"], 0, fall_speed)
        coords = canvas.coords(data["id"])
        if not coords:  # 이미 삭제된 객체면 건너뜀
            continue
        y = coords[1]
        if y > screen_h - 50:  # 바닥에 닿으면 삭제하고 생명 감소
            canvas.delete(data["id"])
            canvas.delete(data["meteor_id"])
            words.remove(data)
            life -= 1
    canvas.itemconfig(hud_id,
                      text=f"점수: {score}  생명: {life}  속도: {fall_speed:.1f}  시간: {round(time.time() - start_time, 1)}s",
                      fill="white", font=("맑은 고딕", 25))
    if check_clear():
        return
    game_loop_timer = root.after(50, game_loop)


def check_input(_event):
    # 엔터를 누르면 입력값이 떨어지는 단어 중 하나와 일치하는지 확인
    global score
    typed = name_entry.get()
    name_entry.delete(0, tk.END)
    for word_data in words:
        if typed == word_data["text"]:
            pos = canvas.coords(word_data["id"])
            canvas.delete(word_data["id"])
            canvas.delete(word_data["meteor_id"])
            words.remove(word_data)
            score += 25
            # 맞힌 위치에 폭발 이펙트 0.5초 표시
            exp_id = canvas.create_image(pos[0], pos[1], image=explosion_photo)
            root.after(500, lambda: canvas.delete(exp_id))
            break
    else:
        score -= 10


def stop_timers():
    # 게임 종료 또는 재시작할 때 남아있는 타이머 정리..
    global spawn_timer, speed_timer, game_loop_timer
    if spawn_timer:
        root.after_cancel(spawn_timer)
        spawn_timer = None
    if speed_timer:
        root.after_cancel(speed_timer)
        speed_timer = None
    if game_loop_timer:
        root.after_cancel(game_loop_timer)
        game_loop_timer = None


def show_result(text, color, elapsed=None):
    # 게임 결과 화면.. 클리어면 시간이랑 랭킹도 같이 표시
    canvas.delete("all")
    load_bg()
    canvas.create_text(screen_w//2, screen_h//2, text=text, fill=color,
                       font=("맑은 고딕", 80, "bold"))
    if elapsed is not None:
        canvas.create_text(screen_w//2, screen_h//2 + 100,
                           text=f"클리어 시간: {elapsed}초",
                           fill="yellow", font=("맑은 고딕", 30))
        score_list = save_score(elapsed)
        show_ranking(score_list)
    btn = tk.Button(root, text="다시하기", command=show_difficulty_selection,
                    bg="black", fg="#ff8000", bd=0, font=("맑은 고딕", 15))
    canvas.create_window(screen_w//2, screen_h//2 + 170, window=btn)


def save_score(elapsed):
    # 클리어 시간을 파일에 저장하고 빠른 순서대로 상위 5개만 유지
    try:
        with open("rank.txt", "r") as f:
            score_list = [float(line.strip()) for line in f.readlines()]
    except FileNotFoundError:
        score_list = []
    score_list.append(elapsed)
    score_list.sort()
    score_list = score_list[:5]
    with open("rank.txt", "w") as f:
        for t in score_list:
            f.write(f"{t}\n")
    return score_list


def show_ranking(score_list):
    # 클리어 시간 순위를 결과 화면에 표시
    rank = ["1위", "2위", "3위", "4위", "5위"]
    for i, t in enumerate(score_list):
        if t >= 60:  # 1분 이상은 초 대신 분으로 표시
            t = f"{t/60:.1f}분"
        else:
            t = f"{t}초"
        canvas.create_text(screen_w//2, screen_h//2 + 200 + i*40,
                           text=f"{rank[i]}  {t}",
                           fill="white", font=("맑은 고딕", 25))


def check_clear():
    # 생명 0이면 게임오버, 목표 점수 달성하면 클리어
    if life <= 0:
        stop_timers()
        show_result("게임오버", "red")
        return True
    if score >= target_score:
        stop_timers()
        elapsed = round(time.time() - start_time, 1)
        show_result("게임클리어", "green", elapsed)
        return True
    return False


# 시작 화면 띄우고 게임 루프 시작ㅎㅎ
root.after(100, show_start)
root.mainloop()