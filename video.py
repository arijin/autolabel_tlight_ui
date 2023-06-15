import os
import glob
import cv2

def create_video_from_images(folder_path, output_video):
    # 获取文件夹中以.jpg结尾的所有图片文件
    image_files = glob.glob(os.path.join(folder_path, "*.jpg"))
    
    # 对文件列表进行自然排序
    image_files = sorted(image_files)
    
    # 输出视频的参数
    output_width = 1920  # 输出视频的宽度
    output_height = 1080  # 输出视频的高度
    fps = 20  # 输出视频的帧率
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 输出视频的编码格式
    
    # 创建VideoWriter对象
    output = cv2.VideoWriter(output_video, fourcc, fps, (output_width, output_height))
    
    # 逐个读取图片文件并写入输出视频
    for image_file in image_files:
        image = cv2.imread(image_file)
        resized_image = cv2.resize(image, (output_width, output_height))
        output.write(resized_image)
    
    # 释放资源并关闭输出视频
    output.release()


# 调用函数创建视频
root_dir = r"C:\Users\qj00241.7HORSE\Downloads\test_data\TlightClipData"
clips_imgs_dir = os.path.join(root_dir, "tl_imgs")

clip_name = "clp_1675339721350"
clip_img_dir = os.path.join(clips_imgs_dir, clip_name)
output_video = os.path.join(clips_imgs_dir, f"{clip_name}.mp4")
create_video_from_images(clip_img_dir, output_video)
