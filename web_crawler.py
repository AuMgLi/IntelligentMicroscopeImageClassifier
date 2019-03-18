from requests_html import HTMLSession
import re
import os
import requests
import sys

session = HTMLSession()


def get_plate_and_field(plate, field=0):
    callback_url = 'https://idr.openmicroscopy.org/webgateway/plate/' + str(plate) + '/' + str(field)
    response = session.get(callback_url)
    # print('response length:', len(str(response.content)))

    return response


def fetch_image_id(response):
    pattern = re.compile(r'"id": \d+')
    image_id_list = pattern.findall(str(response.content))
    print('length of image_id_group:', len(image_id_list))
    print(image_id_list)
    download_image_url_prefix = 'https://idr.openmicroscopy.org/webclient/render_image_download/'
    pattern_id = re.compile(r'\d+')
    download_url_list = []
    for _id in image_id_list:
        _id = pattern_id.search(_id).group(0)
        # print(_id)
        download_image_url = download_image_url_prefix + _id + '/'
        # print(download_image_url)
        download_url_list.append(download_image_url)

    return download_url_list


def download_image_set(url_list, dir_path, file_suffix='.jpg'):
    if len(dir_path) > 1 and dir_path[-1] == '/':
        dir_path = dir_path[:-1]
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    num_of_url = len(url_list)
    post = 0
    for url in url_list:
        post = post + 1
        file_name = url.split('/')[-2] + file_suffix
        file_path = os.path.join(dir_path, file_name)
        if os.path.exists(file_path):
            print(file_path + ' have already exist, skip.')
        else:
            requests_get = requests.get(url)
            with open(file_path, 'wb') as data:
                data.write(requests_get.content)
            print('Downloaded ' + file_path +
                  ' [' + str(post) + ' of ' + str(num_of_url) + ']')


def main(plate, field):
    image_dir = r'.\data\images' + '\\plate' + str(plate)
    res = get_plate_and_field(plate, field)
    download_url_list = fetch_image_id(res)
    download_image_set(download_url_list, image_dir)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
    # res = get_plate_and_field(3887, 0)
    # download_url_list = fetch_image_id(res)
