import os
import subprocess
import logging
from telegram.ext import Updater, MessageHandler, Filters

# আপনার সঠিক টোকেনটি এখানে বসানো হয়েছে
TOKEN = '771526754:AAF338IlEXNXwXQ_y-Zwiop0JQdu3OPIBKk'
FRAME_PATH = 'frame.jpg'

# লগিং সেটআপ (বটে কোনো সমস্যা হলে তা দেখার জন্য)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ১. ফটো বা ফ্রেম হ্যান্ডল করার ফাংশন
def handle_photo(update, context):
    try:
        # ইউজার যদি কোনো ছবি পাঠায়, সেটাকে frame.jpg নামে সেভ করবে
        photo_file = update.message.photo[-1].get_file()
        photo_file.download(FRAME_PATH)
        update.message.reply_text("অভিনন্দন! আপনার ফ্রেমটি সেভ করা হয়েছে। এখন সিরিয়াল ভিডিও পাঠান। ✅")
    except Exception as e:
        update.message.reply_text(f"ফ্রেম সেভ করতে সমস্যা হয়েছে: {e}")

# ২. ভিডিও প্রসেস করার ফাংশন
def handle_video(update, context):
    # আগে চেক করবে ফ্রেম সেভ করা আছে কি না
    if not os.path.exists(FRAME_PATH):
        update.message.reply_text("আগে আপনার ফ্রেমের ছবিটি (Frame Photo) পাঠান, তারপর ভিডিও পাঠান।")
        return

    update.message.reply_text("ভিডিওটি পাওয়া গেছে। এডিটিং শুরু হচ্ছে, দয়া করে কয়েক মিনিট অপেক্ষা করুন... ⏳")
    
    video_file = update.message.video.get_file()
    input_name = "input_video.mp4"
    output_name = "final_output.mp4"
    
    try:
        # ভিডিও ডাউনলোড করা
        video_file.download(input_name)

        # FFmpeg কমান্ড: মিরর ইফেক্ট + ফ্রেমের ভেতর সেট করা + অডিও চেঞ্জ
        # scale=615:420 এবং overlay=25:150 আপনার দেওয়া ছবির বক্সের মাপে সেট করা
        cmd = (
            f'ffmpeg -y -i "{input_name}" -i "{FRAME_PATH}" '
            f'-filter_complex "[0:v]hflip,scale=615:420[inner];[1:v][inner]overlay=25:150" '
            f'-af "asetrate=44100*1.05,atempo=1.05" '
            f'-vcodec libx264 -crf 28 -preset fast "{output_name}"'
        )
        
        # কমান্ডটি রান করা
        subprocess.run(cmd, shell=True, check=True)
        
        # এডিট করা ভিডিওটি টেলিগ্রামে ফেরত পাঠানো
        with open(output_name, 'rb') as v:
            update.message.reply_video(v, caption="আপনার ভিডিও তৈরি! এখন ইউটিউবে আপলোড করতে পারেন। ✅")
            
    except Exception as e:
        update.message.reply_text(f"এডিট করতে সমস্যা হয়েছে: {e}")
    
    # মেমোরি খালি করার জন্য সাময়িক ফাইলগুলো ডিলিট করা
    if os.path.exists(input_name): os.remove(input_name)
    if os.path.exists(output_name): os.remove(output_name)

# ৩. মেইন ফাংশন বট চালু করার জন্য
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # ছবি পাঠালে 'handle_photo' ফাংশন চলবে
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    
    # ভিডিও পাঠালে 'handle_video' ফাংশন চলবে
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    
    print("বটটি চালু হয়েছে... এখন টেলিগ্রামে যান।")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
