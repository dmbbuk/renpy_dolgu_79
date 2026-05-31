init python:
    import random

    _typing_clips = [
        "audio/typing1.mp3",
        "audio/typing2.mp3",
        "audio/typing3.mp3",
        "audio/typing4.mp3",
        "audio/typing5.mp3",
    ]

    # ─ 속도 프리셋 ─
    # 타이핑 cps (chars per second). 30자 문장 기준 대략 총 시간:
    SPEED_NORMAL = 10   # 보통 ≈ 3초
    SPEED_FAST = 15     # 빠르게 ≈ 2초
    SPEED_VFAST = 30    # 아주 빠르게 ≈ 1초
    # 슬라이드 19(200자+) 전용 — 사용자 지시 "3배 더 빠르게" (원본 40 cps → 120)
    SPEED_RAPID = 120

    # 삭제 총 시간(초). erase_in(target, seconds) 의 seconds 인자로 직접 사용.
    ERASE_NORMAL = 3.0  # 보통
    ERASE_FAST = 2.0    # 빠르게
    ERASE_VFAST = 1.0   # 아주 빠르게

    $ quick_menu = False  #하단 옵션 삭제

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

    def auto_type(target, cps=SPEED_NORMAL, sound=True, layout="center"):
        # 현재 텍스트 → target 으로 한 글자씩 자동 전이 (클릭 없음, 공백 스킵).
        # 공통 접두사 이후를 뒤에서부터 삭제 → target 의 나머지를 타이핑.
        cp = _common_prefix_len(store.current_text, target)
        while len(store.current_text) > cp:
            removed = store.current_text[-1]
            store.current_text = store.current_text[:-1]
            renpy.show_screen("typewriter_screen", store.current_text, layout=layout)
            if removed == " ":
                continue
            if sound:
                play_typing()
            renpy.pause(1.0 / cps, hard=True)
        while len(store.current_text) < len(target):
            next_c = target[len(store.current_text)]
            store.current_text = target[: len(store.current_text) + 1]
            renpy.show_screen("typewriter_screen", store.current_text, layout=layout)
            if next_c == " ":
                continue
            if sound:
                play_typing()
            renpy.pause(1.0 / cps, hard=True)

    def auto_type_sentences(target, cps=SPEED_NORMAL, sound=True, layout="center"):
        # target 으로 자동 전이 + 추가되는 텍스트를 마침표 단위로 끊어 청크 끝마다 클릭 대기.
        cp = _common_prefix_len(store.current_text, target)
        # 1) 공통 접두사까지 자동 삭제 (클릭 없음)
        if len(store.current_text) > cp:
            auto_type(store.current_text[:cp], cps=cps, sound=sound, layout=layout)
        # 2) 추가 부분을 청크별로 자동 타이핑 + 청크 끝 클릭
        to_add = target[cp:]
        chunks = _split_chunks(to_add)
        accumulated = store.current_text
        for chunk in chunks:
            accumulated += chunk
            auto_type(accumulated, cps=cps, sound=sound, layout=layout)
            renpy.pause()

    def erase_in(target, seconds, sound=True, layout="center"):
        # 현재 텍스트 → target 까지 총 seconds 안에 자동 전이 (삭제 + 추가 통합).
        cp = _common_prefix_len(store.current_text, target)
        change = (
            sum(1 for c in store.current_text[cp:] if c != " ")
            + sum(1 for c in target[cp:] if c != " ")
        )
        if change <= 0:
            return
        cps = change / max(seconds, 0.01)
        auto_type(target, cps=cps, sound=sound, layout=layout)

    def output_by_sentence(text, layout="center"):
        # "연출 없음" 슬라이드용. 마침표 단위 청크 통째로 출력 + 버스트 사운드.
        chunks = _split_chunks(text)
        accumulated = store.current_text
        for chunk in chunks:
            accumulated += chunk
            store.current_text = accumulated
            renpy.show_screen("typewriter_screen", store.current_text, layout=layout)
            burst_count = max(3, min(len(chunk) // 4, 10))
            play_typing_burst(burst_count)
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

screen typewriter_screen(text, layout="center"):
    if layout == "right":
        text text:
            xalign 0.75
            yalign 0.5
            xsize 900
            text_align 0.0
    else:
        text text:
            xalign 0.5
            yalign 0.5
            xsize 1400
            text_align 0.0


label start:
    $ current_text = ""
    show screen typewriter_screen("")

    # ───── 슬라이드 2~4 (연출: 한 글자씩 → 한 글자씩 삭제, 보통 속도) ─────
    $ auto_type_sentences("모든 작가는 글을 쓰려는 힘과\n글을 지우려는 힘을 동시에 지니고 있다.", cps=SPEED_NORMAL)
    $ erase_in("", ERASE_NORMAL)
    $ auto_type_sentences("대부분의 작가에게는\n지우려는 힘이 더 강하다.", cps=SPEED_NORMAL)
    $ erase_in("", ERASE_NORMAL)
    $ auto_type_sentences("그건 자신의 미숙함을 들키지 않는다는\n점에서 최악은 아니다.", cps=SPEED_NORMAL)
    $ erase_in("", ERASE_NORMAL)

    # ───── 슬라이드 5~7 (연출: 부분 삭제 반복 — "최악은 역시" 유지) ─────
    $ auto_type_sentences("최악은 역시, 형편없는 작품을\n미처 지우지도 못하고 계속 써내려 가는 것.", cps=SPEED_NORMAL)
    $ erase_in("최악은 역시", ERASE_NORMAL)
    $ auto_type_sentences("최악은 역시, 형편없는 작품을\n미처 지우지도", cps=SPEED_NORMAL)
    $ erase_in("최악은 역시", ERASE_NORMAL)
    $ auto_type_sentences("최악은 역시, 형편없는 작품", cps=SPEED_NORMAL)
    $ erase_in("", ERASE_NORMAL)

    # ───── 슬라이드 8 (연출: 3글자 + 2초 정지) ─────
    $ auto_type("최악은", cps=SPEED_NORMAL)
    $ renpy.pause(2.0, hard=True)
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

    # ───── 슬라이드 22~23 (연출: 일러스트 - 추후 에셋, 텍스트는 문장 단위 출력) ─────
    # TODO: 어두운 무대 + 수직 스포트라이트 + 손 뻗는 남자 일러스트
    $ output_by_sentence("그는 어둠을 향해 손을 뻗는다.")
    $ next_slide()
    $ output_by_sentence("무언가 움켜쥐려는 듯이")
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
