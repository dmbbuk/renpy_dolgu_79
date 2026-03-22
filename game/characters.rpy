# 1. '그' (남자) - 시집을 읽고 R버튼을 찾는 주체
# 우울하고 차분한 회색/보라색 톤
define m = Character('그', color="#a8a8cf")

# 2. '나' (독자) - 1인칭 주인공 시점
# 중립적인 흰색 또는 옅은 하늘색
define me = Character('나', color="#c8ffc8")

# 3. 시스템 / 경고문 - 메타적인 메시지, 삭제 알림
# 기계적인 느낌의 강렬한 색상 (빨간색 혹은 터미널 녹색)
# [비프음]을 텍스트로 그대로 출력하려면 대괄호를 두 번 써야 합니다 [[
# define sys = Character('시스템', color="#ff4040", what_prefix="[[비프음] ")
define sys = Character('시스템', color="#ff4040")

# 4. NPC / 군중 - 해변의 NPC, 시인들
# 이름이 고정되지 않은 캐릭터를 위해 dynamic param 사용 가능, 여기선 단순하게 정의
define npc = Character('NPC', color="#ffcccc")

# 5. 이름 없는 서술 (Narrator)
# 렌파이 기본 narrator를 그대로 사용하면 됩니다. (별도 정의 불필요)
