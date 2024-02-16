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
    # https://www.bancoinvest.pt/poupanca-e-investimento/investimento/fundos-de-investimento/detalhe-fundo-de-investimento?isin=PTARMCLM0004
    BANK = 'AR'
    FUND_NAME = 'Alves Ribeiro PPR/OICVM'
    ISIN = 'PTARMCLM0004'

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
        fund, is_new = Fund.get_or_create(bank=self.BANK, name=self.FUND_NAME)
        latest_quote = Quote.get_latest(fund)

        pattern = r'n(\d{2}-\d{2}-\d{4};[\d\,]+);'
        data = re.findall(pattern, content)
        for entry in data:
            date, quote = entry.split(';')

            date = datetime.strptime(date, '%d-%m-%Y').date()
            quote = float(quote.replace(',', '.'))

            if latest_quote and latest_quote.date >= date:
                continue

            self.update_db(fund, date, quote)

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
