from PIL import Image
import cv2 as cv
import os
import random
import shutil


def resize(src_img_path, output_dir, width=299, height=299):
    if not os.path.exists(src_img_path):
        print(src_img_path, 'not exist!')
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    src_img = Image.open(src_img_path)
    new_img = src_img.resize((width, height), Image.ANTIALIAS)
    new_img.save(output_dir)


def crop_to_299(src_img_path, output_dir):
    """
    把长宽不等的图片裁剪成正方形，再resize到299*299
    :param src_img_path:
    :param output_dir:
    :return:
    """
    if not os.path.exists(src_img_path):
        print(src_img_path, 'not exist!')
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    src_img = Image.open(src_img_path)
    width, height = src_img.size
    if width > height:
        diff = (width - height) // 2
        cropped = src_img.crop((diff, 0, width - diff, height))
    else:
        diff = (height - width) // 2
        cropped = src_img.crop((0, diff, width,height - diff))
    cropped = cropped.resize((299, 299), Image.ANTIALIAS)
    _, output_file_name = os.path.split(src_img_path)
    output_path = os.path.join(output_dir, output_file_name)
    cropped.save(output_path)


def random_move_file(src_dir, dst_dir, radio):
    """
    在src_dir中随机移动radio比例个文件到dst_dir
    :param src_dir:
    :param dst_dir:
    :param radio:
    :return:
    """
    if not os.path.isdir(src_dir):
        print(src_dir + ' is not a valid directory!')
        return
    elif radio < 0 or radio > 1:
        print('radio must be set between 0~1!')
        return
    else:
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        cnt = 0
        for file in os.listdir(src_dir):
            if random.random() <= radio:
                src_file = os.path.join(src_dir, file)
                dst_file = os.path.join(dst_dir, file)
                shutil.move(src_file, dst_file)
                print('moved ' + src_file + ' to ' + dst_file)
                cnt = cnt + 1
        print('Moved %d files.' % cnt)


if __name__ == '__main__':
    # test_img_path = 'data/images/3415304.jpg'
    # test_output_img = 'data/images/test_output'
    # crop_to_299(test_img_path, test_output_img)
    root_img_dir = r'data\images'
    for i in os.listdir(root_img_dir):
        if i.startswith('test'):
            continue
        screen_dir = os.path.join(root_img_dir, i)
        if os.path.isfile(screen_dir):
            continue
        for j in os.listdir(screen_dir):
            plate_dir = os.path.join(screen_dir, j)
            # print(plate_dir)
            if os.path.isdir(plate_dir):
                random_move_file(plate_dir, screen_dir, 1)
