import cv2
import time
from logging import getLogger

# Self-made module
import log
from video import WebCam

# Log設定
LOG_PATH = "./Log/" #Logファイル保存先
logger = getLogger(__name__)
log.set_log_config(logger, LOG_PATH, 'timelapse.log')



if __name__ == "__main__":

    logger.info('App start')
    resize_ratio = 1
    video_path = './Video/'
    remark = 'timelapse'

    # webcamインスタンス
    wc = WebCam(video_path, remark) 
    wc.start_webcam(0)

    fps = 30

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
            
            if wc.compare_sec():

                try:
                    wc.save_video(img)
                except Exception as e:
                    logger.exception(e)

            # キー入力受付 & ループディレイ
            k = cv2.waitKey(10) #ms
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
