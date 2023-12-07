from datetime import datetime, timedelta
import logging
import re

from bs4 import BeautifulSoup

from models import Fund, Quote
from db import Database
from scrapper import Scrapper


log = logging.getLogger(__name__)


class AR(Scrapper):
    URL = ('https://www.bancoinvest.pt/poupanca-e-investimento/investimento/grafico?isin=PTARMCLM0004')
    BANK = 'AR'

    def __init__(self):
        Scrapper.__init__(self, name=self.BANK)
        self.db = Database()

    def scrap(self):
        content = self.make_request(self.URL)

        try:
            Fund.database().connect()
            self.parse(content)
        finally:
            Fund.database().close()

    def parse(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        details = soup.find_all('div', 'detalhesFundo')

        for info in details:
            name = info.find('a', class_='nomeFundo').get_text()

            fund, is_new = Fund.get_or_create(bank=self.BANK, name=name)

            date = info.find('div', class_='cotacaoDiaLbl').get_text()
            match = re.search(r'\d{2}\-\d{2}\-\d{4}', date)
            if not match:
                log.error(f'Unable to find a valid date in: {date}')
                continue

            date = datetime.strptime(match.group(), '%d-%m-%Y')
            max_age = datetime.utcnow() - timedelta(hours=self.args.scrapper_frequency)

            recent_quotes = Quote.select().where(
                Quote.fund == fund,
                Quote.created > max_age
            ).count()

            if recent_quotes > 0:
                log.debug(f'Quote for {name} on {date} already exists.')
                continue
            if date < datetime.utcnow() - timedelta(days=2):
                log.debug(f'Quote for {name} on {date} is too old.')
                continue

            quote = info.find('div', class_="cotacaoDia").get_text()
            match = re.search(r'([\d\,]+) €', quote)
            if match:
                quote = float(match.group(1).replace(',', '.'))

            new_quote = Quote.create(fund=fund, value=quote)
            log.debug(f'Quote for {name} on {date}: {new_quote.value}')

            prev_quote = info.find('div', class_="cotacaoDiaAnterior").get_text()
            match = re.search(r'([\d\,]+) €', prev_quote)
            if match:
                prev_quote = float(match.group(1).replace(',', '.'))
