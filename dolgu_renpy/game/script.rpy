init python:
    import random

    _typing_clips = [
        "audio/typing1.mp3",
        "audio/typing2.mp3",
        "audio/typing3.mp3",
        "audio/typing4.mp3",
        "audio/typing5.mp3",
    ]

    def play_typing():
        renpy.sound.play(random.choice(_typing_clips))

screen click_type_screen(text):
    text text:
        xalign 0.5
        yalign 0.5
        xsize 1400
        text_align 0.0

label click_type(fulltext):
    # 1) 타이핑: 클릭마다 한 글자씩 등장
    $ i = 0
    while i < len(fulltext):
        $ i += 1
        show screen click_type_screen(fulltext[:i])
        $ play_typing()
        pause
    # 2) 지우기: 클릭마다 최근 글자부터 한 글자씩 삭제
    while i > 0:
        $ i -= 1
        show screen click_type_screen(fulltext[:i])
        $ play_typing()
        pause
    hide screen click_type_screen
    return

label start:

    call click_type("모든 작가는 글을 쓰려는 힘과\n글을 지우려는 힘을 동시에 지니고 있다.")

    call click_type("대부분의 작가에게는\n지우려는 힘이 더 강하다.")

    return
