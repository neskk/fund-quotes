from datetime import datetime, timedelta
import logging
import re

from bs4 import BeautifulSoup

from models import Fund, Quote
from db import Database
from scrapper import Scrapper


log = logging.getLogger(__name__)


class CGD(Scrapper):
    URL = ('https://www.cgd.pt/Particulares/Poupanca-Investimento/Fundos-de-Investimento/Pages/CotacoeseRendibilidades.aspx')
    BANK = 'CGD'

    # Grab ID from here
    # https://pt.investing.com/funds/ptcxghhm0011-chart
    # <div id="tvc_container_96b53f9fc64a32e7094b5aecdb8cd085" class="tvChartContainer" width="650" height="750">
    #js_instrument_chart_last_update

    #https://tvc4.investing.com/6b6dcf65c5c41f4e669602ab931fe39e/1707969368/50/50/15/history?symbol=1170004&resolution=D&from=1676865370&to=1707969430

    def __init__(self):
        Scrapper.__init__(self, name=self.BANK)
        self.db = Database.get_db()

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

            date = datetime.strptime(match.group(), '%d-%m-%Y').date()
            # max_age = datetime.utcnow() - timedelta(hours=self.args.scrapper_frequency)

            quote = info.find('div', class_="cotacaoDia").get_text()
            match = re.search(r'([\d\,]+) €', quote)
            if not match:
                log.error(f'Unable to find a valid quote for: {date}')
                continue

            quote = float(match.group(1).replace(',', '.'))

            self.update_db(fund, date, quote)

            # prev_quote = info.find('div', class_="cotacaoDiaAnterior").get_text()
            # match = re.search(r'([\d\,]+) €', prev_quote)
            # if match:
            #     prev_quote = float(match.group(1).replace(',', '.'))

    def update_db(self, fund, date, value):
        quote = Quote.get_or_none(
            Quote.fund == fund,
            Quote.date == date,
        )

        if quote and quote.value == value:
            log.debug(f'Quote for {fund.name} on {date} already exists.')
            return

        if not quote:
            quote = Quote.create(fund=fund, date=date, value=value)
            log.debug(f'Quote for {fund.name} on {date}: {quote.value}')
            return

        quote.value = value
        quote.modified = datetime.utcnow()
        quote.save()
        log.debug(f'Updated quote for {fund.name} on {date}: {quote.value}')
