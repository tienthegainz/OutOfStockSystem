import datetime
import json
import re

from bs4 import BeautifulSoup
from six.moves.urllib.parse import urlencode
from six.moves.urllib.parse import urlparse

from icrawler import Crawler, Feeder, Parser, ImageDownloader
from icrawler.builtin.filter import Filter
from icrawler.builtin import GoogleImageCrawler


class GoogleFeeder(Feeder):

    def get_filter(self):
        search_filter = Filter()

        # type filter
        def format_type(img_type):
            return ('itp:lineart'
                    if img_type == 'linedrawing' else 'itp:' + img_type)

        type_choices = ['photo', 'face', 'clipart', 'linedrawing', 'animated']
        search_filter.add_rule('type', format_type, type_choices)

        # color filter
        def format_color(color):
            if color in ['color', 'blackandwhite', 'transparent']:
                code = {
                    'color': 'color',
                    'blackandwhite': 'gray',
                    'transparent': 'trans'
                }
                return 'ic:' + code[color]
            else:
                return 'ic:specific,isc:{}'.format(color)

        color_choices = [
            'color', 'blackandwhite', 'transparent', 'red', 'orange', 'yellow',
            'green', 'teal', 'blue', 'purple', 'pink', 'white', 'gray',
            'black', 'brown'
        ]
        search_filter.add_rule('color', format_color, color_choices)

        # size filter
        def format_size(size):
            if size in ['large', 'medium', 'icon']:
                size_code = {'large': 'l', 'medium': 'm', 'icon': 'i'}
                return 'isz:' + size_code[size]
            elif size.startswith('>'):
                size_code = {
                    '400x300': 'qsvga',
                    '640x480': 'vga',
                    '800x600': 'svga',
                    '1024x768': 'xga',
                    '2mp': '2mp',
                    '4mp': '4mp',
                    '6mp': '6mp',
                    '8mp': '8mp',
                    '10mp': '10mp',
                    '12mp': '12mp',
                    '15mp': '15mp',
                    '20mp': '20mp',
                    '40mp': '40mp',
                    '70mp': '70mp',
                }
                return 'isz:lt,islt:' + size_code[size[1:]]
            elif size.startswith('='):
                wh = size[1:].split('x')
                assert len(wh) == 2
                return 'isz:ex,iszw:{},iszh:{}'.format(*wh)
            else:
                raise ValueError(
                    'filter option "size" must be one of the following: '
                    'large, medium, icon, >[]x[], =[]x[] ([] is an integer)')

        search_filter.add_rule('size', format_size)

        # licence filter
        license_code = {
            'noncommercial': 'f',
            'commercial': 'fc',
            'noncommercial,modify': 'fm',
            'commercial,modify': 'fmc'
        }

        def format_license(license):
            return 'sur:' + license_code[license]

        license_choices = list(license_code.keys())
        search_filter.add_rule('license', format_license, license_choices)

        # date filter
        def format_date(date):
            if date == 'pastday':
                return 'qdr:d'
            elif date == 'pastweek':
                return 'qdr:w'
            elif isinstance(date, tuple):
                assert len(date) == 2
                date_range = []
                for date_ in date:
                    if date_ is None:
                        date_str = ''
                    elif isinstance(date_, (tuple, datetime.date)):
                        date_ = datetime.date(*date_) if isinstance(
                            date_, tuple) else date_
                        date_str = date_.strftime('%m/%d/%Y')
                    else:
                        raise TypeError(
                            'date must be a tuple or datetime.date object')
                    date_range.append(date_str)
                return 'cdr:1,cd_min:{},cd_max:{}'.format(*date_range)
            else:
                raise TypeError(
                    'filter option "date" must be "pastday", "pastweek" or '
                    'a tuple of dates')

        search_filter.add_rule('date', format_date)

        return search_filter

    def feed(self, keyword, offset, max_num, language=None, filters=None):
        base_url = 'https://www.google.com/search?'
        self.filter = self.get_filter()
        filter_str = self.filter.apply(filters, sep=',')
        for i in range(offset, offset + max_num, 100):
            params = dict(
                q=keyword,
                ijn=int(i / 100),
                start=i,
                tbs=filter_str,
                tbm='isch')
            if language:
                params['lr'] = 'lang_' + language
            url = base_url + urlencode(params)
            self.out_queue.put(url)
            self.logger.debug('put url to url_queue: {}'.format(url))


class GoogleParser(Parser):
    def parse(self, response):
        soup = BeautifulSoup(
            response.content.decode('utf-8', 'ignore'), 'lxml')
        #image_divs = soup.find_all('script')
        image_divs = soup.find_all(name='script')
        for div in image_divs:
            #txt = div.text
            txt = str(div)
            # if not txt.startswith('AF_initDataCallback'):
            if 'AF_initDataCallback' not in txt:
                continue
            if 'ds:0' in txt or 'ds:1' not in txt:
                continue
            # txt = re.sub(r"^AF_initDataCallback\({.*key: 'ds:(\d)'.+data:function\(\){return (.+)}}\);?$",
            #             "\\2", txt, 0, re.DOTALL)
            #meta = json.loads(txt)
            #data = meta[31][0][12][2]
            #uris = [img[1][3][0] for img in data if img[0] == 1]

            uris = re.findall(r'http.*?\.(?:jpg|png|bmp)', txt)
            return [{'file_url': uri} for uri in uris]


class GoogleDownloader(ImageDownloader):

    def get_filename(self, task, default_ext):
        url_path = urlparse(task['file_url'])[2]
        if '.' in url_path:
            extension = url_path.split('.')[-1]
            if extension.lower() not in ['jpg', 'jpeg', 'png']:
                extension = default_ext
        else:
            extension = default_ext
        file_idx = self.fetched_num + self.file_idx_offset
        return '{}_{:06d}.{}'.format("_".join(self.keyword.split()), file_idx, extension)

    def start(self, keyword, file_idx_offset=0, *args, **kwargs):
        self.clear_status()
        self.set_file_idx_offset(file_idx_offset)
        self.keyword = keyword
        self.init_workers(*args, **kwargs)
        for worker in self.workers:
            worker.start()
            self.logger.debug('thread %s started', worker.name)


class MyGoogleImageCrawler(Crawler):

    def __init__(self,
                 feeder_cls=GoogleFeeder,
                 parser_cls=GoogleParser,
                 downloader_cls=GoogleDownloader,
                 *args,
                 **kwargs):
        super(MyGoogleImageCrawler, self).__init__(
            feeder_cls, parser_cls, downloader_cls, *args, **kwargs)

    def crawl(self,
              keyword,
              filters=None,
              offset=0,
              max_num=1000,
              min_size=None,
              max_size=None,
              language=None,
              file_idx_offset=0,
              overwrite=False):
        if offset + max_num > 1000:
            if offset > 1000:
                self.logger.error(
                    '"Offset" cannot exceed 1000, otherwise you will get '
                    'duplicated searching results.')
                return
            elif max_num > 1000:
                max_num = 1000 - offset
                self.logger.warning(
                    'Due to Google\'s limitation, you can only get the first '
                    '1000 result. "max_num" has been automatically set to %d. '
                    'If you really want to get more than 1000 results, you '
                    'can specify different date ranges.', 1000 - offset)

        feeder_kwargs = dict(
            keyword=keyword,
            offset=offset,
            max_num=max_num,
            language=language,
            filters=filters)
        downloader_kwargs = dict(
            keyword=keyword,
            max_num=max_num,
            min_size=min_size,
            max_size=max_size,
            file_idx_offset=file_idx_offset,
            overwrite=overwrite)
        super(MyGoogleImageCrawler, self).crawl(
            feeder_kwargs=feeder_kwargs, downloader_kwargs=downloader_kwargs)


if __name__ == "__main__":
    crawler = MyGoogleImageCrawler(feeder_threads=1,
                                   parser_threads=1,
                                   downloader_threads=4,
                                   storage={'root_dir': '/home/tienhv/GR/OutOfStockSystem/images/object_detection'})

    products = {"chanel perfume": 200,
                "yves saint laurent perfume": 200, "lancome perfume": 200}

    for k, v in products.items():
        crawler.crawl(keyword=k, max_num=v)
