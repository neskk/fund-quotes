#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import requests
from timeit import default_timer as timer
from threading import Thread

from abc import ABC, abstractmethod
from urllib3.util.retry import Retry
from urllib3.exceptions import MaxRetryError
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError

from config import Config
from user_agent import UserAgent
from utils import export_file, http_headers

log = logging.getLogger(__name__)


class Scrapper(ABC, Thread):

    STATUS_FORCELIST = [413, 429, 500, 502, 503, 504]

    def __init__(self, name):
        ABC.__init__(self)
        Thread.__init__(self, name=name, daemon=False)
        args = Config.get_args()
        self.args = args

        self.debug = args.verbose
        self.download_path = args.download_path
        self.timeout = args.scrapper_timeout
        self.proxy_url = args.scrapper_proxy

        self.name = name
        self.user_agent = UserAgent.generate(args.user_agent)
        self.session = None
        self.retries = Retry(
            allowed_methods=None,  # retry on all HTTP verbs
            total=args.scrapper_retries,
            backoff_factor=args.scrapper_backoff_factor,
            status_forcelist=self.STATUS_FORCELIST)

        self.setup_session()
        log.info('Initialized scrapper: %s.', name)

    def setup_session(self):
        self.session = requests.Session()
        # Mount handler on both HTTP & HTTPS
        adapter = HTTPAdapter(max_retries=self.retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def setup_proxy(self, no_proxy=False):
        proxy_url = None
        if not no_proxy and self.proxy_url:
            proxy_url = self.proxy_url

        self.session.proxies = {'http': proxy_url, 'https': proxy_url}

    def make_request(self, url, referer=None, post={}, json=False):
        headers = http_headers()
        headers['User-Agent'] = self.user_agent
        headers['Referer'] = referer or 'https://www.google.com'

        if post:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            response = self.session.post(
                url,
                timeout=self.timeout,
                headers=headers,
                data=post)
        else:
            response = self.session.get(
                url,
                timeout=self.timeout,
                headers=headers,
                verify=False)

        response.raise_for_status()

        if json:
            content = response.json()
        else:
            content = response.text

        response.close()
        return content

    def request_url(self, url, referer=None, post={}, json=False):
        error_count = 0
        no_proxy = False
        while True:
            if error_count > 4:
                log.error('Failed to scrap webpage.')
                break
            start_t = timer()
            try:
                if error_count == 4:
                    log.debug('Not using proxy for next request.')
                    no_proxy = True
                    continue
                self.setup_proxy(no_proxy)
                content = self.make_request(url, referer, post, json)
                if not content:
                    error_count += 1
                    continue

                return content
            except MaxRetryError as e:
                log.error(f'MaxRetryError: {e.reason}')
            except ConnectionError as e:
                log.error(f'Connection error: {e}')
            except HTTPError as e:
                log.error(f'HTTP error: {e}')
            except Exception as e:
                log.exception('Failed to request URL "%s": %s', url, e)

            log.debug(f'Request took: {timer()-start_t}')
            error_count += 1

        return None

    def download_file(self, url, filename, referer=None, use_proxy=False):
        result = False
        try:
            # Setup request headers
            headers = http_headers(keep_alive=True)
            headers['User-Agent'] = self.user_agent
            headers['Referer'] = referer or 'https://www.google.com'

            if use_proxy:
                self.setup_proxy()

            response = self.session.get(
                url,
                # proxies={'http': self.proxy, 'https': self.proxy},
                timeout=self.timeout,
                headers=headers)

            response.raise_for_status()

            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=128):
                    fd.write(chunk)
                result = True

            response.close()
        except Exception as e:
            log.exception('Failed to download file "%s": %s.', url, e)

        return result

    def export_webpage(self, soup, filename):
        content = soup.prettify()  # .encode('utf8')
        filename = '{}/{}'.format(self.download_path, filename)

        export_file(filename, content)
        log.debug('Web page output saved to: %s', filename)

    def run(self):
        try:
            log.debug(f'{self.name} scrapper started.')
            self.scrap()
            log.debug(f'{self.name} scrapper stopped.')

        except Exception as e:
            log.exception(f'{self.name} scrapper failed: {e}')

    @abstractmethod
    def scrap(self):
        """
        Scrap and store relevant web content.
        """
        pass
