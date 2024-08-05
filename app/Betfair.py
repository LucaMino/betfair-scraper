import time
import helper
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class Betfair:
    # constructor
    def __init__(self):
        # init webdriver
        self.init_webdriver()

    # main
    def get_markets(self):
        try:
            # define response
            response = {}
            # loop changing market type on url
            for index, market in enumerate(helper.config('bookmakers.betfair.links.market_type_codes')):
                # navigate to route
                route = helper.config('bookmakers.betfair.links.daily_soccer_events') + '?marketType=' + market
                helper.route(self.driver, route)
                # reject cookie in headless mode
                if not helper.config('bookmakers.betfair.headless'):
                    time.sleep(1)
                    # reject cookie popup
                    if index == 0:
                        self.reject_cookie()
                        time.sleep(1)
                # get matches
                html = self.get_matches_html()
                sections = self.get_sections(html)
                response = self.get_matches(sections, response, market)

            # quit
            self.driver.quit()

            return response

        except TimeoutException:
            helper.print_c('TimeoutException', 'red')

        except NoSuchElementException:
            helper.print_c('NoSuchElementException', 'red')

        except Exception as e:
            helper.print_c(f"Exception error: {e}", 'red')

        while True:
            pass

    # init webdriver
    def init_webdriver(self):
        # initialise webdriver options
        chrome_options = Options()

        if helper.config('selenium.headless'):
            # set headless mode
            chrome_options.add_argument('--headless=new')
        else:
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            # set window size
            chrome_options.add_argument(helper.config('selenium.window_size'))

        # create instance of chrome driver with chrome_options
        self.driver = webdriver.Chrome(options=chrome_options)
        # set driver wait (after x second raise TimeoutException)
        self.wait = WebDriverWait(self.driver, helper.config('selenium.web_driver_wait'))

    # reject cookies popup
    def reject_cookie(self):
        # wait element loaded
        helper.visibility_of_element_located(self.wait, 'ID', 'onetrust-button-group')
        time.sleep(1)
        # click after element be clickable
        helper.element_to_be_clickable(self.wait, 'ID', 'onetrust-reject-all-handler', True)

    # move to helper
    def get_matches_html(self):
        ul_element = helper.find_element(self.driver, 'CLASS_NAME', 'section-list')

        # Extract the HTML of the ul element
        ul_html = ul_element.get_attribute('innerHTML')

        return ul_html

    # returns the differnt sections
    def get_sections(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        list_items = soup.findAll('li', class_='section')

        items = []
        # Extract the text content of each <li> tag
        for item in list_items:
            item_type = item.find('span', class_='section-header-title')
            if item_type and item_type.string:
                item_name = item_type.string
                items.append({
                    'name': helper.normalize_string(item_name),
                    'element': item
                })
        return items

    # get matches
    def get_matches(self, sections, allMarket, market):
        # response = {}
        for section in sections:
            if section.get('name') == helper.config('bookmakers.betfair.lang.it.today'):
                matches = section.get('element').findAll('li', class_='com-coupon-line-new-layout')
                helper.print_c('Betfair matches found ' + 'for ' + market + ': ' + str(len(matches)))
                for index, match in enumerate(matches):
                    # get link tag
                    event_link = match.find('a', class_='event-link')
                    # get team names
                    team_name_spans = match.find_all('span', class_='team-name')
                    team_names = [span.get_text(strip=True) for span in team_name_spans]
                    # get html
                    quotes_html = match.find('div', class_='market-3-runners')
                    # get default (1X2) quotes
                    defaultMarketQuotes = self.get_runners(quotes_html, '1X2')
                    # skip
                    if not defaultMarketQuotes:
                        continue
                    # join teams from array and create key of the match (s1 - s2)
                    match_key = ' - '.join(team_names)
                    # print(match_key)
                    if match_key not in allMarket:
                        # create new event
                        allMarket[match_key] = {
                            'url': helper.config('bookmakers.betfair.links.base_event_url') + event_link.get('href'),
                            'markets': {}
                        }
                    # push 1X2 market if not present
                    if '1X2' not in allMarket[match_key]['markets']:
                        allMarket[match_key]['markets']['1X2'] = defaultMarketQuotes
                    # get second quotes
                    second_quotes_html = match.find('div', class_='market-2-runners')
                    # get current market (from param) quotes
                    currentMarketQuotes = self.get_runners(second_quotes_html, market)

                    if market not in allMarket[match_key]['markets']:
                        allMarket[match_key]['markets'][market] = currentMarketQuotes

                    if index == helper.config('bookmakers.betfair.limit'):
                        break

        return allMarket

    def get_runners(self, html, market):
        marketRunners = html.find_all('a', class_='ui-market-action')
        quotes = [a.text.strip() for a in marketRunners]

        # skip if match is suspended
        if helper.config('bookmakers.betfair.lang.it.suspended') in quotes or not quotes:
            return False

        match market:
            case '1X2':
                if len(quotes) != 3:
                    return False
                # set runners
                runners = [
                    {
                        'book': 'BETFAIR',
                        'market': '1',
                        'quote': quotes[0]
                    },
                    {
                        'book': 'BETFAIR',
                        'market': 'X',
                        'quote': quotes[1]
                    },
                        {
                        'book': 'BETFAIR',
                        'market': '2',
                        'quote': quotes[2]
                    }
                ]
            case 'BOTH_TEAMS_TO_SCORE':
                if len(quotes) != 2:
                    return False
                runners = [
                    {
                        'book': 'BETFAIR',
                        'market': 'YES',
                        'quote': quotes[0]
                    },
                    {
                        'book': 'BETFAIR',
                        'market': 'NO',
                        'quote': quotes[1]
                    }
                ]
            case 'DOUBLE_CHANCE':
                if len(quotes) != 3:
                    return False
                runners = [
                    {
                        'book': 'BETFAIR',
                        'market': '1X',
                        'quote': quotes[0]
                    },
                    {
                        'book': 'BETFAIR',
                        'market': 'X2',
                        'quote': quotes[1]
                    },
                    {
                        'book': 'BETFAIR',
                        'market': '12',
                        'quote': quotes[2]
                    }
                ]
            case 'DRAW_NO_BET':
                if len(quotes) != 2:
                    return False
                runners = [
                    {
                        'book': 'BETFAIR',
                        'market': '1',
                        'quote': quotes[0]
                    },
                    {
                        'book': 'BETFAIR',
                        'market': '2',
                        'quote': quotes[1]
                    }
                ]
            case 'OVER_UNDER_05' | 'OVER_UNDER_15' | 'OVER_UNDER_25' | 'OVER_UNDER_35' | 'OVER_UNDER_45':
                if len(quotes) != 2:
                    return False
                runners = [
                    {
                        'book': 'BETFAIR',
                        'market': 'OVER',
                        'quote': quotes[0]
                    },
                    {
                        'book': 'BETFAIR',
                        'market': 'UNDER',
                        'quote': quotes[1]
                    }
                ]
            case _:
                helper.print_c('Error on betfair market type switch, market: ' + market, 'red')
                return False

        data = {
            'market_type': market,
            'runners': runners
        }

        return data