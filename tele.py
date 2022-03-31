import telegram
from telegram.ext import Updater, CommandHandler

# [0]에서 메모한 정보를 넣어주세요
my_api_key = "5153253987:AAHJRC1fvAmk0Die3mzkTBIcQwbEc1mBYgA"   #내 API 키 정보
chat_room_id = 5267710018   # 채팅방 ID

# 세팅
my_bot = telegram.Bot(my_api_key)
updater = Updater(my_api_key)       # 메시지가 있는지 체크
updater.dispatcher.stop()
updater.job_queue.stop()
updater.stop()

# 명령어와 연결할 기능 구현
def TestPrint(bot, update):
    my_bot.sendMessage(chat_id=chat_room_id, text="hello~")

# 기능과 명령어 연결("/hi" 명령어가 들어오면 TestPrint 함수가 실행됨)
updater.dispatcher.add_handler(CommandHandler("hi", TestPrint))

# 시작
updater.start_polling()
updater.idle()
