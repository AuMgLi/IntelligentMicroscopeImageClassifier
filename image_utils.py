from PIL import Image
import cv2 as cv
import os
import random
import shutil
import re


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
    _, output_file_name = os.path.split(src_img_path)
    output_path = os.path.join(output_dir, output_file_name)
    if os.path.exists(output_path):
        print(output_path, 'has existed, skip!')
        return
    width, height = src_img.size
    if width > height:
        diff = (width - height) // 2
        cropped = src_img.crop((diff, 0, width - diff, height))
    else:
        diff = (height - width) // 2
        cropped = src_img.crop((0, diff, width,height - diff))
    cropped = cropped.resize((299, 299), Image.ANTIALIAS)
    cropped.save(output_path)
    print(output_path, 'is saved.')


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
            src_file = os.path.join(src_dir, file)
            if os.path.isdir(src_file):
                print(src_file, 'is a directory, skip.')
                continue
            if random.random() <= radio:
                dst_file = os.path.join(dst_dir, file)
                shutil.move(src_file, dst_file)
                print('moved ' + src_file + ' to ' + dst_file)
                cnt = cnt + 1
        print('Moved %d files.' % cnt)


def create_label_txt(root_img_dir):
    for train_or_validation in os.listdir(root_img_dir):
        if train_or_validation == 'train' or \
                train_or_validation == 'validation':
            train_or_validation_name = train_or_validation
            if train_or_validation_name == 'train':
                train_txt_file = os.path.join(train_or_validation, 'train.txt')
                if os.path.exists(train_txt_file):
                    os.remove(train_txt_file)
            else:
                validation_txt_file = os.path.join(train_or_validation, 'validation.txt')
                if os.path.exists(validation_txt_file):
                    os.remove(validation_txt_file)
            train_or_validation = os.path.join(root_img_dir, train_or_validation)
            for screen_dir in os.listdir(train_or_validation):
                screen_name = screen_dir
                screen_dir = os.path.join(train_or_validation, screen_dir)
                if not os.path.isdir(screen_dir):
                    continue
                if screen_name.startswith('idr0008'):
                    label = 0
                elif screen_name.startswith('idr0009'):
                    label = 1
                elif screen_name.startswith('idr0010'):
                    label = 2
                elif screen_name.startswith('idr0013'):
                    label = 3
                elif screen_name.startswith('idr0035'):
                    label = 4
                else:
                    continue
                # print('screen_dir:', screen_dir)
                if train_or_validation_name == 'train':
                    train_txt_file = os.path.join(train_or_validation, 'train.txt')
                    train_txt_file = open(train_txt_file, 'a')
                    for image in os.listdir(screen_dir):
                        print('train: ' + screen_name + '/' + image + ' ' + str(label))
                        train_txt_file.write(screen_name + '/' + image + ' ' + str(label) + '\n')
                    train_txt_file.close()
                else:
                    validation_txt_file = os.path.join(train_or_validation, 'validation.txt')
                    validation_txt_file = open(validation_txt_file, 'a')
                    for image in os.listdir(screen_dir):
                        print('validation: ' + screen_name + '/' + image + ' ' + str(label))
                        validation_txt_file.write(screen_name + '/' + image + ' ' + str(label) + '\n')
                    validation_txt_file.close()


if __name__ == '__main__':
    root_img_dir = r'data\images'
    '''# 移动各子plate文件夹到母screen文件夹
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
                random_move_file(plate_dir, screen_dir, 1)'''

    '''# 分出train(66%)数据集和validation(34%)数据集
    for i in os.listdir(root_img_dir):
        if i.startswith('test'):
            continue
        screen_dir = os.path.join(root_img_dir, i)
        if os.path.isfile(screen_dir):
            continue
        train_dir = os.path.join(screen_dir, 'train')
        if not os.path.exists(train_dir):
            os.makedirs(train_dir)
        random_move_file(screen_dir, train_dir, 0.66)
        validation_dir = os.path.join(screen_dir, 'validation')
        if not os.path.exists(validation_dir):
            os.makedirs(validation_dir)
        random_move_file(screen_dir, validation_dir, 1)'''

    '''# 将图片尺寸统一成299*299
    for i in os.listdir(root_img_dir):
        if i.startswith('test'):
            continue
        screen_dir = os.path.join(root_img_dir, i)
        if os.path.isfile(screen_dir):
            continue
        train_dir = os.path.join(screen_dir, 'train')
        if not os.path.exists(train_dir):
            print('Where is the fucking train_dir of screen ' + screen_dir + '?')
        validation_dir = os.path.join(screen_dir, 'validation')
        if not os.path.exists(validation_dir):
            print('Where is the fucking validation_dir of screen ' + screen_dir + '?')
        for image in os.listdir(train_dir):
            output_dir = os.path.join(train_dir, 'train_299')
            image = os.path.join(train_dir, image)
            if not os.path.isfile(image):
                print(image, 'is not a valid file, skip')
                continue
            crop_to_299(image, output_dir)

        for image in os.listdir(validation_dir):
            output_dir = os.path.join(validation_dir, 'validation_299')
            image = os.path.join(validation_dir, image)
            if not os.path.isfile(image):
                print(image, 'is not a valid file, skip')
                continue
            crop_to_299(image, output_dir)'''

    # 创建标签文件
    create_label_txt(root_img_dir)
