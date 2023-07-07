import re
import csv
import time
import concurrent.futures
import urllib.request
from urllib.parse import urlparse, urljoin

class SiteMapper:
    def __init__(self, start_url, max_threads=10, notify_threshold=None, max_depth=None):
        self.start_url = start_url
        self.max_threads = max_threads
        self.visited = set()
        self.site_map = {}
        self.link_timestamps = {}
        self.notify_threshold = notify_threshold
        self.max_depth = max_depth

    def extract_links(self, url):
        try:
            response = urllib.request.urlopen(url)
            html_content = response.read().decode('utf-8')
            links = re.findall(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"', html_content)
            filtered_links = []
            for link in links:
                absolute_url = urljoin(url, link)
                if self.is_same_domain(url, absolute_url):
                    filtered_links.append(absolute_url)
            return filtered_links
        except Exception as e:
            return []

    def is_same_domain(self, parent_url, child_url):
        parent_domain = urlparse(parent_url).netloc
        child_domain = urlparse(child_url).netloc
        return parent_domain == child_domain

    def process_page(self, url, depth=0):
        if url not in self.visited and (self.max_depth is None or depth <= self.max_depth):
            print(f"Processing {url}")
            self.visited.add(url)
            self.site_map[url] = []

            links = self.extract_links(url)
            current_time = time.time()
            self.link_timestamps[url] = current_time

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = [executor.submit(urljoin, url, link) for link in links]
                for future in concurrent.futures.as_completed(futures):
                    child_url = future.result()
                    if child_url and self.is_same_domain(url, child_url) and child_url not in self.visited:
                        self.site_map[url].append(child_url)
                        self.process_page(child_url, depth+1)

            if self.notify_threshold is not None and len(self.visited) >= self.notify_threshold:
                print(f"Threshold reached: {self.notify_threshold} pages visited.")

    def create_site_map(self):
        self.process_page(self.start_url)
        return self.site_map, self.link_timestamps


def save_site_map_to_csv(site_map, output_file, start_time, link_timestamps):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['URL сайта', 'Время обработки (сек)', 'Кол-во найденных ссылок', 'Имя файла с результатом'])
        for url, links in site_map.items():
            link_timestamp = link_timestamps.get(url, start_time)
            processing_time = time.time() - link_timestamp
            num_links = len(links)
            filename = f"{urlparse(url).netloc}_sitemap.txt"
            writer.writerow([url, processing_time, num_links, filename])


if __name__ =='__main__':
    urls = [
        'http://crawler-test.com/',
        'http://google.com/',
        'https://vk.com/',
        'https://dzen.ru/',
        'https://stackoverflow.com/'
    ]

    for url in urls:
        start_time = time.time()
        mapper = SiteMapper(url, max_threads=6, notify_threshold=100, max_depth=2)
        site_map, link_timestamps = mapper.create_site_map()
        output_file = f"{urlparse(url).netloc}_sitemap.csv"
        save_site_map_to_csv(site_map, output_file, start_time, link_timestamps)
        print(f"Site map for {url} saved to {output_file}")
