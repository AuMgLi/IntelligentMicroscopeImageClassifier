from requests_html import HTMLSession
import re
import os
import requests
import threading
import queue

q = queue.Queue()


class IdrImagesCrawler:

    def __init__(self, image_dir, plate, field=0):
        self.__session = HTMLSession()
        self.__image_dir = image_dir
        self.__plate = plate
        self.__field = field

    def get_image_dir_to_download(self):
        return self.__image_dir

    def create_image_dir_for_download(self):
        if len(self.__image_dir) > 1 and self.__image_dir[-1] == '/':
            self.__image_dir = self.__image_dir[:-1]
        if not os.path.exists(self.__image_dir):
            os.makedirs(self.__image_dir)

    def __get_plate_and_field(self, plate, field=0):
        callback_url = 'https://idr.openmicroscopy.org/webgateway/plate/' + str(plate) + '/' + str(field)
        response = self.__session.get(callback_url)
        # print('response length:', len(str(response.content)))
        return response

    def fetch_image_id(self):
        pattern = re.compile(r'"id": \d+')
        response = self.__get_plate_and_field(self.__plate, self.__field)
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


class MultiThreadDownloader(threading.Thread):

    def __init__(self, thread_id, url_list, start_pos, end_pos, idr_crawler):
        super().__init__()
        self.thread_id = thread_id
        self.url_list = url_list
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.__idr_crawler = idr_crawler

    def download_image_set(self, url_list, file_suffix='.jpg'):
        dir_path = self.__idr_crawler.get_image_dir_to_download()
        # num_of_url = len(url_list)
        post = 0
        for url_pos in range(self.start_pos, self.end_pos):
            url = url_list[url_pos]
            post = post + 1
            file_name = url.split('/')[-2] + file_suffix
            file_path = os.path.join(dir_path, file_name)
            if os.path.exists(file_path):
                q.put('1' + file_path)
            else:
                try:
                    requests_get = requests.get(url)
                    with open(file_path, 'wb') as data:
                        data.write(requests_get.content)
                    # print('Thread ' + str(self.thread_id) + ' has downloaded ' +
                    #       file_path + ' [' + str(post) + ' of ' + str(num_of_url) + ']')
                    q.put('0' + file_path)
                except Exception:
                    print('-------------- Error: thread %d timeout! ------------------' % self.thread_id)

    def run(self):
        # image_dir = r'.\data\images' + '\\plate' + str(self.plate)
        # res = self.idr_crawler.get_plate_and_field(self.plate, self.field)
        # download_url_list = self.
        self.download_image_set(self.url_list)


class DownloaderMonitor(threading.Thread):

    def __init__(self, num_of_urls):
        super().__init__()
        self.num_of_urls = num_of_urls

    def run(self):
        cnt = 0
        while cnt < self.num_of_urls:
            cnt = cnt + 1
            try:
                msg = q.get(timeout=5)
                if msg[0] == '0':
                    msg = msg[1:]
                    print(msg + ' has been successfully downloaded. [' +
                          str(cnt) + ' of ' + str(self.num_of_urls) + ']')
                elif msg[0] == '1':
                    msg = msg[1:]
                    print(msg + ' have already exist, skip. [' +
                          str(cnt) + ' of ' + str(self.num_of_urls) + ']')
            except queue.Empty:
                pass
        print('Done.')


def download(m_plate, m_field=0, m_num_of_threads=16):
    m_image_dir = r'.\data\images' + '\\plate' + str(m_plate)
    m_idr_crawler = IdrImagesCrawler(m_image_dir, m_plate, m_field)
    m_idr_crawler.create_image_dir_for_download()
    m_url_list = m_idr_crawler.fetch_image_id()
    m_num_of_urls = len(m_url_list)
    m_num_of_urls_per_thread = m_num_of_urls // m_num_of_threads
    # m_num_of_urls_last_thread = m_num_of_urls - m_num_of_urls_per_thread * (m_num_of_threads - 1)
    downloader_monitor = DownloaderMonitor(m_num_of_urls)
    downloader_monitor.start()
    for i in range(m_num_of_threads):
        m_start_pos = i * m_num_of_urls_per_thread
        if i < m_num_of_threads - 1:
            m_end_pos = m_start_pos + m_num_of_urls_per_thread
        else:
            m_end_pos = m_num_of_urls
        t = MultiThreadDownloader(i, m_url_list, m_start_pos, m_end_pos, m_idr_crawler)
        t.start()


if __name__ == '__main__':
    for i in range(4):
        download(6305, i, 24)
