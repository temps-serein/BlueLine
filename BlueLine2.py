import os
import time

import cv2
import numpy as np

"""
copyright@B站 天边的哔哩哔哩
2022/10/6 本版本为实时转换版本，为兼顾实时转换效率，不设置固定时限（如10s内完成动作），以蓝线全部通过截止
故理论时长为（图像高度/每帧取宽）/帧率 ，因为计算速度问题，实际耗时会更长些
"""


def img_to_video(output_video_path, frame_dirpath, fps):
    """
    将处理好的帧图片合成视频
    :param output_video_path: 输出视频的地址
    :param frame_dirpath: 帧图片所在文件夹地址
    :param fps: 输出帧率
    :return: None
    """
    img = cv2.imread(f"{frame_dirpath}/1.jpg")
    hight, width, _ = img.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    videoWriter = cv2.VideoWriter(output_video_path, fourcc, fps, (width, hight))
    order = [int(i.strip(".jpg")) for i in os.listdir(frame_dirpath) if i.endswith(".jpg")]
    jpglist = [f"{frame_dirpath}/{i}.jpg" for i in sorted(order)]  # 直接读取可能非顺序帧
    for i, jpg in enumerate(jpglist):
        img = cv2.imread(filename=jpg)
        videoWriter.write(img)
        print(f"将字符画写入视频, 进度{(i + 1)}/{len(jpglist)}！")
    videoWriter.release()
    print(f"{output_video_path} 输出完成！")


def main(output_frame_dirpath, output_video_path, fps=30, axis=0, width_blueline=3, \
         pixel_number_each_frame=5, countdown_time=5):
    """
    主函数
    :param output_frame_dirpath: 输出帧的文件夹地址
    :param output_video_path: 输出视频的存放地址
    :param fps: 图像帧率
    :param axis: 处理的方向，0代表从上到下扫描，1为从左到右扫描
    :param width_blueline:蓝线宽度，不区水平或竖直方向
    :param pixel_number_each_frame: 每帧截取的像素厚度，越大则越快扫描完成
    :param countdown_time: 开始扫描的倒计时时长
    :return: None
    """
    video_c = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    width = int(video_c.get(3))
    hight = int(video_c.get(4))
    video_c.set(5, fps)  # 设置摄像头的FPS

    canvas = np.zeros((hight, width, 3))
    if axis == 0:
        array_blueline = np.array([[[255, 255, 0] for _ in range(width)] for _ in range(width_blueline)])
    else:
        array_blueline = np.array([[[255, 255, 0] for _ in range(width_blueline)] for _ in range(hight)])
    starttime = time.time()
    frame_index, row_index, column_index, count = 0, 0, 0, 0
    while row_index + pixel_number_each_frame < hight and column_index + pixel_number_each_frame < width:
        ret, frame = video_c.read()
        frame = cv2.flip(frame,1)
        if time.time() - starttime - countdown_time > 0:
            if axis == 0:
                canvas[row_index:row_index + pixel_number_each_frame] = frame[
                                                                        row_index:row_index + pixel_number_each_frame]
                row_index += pixel_number_each_frame
                if row_index + width_blueline < hight:
                    frame[:row_index] = canvas[:row_index]
                    frame[row_index:row_index+ width_blueline] = array_blueline
                    cv2.imshow('Viewer', frame / 255)
            else:
                canvas[:, column_index: column_index + pixel_number_each_frame] = \
                    frame[:, column_index: column_index + pixel_number_each_frame]
                column_index += pixel_number_each_frame
                if column_index + width_blueline < width:
                    frame[:,:column_index] = canvas[:,:column_index]
                    frame[:, column_index:column_index + width_blueline] = array_blueline
                    cv2.imshow('Viewer', frame / 255)
        else:
            cv2.imshow('Viewer', frame)
        cv2.imwrite(f'{output_frame_dirpath}/{count}.jpg', frame)
        print(f'{output_frame_dirpath}/{count}.jpg')
        count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    img_to_video(output_video_path, output_frame_dirpath,fps)
    video_c.release()
    cv2.destroyAllWindows()
    # cv2.waitKey()


if __name__ == '__main__':
    output_frame_dirpath = 'resource/output'
    output_video_path = 'resource/321.mp4'
    axis = 0
    fps = 30
    main(output_frame_dirpath, output_video_path, axis=axis)
