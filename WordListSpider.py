'''Spider that generates word lists'''
from urllib.parse import urljoin, urlparse
import argparse
import mimetypes

from RobotParser import RobotParser
import requests
import bs4
mimetypes.init()


class WordListSpider(object):
    def __init__(self, url, useragent='WordListSpider'):
        self.host = urlparse(url).netloc
        self.tocrawl = {url}
        self.crawled = set()
        self.robotparser = RobotParser(useragent=useragent)
        self.session = requests.Session()
        self.session.headers['User-Agent'] = useragent
        self.wordlist = set()

    def next(self):
        url = list(self.tocrawl)[0]
        self.tocrawl.remove(url)
        self.crawled.add(url)
        print(url, len(self.tocrawl), len(self.crawled))
        try:
            r = self.session.get(url)
            soup = bs4.BeautifulSoup(r.text)
            links = {tag.attrs['href'] for tag in soup.select('a[href]')}
            links = {urljoin(r.url, l) for l in links}
            links = {l for l in links if urlparse(l).netloc == self.host}
            links = {l for l in links if mimetypes.guess_type(l)[0] in (
                'text/html', None, 'application/xhtml+xml')}
            links = {l for l in links if self.robotparser.can_fetch(l)}
            links.difference_update(self.crawled)
            self.tocrawl.update(links)
            [tag.replaceWith('') for tag in soup.find_all('script')]
            [tag.replaceWith('') for tag in soup.find_all('style')]
            text = soup.get_text().lower().split()
            text = set(i for i in text if i)
            self.wordlist.update(text)
        except Exception as error:
            print(error, error.with_traceback(None))

    def run(self):
        try:
            while True:
                self.next()
        except IndexError:
            pass


def main():
    '''Parse commandline arguments and run program'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url',
                        help='Url to start crawl, is required',
                        required=True)
    parser.add_argument('-o', '--output',
                        help='Output file, defaults to out.txt',
                        default='out.txt')
    args = parser.parse_args()
    wls = WordListSpider(args.url)
    wls.run()
    wordlist = '\n'.join(wls.wordlist)
    for char in set(wordlist):
        if char not in 'abcdefghijklmnopqrstuvwxyz\n':
            wordlist = wordlist.replace(char, '')
    with open(args.output, 'w') as file:
        file.write(wordlist)
if __name__ == '__main__':
    main()
