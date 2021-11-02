import datetime
import cv2
import os
import time
from logging import getLogger

# Self-made module
import log

# Log設定
LOG_PATH = "./webcam/Log/" #Logファイル保存先
logger = getLogger(__name__)
log.set_log_config(logger, LOG_PATH, 'webcam.log')


class WebCamTimeLapse:

    def __init__(self, mp4_fps, resize_ratio, video_path, remark):
        
        # ファイルパス
        self.VIDEO_PATH = video_path #Videoデータ保存先
        self.remark = remark

        # 時間ごとに処理するための比較用変数
        dt_now = datetime.datetime.now()
        self.previous_sec = dt_now.second
        self.previous_min = dt_now.minute
        self.previous_hour = dt_now.hour

        # Fourcc (MP4)
        self.fourcc = cv2.VideoWriter_fourcc("m","p","4","v") 

        # Video保存設定
        self.mp4_fps = mp4_fps #FPS for timelapse
        self.resize_ratio = resize_ratio # 縮小比率
        

    def timelapse(self):

        logger.info('Start timelapse')

        try:

            # MP4保存先
            filename = self.__get_video_dir()

            # Webカメラ用インスタンス     
            cap = cv2.VideoCapture(0) # 引数でカメラ指定

            # Webカメラ情報取得    
            fps = int(cap.get(cv2.CAP_PROP_FPS)) # FPS    
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # Width   
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # Height
            logger.info(f'FPS={fps} Width={w} Hight={h}')

            # 設定にしたがってサイズ等分 1ならそのまま 2なら半分
            mp4_w = int(w/self.resize_ratio)
            mp4_h = int(h/self.resize_ratio)

            # Video保存用インスタンス
            video = cv2.VideoWriter(filename, self.fourcc, self.mp4_fps, (mp4_w,mp4_h))

            # Webカメラ安定タイマー
            time.sleep(2) #s

            while True:
                #１フレーム読み込み
                ret, img = cap.read()

                # Movie表示
                dt_now = datetime.datetime.now()
                dt_str = dt_now.strftime('%Y/%m/%d %H:%M:%S')
                cv2.putText(img, dt_str,(0,30), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2, cv2.LINE_AA)
                try:
                    cv2.imshow("image", img)
                except Exception as e:
                    logger.exception(e)

                # 1秒ごとにムービー保存
                if self.__compare_sec():
                    
                    # 1時間ごとに保存ファイル切り替え
                    if self.__compare_hour():
                        
                        # 日付変わったとき用にファイルパス更新
                        filename = self.__get_video_dir()

                        # Video保存用インスタンス更新
                        video.release()
                        video = cv2.VideoWriter(filename, self.fourcc, self.mp4_fps, (mp4_w,mp4_h))
                    
                    try:
                        video.write(cv2.resize(img,(mp4_w,mp4_h)))
                    except Exception as e:
                        logger.exception(e)

                # キー入力受付 & ループディレイ
                k = cv2.waitKey(50) #ms
                if k == 27: # ESCで終了
                    break

        except KeyboardInterrupt: # ターミナルCtrl+C強制終了
            logger.info(f"KeyboardInterrupt")

        except Exception as e:
            logger.exception(e)

        finally:
            #終了処理
            video.release()
            cap.release()
            cv2.destroyAllWindows()
            logger.info('Finished')


    def __get_video_dir(self):

        dt_now = datetime.datetime.now()

        day_folder = dt_now.strftime("%Y%m%d")
        video_dir = self.VIDEO_PATH + day_folder+'_'+self.remark
        os.makedirs(video_dir, exist_ok=True)
        filename = video_dir +"/"+ dt_now.strftime("%Y%m%d_%H%M%S") + ".mp4"

        logger.info(filename)

        return filename


    def __compare_sec(self):

        dt_now = datetime.datetime.now()
        now = dt_now.second

        if self.previous_sec == now:
            return False
        else:
            self.previous_sec = now
            return True


    def __compare_min(self):

        dt_now = datetime.datetime.now()
        now = dt_now.minute

        if self.previous_min == now:
            return False
        else:
            self.previous_min = now
            return True


    def __compare_hour(self):

        dt_now = datetime.datetime.now()
        now = dt_now.hour

        if self.previous_hour == now:
            return False
        else:
            self.previous_hour = now
            return True


if __name__ == "__main__":

    logger.info('App start')
    mp4_fps = 60
    resize_ratio = 1
    video_path = './Video/'
    remark = 'GC3_OCVIR'

    # タイムラプスのインスタンス
    tl = WebCamTimeLapse(mp4_fps, resize_ratio, video_path, remark)       
    tl.timelapse()