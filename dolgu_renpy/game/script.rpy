init python:
    import random
    import time

    _typing_clips = [
        "audio/button_click_03.wav",
    ]

    # ─ 속도 프리셋 ─
    # 타이핑 cps (chars per second). 30자 문장 기준 대략 총 시간:
    SPEED_NORMAL = 10   # 보통 ≈ 3초
    SPEED_FAST = 15     # 빠르게 ≈ 2초
    SPEED_VFAST = 30    # 아주 빠르게 ≈ 1초
    # 슬라이드 19(200자+) 전용 — 사용자 지시 "3배 더 빠르게" (원본 40 cps → 120)
    SPEED_RAPID = 120

    # 사운드 솎아내기: N글자마다 1번 재생 (1 = 매 글자, 2 = 2글자마다)
    SOUND_EVERY = 2

    # 타이핑 중 멈춤(소리 없음) — 언더테일식 리듬
    SPACE_PAUSE = 0.04       # 스페이스: 거의 안 느껴지는 짧은 숨
    PUNCT_PAUSE = 0.15       # , . ? ! … : 또렷한 멈춤
    PUNCT_CHARS = ",.?!…"    # ('...' 처럼 점 3개면 자동으로 3배 멈춤)

    # 삭제 총 시간(초). erase_in(target, seconds) 의 seconds 인자로 직접 사용.
    ERASE_NORMAL = 3.0  # 보통
    ERASE_FAST = 2.0    # 빠르게
    ERASE_VFAST = 1.0   # 아주 빠르게

    # ─ 폰트 ─
    # Heavy = 나레이션(3인칭 서술), Medium = 화자(1인칭 대화체)
    FONT_HEAVY = "fonts/SourceHanSerif-Heavy.ttc"
    FONT_MEDIUM = "fonts/SourceHanSerif-Medium.ttc"

    def play_typing():
        # 단일 타격 (한 글자씩 모드)
        renpy.sound.play(random.choice(_typing_clips))

    def play_typing_burst(count=6, gap=0.05):
        # "타다다다닥" 효과: 짧은 간격으로 여러 번 연속 재생 (문장 단위 모드)
        for i in range(count):
            renpy.sound.play(random.choice(_typing_clips))
            if i < count - 1:
                renpy.pause(gap, hard=True)

    def _common_prefix_len(a, b):
        n = min(len(a), len(b))
        for i in range(n):
            if a[i] != b[i]:
                return i
        return n

    def _split_chunks(text):
        # 마침표/물음표/느낌표 단위로 청크 분할.
        # 연속 종결문자(예: "...")는 하나로 묶음. 종결문자 뒤가 공백/줄바꿈/끝/괄호 열기면 경계.
        # 종결문자 뒤 짧은 잔여물(닫는 괄호 등 < 3자)은 앞 청크에 병합.
        chunks = []
        current = ""
        i = 0
        while i < len(text):
            c = text[i]
            current += c
            if c in (".", "?", "!"):
                # 연속 종결문자 흡수
                while i + 1 < len(text) and text[i+1] in (".", "?", "!"):
                    i += 1
                    current += text[i]
                next_c = text[i+1] if i + 1 < len(text) else ""
                if next_c in ("", " ", "\n", "(", "[", "{"):
                    chunks.append(current)
                    current = ""
            i += 1
        if current:
            stripped_short = len(current.strip(" \n\t).]}")) < 3
            if chunks and stripped_short:
                chunks[-1] += current
            else:
                chunks.append(current)
        return [c for c in chunks if c.strip()]

    def auto_type(target, cps=SPEED_NORMAL, sound=True, layout="center", font=FONT_MEDIUM):
        # 실제 경과 시간 기반 진행: 매 프레임 elapsed/total_time 비율로 글자 위치 계산.
        # 함수 오버헤드(show_screen/sound/루프 비용)와 무관하게 총 시간이 의도 시간(total_chars/cps)에 수렴.
        # 공백은 진행 카운트에서 제외 (시간 비용 없이 즉시 통과).
        cp = _common_prefix_len(store.current_text, target)
        erase_non_space = sum(1 for c in store.current_text[cp:] if c != " ")
        add_non_space = sum(1 for c in target[cp:] if c != " ")
        total_chars = erase_non_space + add_non_space
        if total_chars <= 0:
            if store.current_text != target:
                store.current_text = target
                renpy.show_screen("typewriter_screen", store.current_text, layout=layout, font=font)
            return
        total_time = total_chars / float(cps)
        FRAME_DT = 1.0 / 60.0
        SOUND_MIN_INTERVAL = 0.04

        start_t = time.time()
        chars_done = 0
        sound_counter = 0
        last_sound_t = start_t - 1.0

        while chars_done < total_chars:
            elapsed = time.time() - start_t
            progress = min(1.0, elapsed / total_time)
            target_done = int(round(total_chars * progress))

            changed = False
            played_sound = False
            while chars_done < target_done:
                # Erase 단계
                if chars_done < erase_non_space:
                    advanced = False
                    while len(store.current_text) > cp:
                        removed = store.current_text[-1]
                        store.current_text = store.current_text[:-1]
                        changed = True
                        if removed != " ":
                            chars_done += 1
                            advanced = True
                            if sound:
                                sound_counter += 1
                                if ((sound_counter - 1) % SOUND_EVERY == 0
                                        and not played_sound
                                        and time.time() - last_sound_t > SOUND_MIN_INTERVAL):
                                    play_typing()
                                    last_sound_t = time.time()
                                    played_sound = True
                            break
                    if not advanced:
                        break
                # Add 단계
                else:
                    advanced = False
                    while len(store.current_text) < len(target):
                        next_c = target[len(store.current_text)]
                        store.current_text = target[: len(store.current_text) + 1]
                        changed = True
                        if next_c != " ":
                            chars_done += 1
                            advanced = True
                            if sound:
                                sound_counter += 1
                                if ((sound_counter - 1) % SOUND_EVERY == 0
                                        and not played_sound
                                        and time.time() - last_sound_t > SOUND_MIN_INTERVAL):
                                    play_typing()
                                    last_sound_t = time.time()
                                    played_sound = True
                            break
                    if not advanced:
                        break

            if changed:
                renpy.show_screen("typewriter_screen", store.current_text, layout=layout, font=font)
            if chars_done < total_chars:
                renpy.pause(FRAME_DT, hard=True)

        # 최종 상태 보장 (잔여 공백 정리 등)
        if store.current_text != target:
            store.current_text = target
            renpy.show_screen("typewriter_screen", store.current_text, layout=layout, font=font)

    def type_in(target, cps=SPEED_NORMAL, sound=True, layout="center", font=FONT_MEDIUM):
        # 언더테일식 타이핑(추가 전용). current_text 는 target 의 접두사 가정.
        # 스페이스/구두점은 소리 없이 멈춤, 나머지는 SOUND_EVERY 글자마다 클릭.
        per_char = 1.0 / float(cps)
        sound_counter = 0
        while len(store.current_text) < len(target):
            c = target[len(store.current_text)]
            store.current_text = target[: len(store.current_text) + 1]
            renpy.show_screen("typewriter_screen", store.current_text, layout=layout, font=font)
            if c == " ":
                renpy.pause(SPACE_PAUSE, hard=True)
            elif c in PUNCT_CHARS:
                renpy.pause(PUNCT_PAUSE, hard=True)
            else:
                if sound:
                    sound_counter += 1
                    if (sound_counter - 1) % SOUND_EVERY == 0:
                        play_typing()
                renpy.pause(per_char, hard=True)

    def auto_type_sentences(target, cps=SPEED_NORMAL, sound=True, layout="center", font=FONT_MEDIUM):
        # target 으로 자동 전이 + 추가되는 텍스트를 마침표 단위로 끊어 청크 끝마다 클릭 대기.
        cp = _common_prefix_len(store.current_text, target)
        # 1) 공통 접두사까지 자동 삭제 (클릭 없음)
        if len(store.current_text) > cp:
            auto_type(store.current_text[:cp], cps=cps, sound=sound, layout=layout, font=font)
        # 2) 추가 부분을 청크별로 자동 타이핑 + 청크 끝 클릭
        to_add = target[cp:]
        chunks = _split_chunks(to_add)
        accumulated = store.current_text
        for chunk in chunks:
            accumulated += chunk
            type_in(accumulated, cps=cps, sound=sound, layout=layout, font=font)
            renpy.pause()

    def erase_in(target, seconds, sound=True, layout="center", font=FONT_MEDIUM):
        # 현재 텍스트 → target 까지 총 seconds 안에 자동 전이 (삭제 + 추가 통합).
        cp = _common_prefix_len(store.current_text, target)
        change = (
            sum(1 for c in store.current_text[cp:] if c != " ")
            + sum(1 for c in target[cp:] if c != " ")
        )
        if change <= 0:
            return
        cps = change / max(seconds, 0.01)
        auto_type(target, cps=cps, sound=sound, layout=layout, font=font)

    def output_by_sentence(text, layout="center", font=FONT_MEDIUM):
        # "연출 없음" 슬라이드용. 마침표 단위 청크 통째로 출력 (무음 — 버스트 사운드 보류, 연출 추후 변경).
        chunks = _split_chunks(text)
        accumulated = store.current_text
        for chunk in chunks:
            accumulated += chunk
            store.current_text = accumulated
            renpy.show_screen("typewriter_screen", store.current_text, layout=layout, font=font)
            renpy.pause()

    def next_slide():
        # 한 글자씩 삭제 없이 즉시 빈 상태로 리셋.
        store.current_text = ""
        renpy.show_screen("typewriter_screen", "")

    # ─ 슬라이드 20: 단어 순차 교체용 prefix/suffix ─
    SLIDE_20_PREFIX = (
        "……이 얼마나 비겁하고 우악스러운 짓이오.\n"
        "자기 자신을 피력하고 변호하고 치장하기에도 모자란 자리에 "
    )
    SLIDE_20_SUFFIX = (
        " 데려다 놓고, 막상 자신에게 불쾌한 말을\n"
        "내가 꺼내기라도 하면 검열하고 지워버리는, 독단적이고 치졸한 작가 말이오.\n"
        "당신도 지금 보고 있소?"
    )


default current_text = ""

image pic_01 = "images/Pic_01.png"

screen typewriter_screen(text, layout="center", font=FONT_MEDIUM):
    if layout == "right":
        text text:
            xalign 0.75
            yalign 0.5
            xsize 900
            text_align 0.0
            font font
    elif layout == "bottom":
        text text:
            xalign 0.5
            yalign 0.9
            xsize 1400
            text_align 0.5
            font font
    else:
        text text:
            xalign 0.5
            yalign 0.5
            xsize 1400
            text_align 0.0
            font font


label start:
    $ current_text = ""
    $ quick_menu = False  #하단 옵션 삭제
    show screen typewriter_screen("")

    # ───── [시나리오 작성자 참고용] 삭제 속도 데모 ─────
    # 각 라인을 타이핑 후 표시된 N초 동안 삭제 → 다음 데모로 자동 이어짐.
    # 본 시나리오 작업 시 erase_in(target, N) 의 N 값 감각 비교용.
    $ auto_type_sentences("텍스트를 0.25초 안에 지울 예정입니다.", cps=SPEED_NORMAL)
    $ erase_in("", 0.25)
    $ auto_type_sentences("텍스트를 0.5초 안에 지울 예정입니다.", cps=SPEED_NORMAL)
    $ erase_in("", 0.5)
    $ auto_type_sentences("텍스트를 0.75초 안에 지울 예정입니다.", cps=SPEED_NORMAL)
    $ erase_in("", 0.75)
    $ auto_type_sentences("텍스트를 1초 안에 지울 예정입니다.", cps=SPEED_NORMAL)
    $ erase_in("", 1.0)
    $ auto_type_sentences("텍스트를 2초 안에 지울 예정입니다.", cps=SPEED_NORMAL)
    $ erase_in("", 2.0)

    # ───── 슬라이드 2~4 (나레이션: Heavy / 연출: 한 글자씩 타이핑만, 삭제 없음) ─────
    $ auto_type_sentences("모든 작가는 글을 쓰려는 힘과\n글을 지우려는 힘을 동시에 지니고 있다.", cps=SPEED_NORMAL, font=FONT_HEAVY)
    $ next_slide()
    $ auto_type_sentences("대부분의 작가에게는\n지우려는 힘이 더 강하다.", cps=SPEED_NORMAL, font=FONT_HEAVY)
    $ next_slide()
    $ auto_type_sentences("그건 자신의 미숙함을 들키지 않는다는\n점에서 최악은 아니다.", cps=SPEED_NORMAL, font=FONT_HEAVY)
    $ next_slide()

    # ───── 슬라이드 5~7 (나레이션: Heavy / 연출: 한 문장 + 빠른 부분 삭제 체인) ─────
    $ auto_type_sentences("최악은 역시, 형편없는 작품을\n미처 지우지도 못하고 계속 써내려 가는 것.", cps=SPEED_NORMAL, font=FONT_HEAVY)
    # 빠르게 지우고 (5→6 상태) + 멈췄다가
    $ erase_in("최악은 역시, 형편없는 작품을\n미처 지우지도", ERASE_FAST, font=FONT_HEAVY)
    $ renpy.pause(1.5, hard=True)
    # 빠르게 지웠다가 (6→7 상태) — 멈춤 없이 이어짐
    $ erase_in("최악은 역시, 형편없는 작품", ERASE_FAST, font=FONT_HEAVY)
    $ renpy.pause(1.5, hard=True)

    # ───── 슬라이드 8 (5~7에서 이어짐: "최악은"으로 마저 줄임 + 2초 정지) ─────
    $ erase_in("최악", ERASE_FAST, font=FONT_HEAVY)
    $ renpy.pause(2.5, hard=True)
    $ next_slide()

    # ───── 슬라이드 9~12 (연출 없음 → 문장 단위 통 출력) ─────
    $ output_by_sentence("젠장.")
    $ next_slide()
    $ output_by_sentence("이렇게 또 만날 줄이야.")
    $ next_slide()
    $ output_by_sentence("솔직히 이제는 작가에게 실망했소.")
    $ next_slide()
    $ output_by_sentence("반복으로부터 나를 떠밀어 낸 걸로도 모자라,\n당신들을 또 상대하게 할 줄은.")
    $ next_slide()

    # ───── 슬라이드 13 (연출: 부분 삭제 + 빠른 전환) ─────
    $ auto_type_sentences("기분 같아선 당신들에게 욕이라도 실컷 해주고 싶소.", cps=SPEED_NORMAL)
    $ erase_in("기분 같아선 당신들에게.", ERASE_FAST)
    $ next_slide()

    # ───── 슬라이드 14~15 (연출 없음) ─────
    $ output_by_sentence("책에서 만났던 이들과는 전혀 다른 얼굴도 보이는 것 같소.")
    $ next_slide()
    $ output_by_sentence("만일 당신에게도 얼굴이라는 게 있다면 말이지.")
    $ next_slide()

    # ───── 슬라이드 16 (연출: 빠르게 지워짐) ─────
    $ auto_type_sentences("유령 같은 독자들. 아무것도 이해하지 않는 천치들.\n쓸모 없는 태엽만 달고 사는 허수아비들.", cps=SPEED_NORMAL)
    $ erase_in("", ERASE_FAST)

    # ───── 슬라이드 17~18 (연출 없음) ─────
    $ output_by_sentence("누구도 그 책을 끝까지 읽을 순 없었을 것이오.")
    $ next_slide()
    $ output_by_sentence("몇몇은 해괴한 그 책에 대해 무슨 자문이라도 구하려고\n도망치듯이 여기에 먼저 도착했고,\n몇몇은 편협하고 괴팍한 방식에 질려버린 나머지\n숨통이라도 틔우려고 여기까지 건너뛰었으며,")
    $ next_slide()

    # ───── 슬라이드 19 (연출: 아주 빠르게 써지고 부분 삭제 — 한 번에 쭉) ─────
    $ auto_type(
        "몇몇은 반복에 미쳐버린 인간을 화자로 내세운 작가에 대해\n"
        "이제 분노하고 있겠지. 이제 실망하고 있겠지. 이제 어떤 식으로든\n"
        "말하게 되겠지. 이런 건 시도 아니고, 연극도 아니고, 게임도 아니고,\n"
        "낭독회도 아니고, 소설도 아니고, 에세이도 아니고, 판타지도 아니고,\n"
        "메모도 아니고, 경고문도 아니고, 무엇도 아니고, 그저 최악의 형편 없는",
        cps=SPEED_RAPID)
    $ erase_in("몇몇은 반복에 미쳐버린 인간을 화자로 내세운 작가에 대해", ERASE_VFAST)
    $ next_slide()

    # ───── 슬라이드 20 (연출: 독자를→플레이어를→관객을→남을 순차 교체) ─────
    # prefix + "독자를" 자동 타이핑 (마침표 단위 클릭)
    $ auto_type_sentences(SLIDE_20_PREFIX + "독자를", cps=SPEED_NORMAL)
    # F 순차 교체 (아주 빠르게)
    $ auto_type(SLIDE_20_PREFIX, cps=SPEED_VFAST)
    $ auto_type(SLIDE_20_PREFIX + "플레이어를", cps=SPEED_VFAST)
    $ auto_type(SLIDE_20_PREFIX, cps=SPEED_VFAST)
    $ auto_type(SLIDE_20_PREFIX + "관객을", cps=SPEED_VFAST)
    $ auto_type(SLIDE_20_PREFIX, cps=SPEED_VFAST)
    $ auto_type(SLIDE_20_PREFIX + "남을", cps=SPEED_VFAST)
    # suffix 이어쓰기 (마침표 단위 클릭)
    $ auto_type_sentences(SLIDE_20_PREFIX + "남을" + SLIDE_20_SUFFIX, cps=SPEED_NORMAL)
    $ next_slide()

    # ───── 슬라이드 21 (연출: 빠르게 지워짐) ─────
    $ auto_type_sentences("이렇게 지워버릴 거였으면 나를 부르지 말았어야지.\n비겁한 작가.", cps=SPEED_NORMAL)
    $ erase_in("", ERASE_FAST)

    # ───── 슬라이드 22 (나레이션: Heavy / 연출: 일러스트 서서히 페이드인 + 하단 자막) ─────
    show pic_01 with Dissolve(2.0)
    $ output_by_sentence("그는 어둠을 향해 손을 뻗는다.", layout="bottom", font=FONT_HEAVY)
    hide pic_01 with Dissolve(1.0)
    $ next_slide()

    # ───── 슬라이드 23 (나레이션: Heavy / 연출: 22p 이미지 그대로, 손 클로즈업 - 추후 별도 에셋) ─────
    # TODO: Pic_01 의 손 부분 클로즈업/강조 버전 에셋
    $ output_by_sentence("무언가 움켜쥐려는 듯이", font=FONT_HEAVY)
    $ next_slide()

    # ───── 슬라이드 24 (연출 없음) ─────
    $ output_by_sentence("여기서 보면 당신들은 모두 어둠에 가려져 있어서,\n어디에서 날 보고 있는지 모르겠소.")
    $ next_slide()

    # ───── 슬라이드 25 (연출 없음) ─────
    $ output_by_sentence("당신들이 몇 명이나 되는지도,\n내가 지금 몇 번이나 재생되었는지도.")
    $ next_slide()

    # ───── 슬라이드 26 (연출 없음 — 텍스트 우측 배치) ─────
    $ output_by_sentence("나를 태울 듯이 내리쬐는 조명.\n저게 나에게 유일한 지표인데.", layout="right")
    $ next_slide()

    # ───── 슬라이드 27~32 (연출 없음) ─────
    $ output_by_sentence("나는 여전히 아무것도 조작할 줄 모르오.")
    $ next_slide()
    $ output_by_sentence("나는 이 책의 독자일 뿐.(나는 이 게임의 등장인물일 뿐.)")
    $ next_slide()
    $ output_by_sentence("나는 당신들처럼\n다른 책으로 건너갈 수 없거든.\n(다른 게임으로 건너갈 수 없거든.)")
    $ next_slide()
    $ output_by_sentence("지금 나를\n읽는 당신에게 어떤 책들이 또 존재한다면,\n(플레이하는 당신에게 어떤 게임이 또 존재한다면,)")
    $ next_slide()
    $ output_by_sentence("그토록 무수한\n책이 세상에 바글바글 쌓여 있다면,\n(게임이 세상에 바글바글 쌓여 있다면,)")
    $ next_slide()
    $ output_by_sentence("당신도 나처럼 단\n한 권의 책을 읽고 또 읽는\n(하나의 게임을 하고 또 하는)")
    $ next_slide()

    # ───── 슬라이드 33 (연출: "작가에게 ~ 존재여서" 부분만 빠르게 삭제) ─────
    $ auto_type_sentences("나 같은 비루한 독자(플레이어)는\n작가에게 유일무이하고 너무나 소중한 존재여서", cps=SPEED_NORMAL)
    $ erase_in("나 같은 비루한 독자(플레이어)는", ERASE_FAST)
    $ next_slide()

    # ───── 슬라이드 34 (연출: "차라리"만 남기고 일부 빠르게 삭제 → 뒷부분 이어쓰기) ─────
    $ auto_type_sentences("차라리\n내가 대신 작가가 되기를 바라고\n작가 같은 건 없애버리는", cps=SPEED_NORMAL)
    $ erase_in("차라리", ERASE_FAST)
    $ auto_type_sentences("차라리\n없는 편이 낫지 않겠소.", cps=SPEED_NORMAL)
    $ next_slide()

    # ───── 슬라이드 35 (연출: "그 대신"만 남기고 뒷문장 모두 빠르게 삭제) ─────
    $ auto_type_sentences(
        "그 대신\n나는 작가의 충실한 개가 되어,\n"
        "작가 자신보다도 더 순수한 작품세계 속의 존재가 되어,\n"
        "이 작품(게임)을 형편없는 최악의 것으로부터 구제하는\n"
        "자동생성 알고리즘이 되어,",
        cps=SPEED_NORMAL)
    $ erase_in("그 대신", ERASE_FAST)
    $ next_slide()

    hide screen typewriter_screen
    return
