 ![img](https://i0.hdslb.com/bfs/article/1044bd4f7325c4d05c3641a0f210608719163226.jpg)

   在抖音曾经火了一阵子的蓝线挑战特效，其原理很简单：在蓝线经过后保留本帧的部分像素，形成蒙板图片，未经过处照常切换帧图片，再将蒙版图片贴到每帧图片上。本着我上我也行的想法，试着用opencv-python实现这个效果，做了摄像头版本和视频处理版本。 

![img](https://i0.hdslb.com/bfs/article/24e7330a8a6c87c4fe2cd1b6f3570adf6040bdda.png@942w_966h_progressive.webp)

## 1.摄像头版本       

从上述描述可知，在摄像头版本中可规定每帧取固定宽度像素，如2个像素，假设视频尺寸为640*480，则需要480/2=240帧，若视频帧率（每秒的帧数）为30，则运行8秒，实际受计算速度等影响会略大于这个值，以下为关键部位代码：

（1）从摄像头获取每帧图像 

```
video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
ret, frame = video.read()	# frame为np数组，宽100高200时，数组形状为200 * 100 *3
frame = cv2.flip(frame,1) # 左右翻转图像为镜像 
```

（2）制作蒙版图片，并取每帧的固定数量的像素 

```Python
#通过row_index记录当前的行索引，获取像素作为蒙版图片
canvas[row_index:row_index + pixel_number_each_frame] = \
	\frame[row_index:row_index + pixel_number_each_frame]
row_index += pixel_number_each_frame	# 每次运行增加固定像素宽度
if row_index + width_blueline < hight:	# 避免因为增加固定像素，导致超出图像的高度
	frame[:row_index] = canvas[:row_index]	# 将每帧的图像上部替换为蒙版图片
	frame[row_index:row_index+ width_blueline] = array_blueline	# 添加蓝线矩阵
   # 窗口显示，BUG在于frame数据为浮点数时默认RGB数值范围0~1，当为整数时为0~255
	cv2.imshow('Viewer', frame / 255)
```

 （3）将处理完的图片及时保存，便于后期导出视频

```python
cv2.imwrite(f'{output_frame_dirpath}/{count}.jpg', frame)
```

（4）合成视频

```python
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
    order = [int(i.strip(".jpg")) for i in os.listdir(frame_dirpath) if 						i.endswith(".jpg")]
    jpglist = [f"{frame_dirpath}/{i}.jpg" for i in sorted(order)]
    for i, jpg in enumerate(jpglist):
        img = cv2.imread(filename=jpg)
        videoWriter.write(img)
        print(f"将字符画写入视频, 进度{(i + 1)}/{len(jpglist)}！")
    videoWriter.release()
    print(f"{output_video_path} 输出完成！")
```

## **2. 视频处理版本**

​    与摄像头版本不同，视频版本需要获取视频信息以做处理。

（1）将视频抽帧为图片

```python
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
```

​    （2）获取视频基本信息

```python
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
```

​    （3）计算相关参数。新视频的时长即为扫描时长，即每帧抽取像素= 图片高度 / 总帧数，此时需要取整，且取整误差=图片高度 - 每帧抽取像素* 总帧数，不处理会导致蓝线无法在时长内扫描完整个高度

```python
array_blueline = np.array([[[255, 255, 0] for _ in range(width)] for _ in 				  range(width_blueline)])
pixel_number_each_frame = int(hight / frame_number) # 每次取帧截取的像素范围
err = hight - pixel_number_each_frame * frame_number - 3 # 误差值分散到每帧，留3个像素给蓝线
```

​    （4）将误差分散到较前的帧图片中

```python
if err_count < err:
	canvas[row_index:row_index + pixel_number_each_frame + 1] = img[row_index:row_index + pixel_number_each_frame + 1]
  row_index += pixel_number_each_frame + 1
  err_count += 1	# 计算误差部分是否使用完
else:
   canvas[row_index:row_index + pixel_number_each_frame] = img[row_index:row_index + pixel_number_each_frame]
  row_index += pixel_number_each_frame
  if row_index + width_blueline <= hight:	# 避免索引跑出图片范围而报错
   		img[:row_index] = canvas[:row_index]
   		img[row_index:row_index+ width_blueline] = array_blueline
```

​    （5）将图片重新合成视频，同摄像头版本，不再赘述.



参考：

[抖音“蓝线挑战”特效是怎么实现的-技术圈 (proginn.com)](https://jishuin.proginn.com/p/763bfbd67c82)

https://github.com/githubhaohao/OpenGLCamera2