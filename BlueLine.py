import os

import cv2
import numpy as np

"""
 本版本为视频转换版，每帧取宽 = 图像高度 / 总帧数
"""


def video_to_img(frame_dirpath, video_path):
    """
    将视频抽取为帧图片以便处理
    :param frame_dirpath: 存放抽取好的帧图片文件夹地址
    :param video_path: 视频地址
    :return: None
    """
    vc = cv2.VideoCapture(video_path)
    c = 0
    ret = vc.isOpened()
    while ret:
        c += 1
        ret, frame = vc.read()
        if ret:
            cv2.imwrite(f'{frame_dirpath}/{c}.jpg', frame)
            print(f'生成{frame_dirpath}/{c}.jpg')
        else:
            break
    vc.release()
    print("视频按各帧提取完成！")


def get_video_msg(video_path):
    """
    获取视频的基本信息
    :param video_path: 视频地址
    :return: [帧数量,[宽度,高度],帧率]
    """
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        frame_number = cap.get(7)
        width = cap.get(3)
        hight = cap.get(4)
        fps = cap.get(5)
        return [frame_number, [width, hight], fps]
    return [-1, -1, -1, [-1, -1], -1]


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


def main(video_path, frame_dirpath, output_frame_dirpath, output_video_path, axis = 0, width_blueline =3):
    """
    主函数
    :param video_path: 视频地址
    :param frame_dirpath: 抽取帧图片的文件夹地址
    :param output_frame_dirpath: 输出帧的文件夹地址
    :param output_video_path: 输出视频的存放地址
    :param axis: 处理的方向，0代表从上到下扫描，1为从左到右扫描
    :param width_blueline: 蓝线宽度，不区水平或竖直方向
    :return: None
    """
    frame_number, shape, fps = get_video_msg(video_path)
    width, hight = [int(shape[0]), int(shape[1])]
    if not os.path.exists(frame_dirpath):
        os.makedirs(frame_dirpath)
    if len(os.listdir(frame_dirpath)) != frame_number:
        video_to_img(frame_dirpath, video_path)
    if not os.path.exists(output_frame_dirpath):
        os.makedirs(output_frame_dirpath)

    if axis == 0:
        array_blueline = np.array([[[255, 255, 0] for _ in range(width)] for _ in range(width_blueline)])
        pixel_number_each_frame = int(hight / frame_number)  # 每次取帧截取的像素范围
        err = hight - pixel_number_each_frame * frame_number - 3  # 误差值分散到每帧，留3个像素给蓝线
    else:
        array_blueline = np.array([[[255, 255, 0] for _ in range(width_blueline)] for _ in range(hight)])
        pixel_number_each_frame = int(width / frame_number)  # 每次取帧截取的像素范围
        err = width - pixel_number_each_frame * frame_number - 3  # 误差值分散到每帧，留3个像素给蓝线

    canvas = np.zeros((hight, width, 3))

    frame_index, row_index, column_index, err_count = 0, 0, 0, 0
    while frame_index < frame_number:
        img = cv2.imread(os.path.join(frame_dirpath, f'{frame_index + 1}.jpg'))
        if axis == 0:
            if err_count < err:
                canvas[row_index:row_index + pixel_number_each_frame + 1] = img[
                                                                         row_index:row_index + pixel_number_each_frame + 1]
                row_index += pixel_number_each_frame + 1
                err_count += 1
            else:
                canvas[row_index:row_index + pixel_number_each_frame] = img[row_index:row_index + pixel_number_each_frame]
                row_index += pixel_number_each_frame
            if row_index + width_blueline <= hight:
                img[:row_index] = canvas[:row_index]
                img[row_index:row_index+ width_blueline] = array_blueline
        else:
            if err_count < err:
                canvas[:, column_index:column_index + pixel_number_each_frame + 1] = \
                    img[:, column_index:column_index + pixel_number_each_frame + 1]
                column_index += pixel_number_each_frame + 1
                err_count += 1
            else:
                canvas[:, column_index: column_index + pixel_number_each_frame] = \
                    img[:, column_index: column_index + pixel_number_each_frame]
                column_index += pixel_number_each_frame
            if column_index + width_blueline < width:
                img[:,:column_index] = canvas[:,:column_index]
                img[:, column_index:column_index + width_blueline] = array_blueline

        cv2.imwrite(os.path.join(output_frame_dirpath, f'{frame_index + 1}.jpg'), img)
        print(f'生成{output_frame_dirpath}/{frame_index + 1}.jpg')
        frame_index += 1
    img_to_video(output_video_path, output_frame_dirpath, fps)


if __name__ == '__main__':
    video_path = 'resource/123.mp4'
    frame_dirpath = 'resource/frame'
    output_frame_dirpath = 'resource/ouput'
    output_video_path= 'resource/321.mp4'
    axis = 0
    main(video_path, frame_dirpath, output_frame_dirpath, output_video_path, axis)
