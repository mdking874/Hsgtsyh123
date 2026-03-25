import os
import subprocess
import logging
from telegram.ext import Updater, MessageHandler, Filters

# আপনার Bot Token এখানে দিন
TOKEN = 'আপনার_বট_টোকেন_এখানে'
FRAME_PATH = 'frame.jpg'

logging.basicConfig(level=logging.INFO)

def process_video(update, context):
    message = update.message
    if not os.path.exists(FRAME_PATH):
        message.reply_text("frame.jpg ফাইলটি পাওয়া যায়নি!")
        return

    message.reply_text("ভিডিও প্রসেসিং শুরু হচ্ছে... সময় লাগবে।")
    
    video_file = message.video.get_file()
    input_name = "input.mp4"
    output_name = "final_output.mp4"
    video_file.download(input_name)

    # ভিডিও এডিটিং কমান্ড
    cmd = (
        f'ffmpeg -i "{input_name}" -i "{FRAME_PATH}" '
        f'-filter_complex "[0:v]hflip,scale=615:420[inner];[1:v][inner]overlay=25:150" '
        f'-af "asetrate=44100*1.05,atempo=1.05" '
        f'-vcodec libx264 -crf 28 -preset fast "{output_name}"'
    )
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        with open(output_name, 'rb') as v:
            message.reply_video(v, caption="সফলভাবে তৈরি হয়েছে! ✅")
    except Exception as e:
        message.reply_text(f"Error: {e}")
    
    if os.path.exists(input_name): os.remove(input_name)
    if os.path.exists(output_name): os.remove(output_name)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.video, process_video))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
