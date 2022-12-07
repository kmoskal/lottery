from bs4 import BeautifulSoup
import argparse
import requests
import urllib3
from datetime import date, datetime

urllib3.disable_warnings()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
    "Accept-Language": "pl-PL",
    "Referer": "https://google.pl",
    "DNT": "1"
}

GAME_LIST = ['lotto', 'eurojackpot', 'multi-multi']
DATE_FORMAT = '%Y-%m-%d' # YYYY-MM-DD

parser = argparse.ArgumentParser(description="Sprawdź wyniki lotto w terminalu")
parser.add_argument("-game", default="lotto", choices=GAME_LIST, 
                    help=f"Podaj nazwę gry w której chcesz sprawdzić wyniki np. {GAME_LIST}.")
parser.add_argument("-count", default=1, type=int, help="Podaj ilość wcześniejszych losowań.")
parser.add_argument("-date", default=str(date.today()), type=str)
args = parser.parse_args()


class Lottery:
    def __init__(self, lottery_name: str, count: int = 1, request_date: str = None):
        self.lottery_name = lottery_name
        self.count = count
        self.request_date = self.date_validator(request_date)
        self.url = f'https://lotto.pl/{lottery_name}/wyniki-i-wygrane/' + ( f'date,{self.request_date},{count}' if date else '')
        self.game_main_boxes = self.collect_data(self.url)
        self.results: dict = {}


    def collect_data(self, url):
        try:
            html = requests.get(url, headers=HEADERS, verify=False).text
            soup = BeautifulSoup(html, 'lxml')
            game_main_boxes = soup.find_all(class_="game-main-box")
            return game_main_boxes
        except requests.exceptions.RequestException:
            raise SystemExit('Wystąpił nieoczekiwany błąd, spróbuj później')

    def date_validator(self, request_date) -> str:
        try:
            validate_date = datetime.strptime(request_date, DATE_FORMAT).strftime(DATE_FORMAT)
            return validate_date
        except ValueError:
            validate_date = str(date.today())
            print('Data musi być w formacie YYYY-MM-DD np. "2000-01-01"')
            print(f'Datę ustawiono na dzisiejszą tj. {date.today()}')
            return validate_date

    def print_results(self):
        for key, value in self.results.items():
            print(key)
            for k, v in value.items():
                print(f'{k:15} {" ".join(v)}')
            print()


class Lotto(Lottery):
    def __init__(self, lottery_name: str, count: int = 1, request_date: str = None):
        super().__init__(lottery_name, count, request_date)

    def print_results(self):
        for game in self.game_main_boxes:
            game_date = game.find(class_="sg__desc-title").text.strip()
            
            lotto = game.find(class_="Lotto")
            lotto_numbers = lotto.find_all(class_="scoreline-item circle")
            lotto_numbers = [ number.decode_contents().strip() for number in lotto_numbers ]
            
            lotto_plus = game.find(class_="LottoPlus")
            lotto_plus_numbers = lotto_plus.find_all(class_="scoreline-item circle")
            lotto_plus_numbers = [ number.decode_contents().strip() for number in lotto_plus_numbers ]
            
            self.results[game_date] =  dict([('Lotto', lotto_numbers), ('Lotto Plus', lotto_plus_numbers)])
            
        super().print_results()


class  EuroJackpot(Lottery):
    def __init__(self, lottery_name: str, count: int = 1, request_date: str = None):
        super().__init__(lottery_name, count, request_date)

    def print_results(self):
        for game in self.game_main_boxes:
            game_date = game.find(class_="sg__desc-title").text.strip()
            euro = game.find(class_="EuroJackpot")
            five_numbers = euro.find_all(class_="scoreline-item circle eurojackpot-order")
            five_numbers = [ number.decode_contents().strip() for number in five_numbers ]
            two_numbers = euro.find_all(class_="scoreline-item circle special-eurojackpot")
            two_numbers = [ number.decode_contents().strip() for number in two_numbers ]

            self.results[game_date] = dict([('EuroJackpot 5', five_numbers ), ('EuroJackpot 2', two_numbers)])
            
        super().print_results()


class MultiMulti(Lottery):
    def __init__(self, lottery_name: str, count: int = 1, request_date: str = None):
        super().__init__(lottery_name, count, request_date)

    def print_results(self):
        for game in self.game_main_boxes:
            game_date = game.find(class_="sg__desc-title").text.strip()
            multi = game.find(class_="MultiMulti")
            multi_numbers = multi.find_all(class_="scoreline-item circle")
            multi_numbers = [ number.decode_contents().strip() for number in multi_numbers ]
            plus_number = multi.find(class_="scoreline-item special-multi circle").text.strip()

            self.results[game_date] = dict([('Multi Multi', multi_numbers), ('Plus', plus_number)])
        super().print_results()


if __name__ == "__main__":
    match args.game:
        case "lotto":
            lottery = Lotto(args.game, args.count, args.date)
            lottery.print_results()
        case "eurojackpot":
            lottery = EuroJackpot(args.game, args.count, args.date)
            lottery.print_results()
        case "multi-multi":
            lottery = MultiMulti(args.game, args.count, args.date)
            lottery.print_results()
