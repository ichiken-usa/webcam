import datetime
import cv2
import os
import time
from logging import getLogger

# Self-made module
import log

# Log設定
LOG_PATH = "./Log/" #Logファイル保存先
logger = getLogger(__name__)
log.set_log_config(logger, LOG_PATH, 'video.log')


class WebCam:

    def __init__(self, video_path, remark):
        
        # ファイルパス
        self.video_path = video_path #Videoデータ保存先
        self.remark = remark

        # 時間ごとに処理するための比較用変数
        dt_now = datetime.datetime.now()
        self.previous_sec = dt_now.second
        self.previous_min = dt_now.minute
        self.previous_hour = dt_now.hour

        # Fourcc (MP4)
        self.fourcc = cv2.VideoWriter_fourcc("m","p","4","v") 



    def start_webcam(self, camera_num):
        # Webカメラ用インスタンス     
        self.cap = cv2.VideoCapture(camera_num) # 引数でカメラ指定
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) # FPS    
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # Width   
        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # Height
        logger.info(f'FPS={self.fps} Width={self.w} Hight={self.h}')   

    def change_video_size(self, resize_ratio):
        # 設定にしたがってサイズ等分 1ならそのまま 2なら半分
        self.w = int(self.w/resize_ratio)
        self.h = int(self.h/resize_ratio)

    def update_video_path(self):

        dt_now = datetime.datetime.now()
        day_folder = dt_now.strftime("%Y%m%d")
        dir = self.video_path + day_folder+'_'+ self.remark
        os.makedirs(dir, exist_ok=True)
        self.video_full_path = dir +"/"+ dt_now.strftime("%Y%m%d_%H%M%S") + ".mp4"

        logger.info(self.video_full_path)

    def set_video_writer(self, fps):
        self.video_writer = cv2.VideoWriter(self.video_full_path, self.fourcc, fps, (self.w,self.h))

    def refresh_video_writer(self):
        self.video_writer.release()
        self.set_video_writer()

    def save_video(self, img):
        self.video_writer.write(cv2.resize(img,(self.w,self.h)))

    def read_image(self):
        ret, img = self.cap.read()
        return img

    def add_current_time(self, img):
        dt_now = datetime.datetime.now()
        dt_str = dt_now.strftime('%Y/%m/%d %H:%M:%S')
        cv2.putText(img, dt_str,(0,30), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2, cv2.LINE_AA)
        return img

    def compare_sec(self):

        dt_now = datetime.datetime.now()
        now = dt_now.second

        if self.previous_sec == now:
            return False
        else:
            self.previous_sec = now
            return True

    def compare_min(self):

        dt_now = datetime.datetime.now()
        now = dt_now.minute

        if self.previous_min == now:
            return False
        else:
            self.previous_min = now
            return True

    def compare_hour(self):

        dt_now = datetime.datetime.now()
        now = dt_now.hour

        if self.previous_hour == now:
            return False
        else:
            self.previous_hour = now
            return True



if __name__ == "__main__":

    logger.info('App start')
    resize_ratio = 1
    video_path = './Video/'
    remark = 'video'

    # webcamインスタンス
    wc = WebCam(video_path, remark)       

    wc.start_webcam(0)

    fps = wc.fps

    try:

        # 設定にしたがってサイズ等分 1ならそのまま 2なら半分
        wc.change_video_size(resize_ratio)

        # MP4保存先を更新
        wc.update_video_path()

        # Video保存用インスタンス
        wc.set_video_writer(fps)

        # Webカメラ安定タイマー
        time.sleep(2) #s

        while True:
            #１フレーム読み込み
            img = wc.read_image()

            # 画面に時間表示追加
            img = wc.add_current_time(img)

            try:
                cv2.imshow("image", img)
            except Exception as e:
                logger.exception(e)
            
            # 1時間ごとに保存ファイル切り替え
            if wc.compare_hour():
                
                # ファイルパス更新
                wc.update_video_path()

                # Video保存用インスタンス更新
                wc.refresh_video_writer(fps)
            
            try:
                wc.save_video(img)
            except Exception as e:
                logger.exception(e)

            # キー入力受付 & ループディレイ
            k = cv2.waitKey(1) #ms
            if k == 27: # ESCで終了
                break

    except KeyboardInterrupt: # ターミナルCtrl+C強制終了
        logger.info(f"KeyboardInterrupt")

    except Exception as e:
        logger.exception(e)

    finally:
        #終了処理
        
        del wc
        cv2.destroyAllWindows()
        logger.info('Finished')
