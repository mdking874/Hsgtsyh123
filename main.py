import os
import subprocess
import logging
from telegram.ext import Updater, MessageHandler, Filters

# আপনার Bot Token এখানে দিন
TOKEN = 'OPIBKk'771526754:AAF338IlEXNXwXQ_y-Zwiop0JQdu3OPIBKk'
FRAME_PATH = 'frame.jpg'

logging.basicConfig(level=logging.INFO)

# ছবি (Frame) হ্যান্ডল করার ফাংশন
def handle_photo(update, context):
    # ইউজার যদি কোনো ছবি পাঠায়, সেটাকে frame.jpg নামে সেভ করবে
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(FRAME_PATH)
    update.message.reply_text("অভিনন্দন! আপনার ফ্রেমটি সেট করা হয়েছে। এখন সিরিয়াল ভিডিও পাঠান। ✅")

# ভিডিও প্রসেস করার ফাংশন
def handle_video(update, context):
    # আগে চেক করবে ফ্রেম সেভ করা আছে কি না
    if not os.path.exists(FRAME_PATH):
        update.message.reply_text("আগে আপনার ফ্রেমের ছবিটি (Frame) পাঠান, তারপর ভিডিও পাঠান।")
        return

    update.message.reply_text("ভিডিওটি পাওয়া গেছে। এডিটিং শুরু হচ্ছে, দয়া করে অপেক্ষা করুন... ⏳")
    
    video_file = update.message.video.get_file()
    input_name = "input.mp4"
    output_name = "final_output.mp4"
    video_file.download(input_name)

    # FFmpeg কমান্ড: মিরর ইফেক্ট + ফ্রেমের ভেতর সেট করা + অডিও চেঞ্জ
    cmd = (
        f'ffmpeg -i "{input_name}" -i "{FRAME_PATH}" '
        f'-filter_complex "[0:v]hflip,scale=615:420[inner];[1:v][inner]overlay=25:150" '
        f'-af "asetrate=44100*1.05,atempo=1.05" '
        f'-vcodec libx264 -crf 28 -preset fast "{output_name}"'
    )
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        with open(output_name, 'rb') as v:
            update.message.reply_video(v, caption="আপনার কপিরাইট ফ্রি ভিডিও তৈরি! ✅")
    except Exception as e:
        update.message.reply_text(f"এডিট করতে সমস্যা হয়েছে: {e}")
    
    # মেমোরি খালি করার জন্য ইনপুট ও আউটপুট ভিডিও ডিলিট করা
    if os.path.exists(input_name): os.remove(input_name)
    if os.path.exists(output_name): os.remove(output_name)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # ছবি পাঠালে এই ফাংশন চলবে
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    
    # ভিডিও পাঠালে এই ফাংশন চলবে
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    
    print("বট চালু হয়েছে...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
