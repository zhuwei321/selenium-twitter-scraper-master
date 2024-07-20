import asyncio
import os
import queue
import sys
import time
import argparse
import getpass
from datetime import datetime
import threading
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from twitter_scraper import Twitter_Scraper
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from fake_headers import Headers
from doubleFa_scraper import doubleFa_scraper  # Assumed import for your doubleFA scraper
from progress import Progress  # Assumed import for your progress bar

class Tweet:
    def __init__(self, card: webdriver, driver: webdriver, actions: ActionChains, scrape_poster_details=False) -> None:
        self.card = card
        self.driver = driver
        self.error = False
        self.tweet = None
        self.tweet_link = None

        try:
            self.user = card.find_element("xpath", './/div[@data-testid="User-Name"]//span').text
        except NoSuchElementException:
            self.error = True
            self.user = "skip"

        try:
            self.handle = card.find_element("xpath", './/span[contains(text(), "@")]').text
        except NoSuchElementException:
            self.error = True
            self.handle = "skip"

        try:
            self.date_time = card.find_element("xpath", ".//time").get_attribute("datetime")
            if self.date_time is not None:
                self.is_ad = False
        except NoSuchElementException:
            self.is_ad = True
            self.error = True
            self.date_time = "skip"

        if self.error:
            return

        try:
            self.retweet_cnt = card.find_element("xpath", './/button[contains(@aria-label,"Repost")]').get_attribute("aria-label").split(" ")[0]
            if self.retweet_cnt == "":
                self.retweet_cnt = "0"
        except NoSuchElementException:
            self.retweet_cnt = "0"

        try:
            self.reply_cnt = card.find_element("xpath", './/button[contains(@aria-label,"Reply")]').get_attribute("aria-label").split(" ")[0]
            if self.reply_cnt == "":
                self.reply_cnt = "0"
        except NoSuchElementException:
            self.reply_cnt = "0"

        try:
            self.like_cnt = card.find_element("xpath", './/button[contains(@aria-label,"Like")]').get_attribute("aria-label").split(" ")[0]
            if self.like_cnt == "":
                self.like_cnt = "0"
        except NoSuchElementException:
            self.like_cnt = "0"

        try:
            self.analytics_cnt = card.find_element("xpath",'.//div[contains(@aria-label,"views")]').get_attribute("aria-label").split(" ")[-2]
            if self.analytics_cnt == "":
                self.analytics_cnt = "0"
        except NoSuchElementException:
            self.analytics_cnt = "0"

        self.tweet = (
            self.user,
            self.handle,
            self.date_time,
            self.reply_cnt,
            self.retweet_cnt,
            self.like_cnt,
            self.analytics_cnt,
            self.tweet_link
        )

try:
    from dotenv import load_dotenv
    print("Loading .env file")
    load_dotenv()
    print("Loaded .env file\n")
except Exception as e:
    print(f"Error loading .env file: {e}")
    sys.exit(1)

def scrape_tweet(tweet_link, scraper, tweets_data, progress, max_retries):
    retries = 0
    while retries < max_retries:
        try:
            scraper.driver.get(tweet_link)
            scraper.driver.execute_script("window.scrollTo(0, 0);")
            try:
                tip = WebDriverWait(scraper.driver, 3, 1).until(
                   EC.visibility_of_element_located(
                      (By.XPATH, '//div[@data-testid = "error-detail"]//span[@style = "text-overflow: unset; color: rgb(113, 118, 123);"]/span'))
                )
                tweet = (None, None, None, 0, 0, 0, 0, tweet_link)
                tweets_data.append(tweet)
                if len(tweets_data) >= 100:
                    save_to_csv(tweets_data)
                    tweets_data.clear()
                break
            except:
                pass

            try:
                tip = WebDriverWait(scraper.driver, 2, 1).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//a[@href="https://help.twitter.com/rules-and-policies/notices-on-twitter"]'))
                )
                tweet = (None, None, None, 0, 0, 0, 0, tweet_link)
                tweets_data.append(tweet)
                if len(tweets_data) >= 100:
                    save_to_csv(tweets_data)
                    tweets_data.clear()
                break
            except:
                pass

            tweet = Tweet(
                card=WebDriverWait(scraper.driver, 30, 1).until(
                EC.visibility_of_element_located((By.XPATH, '//article[@tabindex="-1" and @data-testid="tweet" and not(@disabled)]'))
                    ),
                driver=scraper.driver,
                actions=ActionChains(scraper.driver),
                scrape_poster_details=scraper.scraper_details["poster_details"],
            )
            tweet.tweet = (tweet.user, tweet.handle, tweet.date_time, tweet.reply_cnt, tweet.retweet_cnt, tweet.like_cnt, tweet.analytics_cnt, tweet_link)

            time.sleep(3)

            tweets_data.append(tweet.tweet)
            progress.print_progress(len(tweets_data), False, 0, False)
            if len(tweets_data) >= 100:
                save_to_csv(tweets_data)
                tweets_data.clear()
            break
        except (NoSuchElementException, TimeoutException):
            retries += 1
            continue
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    else:
        print(f"Failed to scrape {tweet_link} after {max_retries} retries")
        tweet = (None, None, None, None, None, None, None, tweet_link)
        tweets_data.append(tweet)
        if len(tweets_data)>=100:
            save_to_csv(tweets_data)
            tweets_data.clear()

def main():
    try:
        parser = argparse.ArgumentParser(
            add_help=True,
            usage="python scraper [option] ... [arg] ...",
            description="Twitter Scraper is a tool that allows you to scrape tweets from twitter without using Twitter's API.",
        )
        scraper2 = doubleFa_scraper()

        try:
            parser.add_argument(
                "--mail",
                type=str,
                default=os.getenv("TWITTER_MAIL"),
                help="Your Twitter mail.",
            )

            parser.add_argument(
                "--user",
                type=str,
                default=os.getenv("TWITTER_USERNAME"),
                help="Your Twitter username.",
            )

            parser.add_argument(
                "--password",
                type=str,
                default=os.getenv("TWITTER_PASSWORD"),
                help="Your Twitter password.",
            )

            parser.add_argument(
                "--FA",
                type=str,
                default=scraper2.catch(),
                help="Your Twitter 2FA.",
            )
        except Exception as e:
            print(f"Error retrieving environment variables: {e}")
            sys.exit(1)

        parser.add_argument(
            "-t",
            "--tweets",
            type=int,
            default=50000,
            help="Number of tweets to scrape (default: 50)",
        )

        parser.add_argument(
            "-u",
            "--username",
            type=str,
            default=None,
            help="Twitter username. Scrape tweets from a user's profile.",
        )

        parser.add_argument(
            "-ht",
            "--hashtag",
            type=str,
            default=None,
            help="Twitter hashtag. Scrape tweets from a hashtag.",
        )

        parser.add_argument(
            "-ntl",
            "--no_tweets_limit",
            nargs='?',
            default=False,
            help="Set no limit to the number of tweets to scrape (will scrap until no more tweets are available).",
        )

        parser.add_argument(
            "-q",
            "--query",
            type=str,
            default=None,
            help="Twitter query or search. Scrape tweets from a query or search.",
        )

        parser.add_argument(
            "-a",
            "--add",
            type=str,
            default="",
            help="Additional data to scrape and save in the .csv file.",
        )

        parser.add_argument(
            "--latest",
            action="store_true",
            help="Scrape latest tweets",
        )

        parser.add_argument(
            "--top",
            action="store_true",
            help="Scrape top tweets",
        )

        args = parser.parse_args()

        USER_MAIL = args.mail
        USER_UNAME = args.user
        USER_PASSWORD = args.password
        USER_2FA = args.FA

        if USER_UNAME is None:
            USER_UNAME = input("Twitter Username: ")

        if USER_PASSWORD is None:
            USER_PASSWORD = getpass.getpass("Enter Password: ")

        if USER_2FA is None:
            USER_2FA = getpass.getpass("2FA: ")

        print()

        tweet_type_args = []

        if args.username is not None:
            tweet_type_args.append(args.username)
        if args.hashtag is not None:
            tweet_type_args.append(args.hashtag)
        if args.query is not None:
            tweet_type_args.append(args.query)

        additional_data: list = args.add.split(",")

        if len(tweet_type_args) > 1:
            print("Please specify only one of --username, --hashtag, or --query.")
            sys.exit(1)

        if args.latest and args.top:
            print("Please specify either --latest or --top. Not both.")
            sys.exit(1)

        if USER_UNAME is not None and USER_PASSWORD is not None:
            scraper = Twitter_Scraper(
                mail=USER_MAIL,
                username=USER_UNAME,
                password=USER_PASSWORD,
                doubleFA=USER_2FA,
            )
            scraper.login()

            # 读取存储 Twitter ID 的 CSV 文件
            csv_file_path = '/home/ubuntu/twitter/scraper/tweets/2024-07-01_11-39-20_tweets_1-5000_1.csv'
            df = pd.read_csv(csv_file_path)

            # 假设 CSV 文件中有一列名为 'twitter_id'，存储了推文的 ID
            twitter_links = df['Tweet Link'].tolist()

            # 爬取推文数据
            tweets_data = []
            progress = Progress(0, len(twitter_links))
            max_retries = 5  # 设置最大重试次数
            
            i=0
            for tweet_link in twitter_links:
                scrape_tweet(tweet_link, scraper, tweets_data, progress, max_retries)
                i+=1
                if i >=5000:
                    break

            # 最后保存剩余的数据
            if tweets_data:
                save_to_csv(tweets_data)


            print("Scraping Complete")
            sys.exit(0)
        else:
            print("Missing Twitter username or password environment variables. Please check your .env file.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nScript Interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    sys.exit(1)

def save_to_csv(tweets_data, folder_path="/home/ubuntu/tweets/"):
        print("Saving Tweets to CSV...")
        now = datetime.now()

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print("Created Folder: {}".format(folder_path))

        data = {
            "Name": [tweet[0] for tweet in tweets_data],
            "Handle": [tweet[1] for tweet in tweets_data],
            "Timestamp": [tweet[2] for tweet in tweets_data],
            "Comments": [tweet[3] for tweet in tweets_data],
            "Retweets": [tweet[4] for tweet in tweets_data],
            "Likes": [tweet[5] for tweet in tweets_data],
            "Analytics": [tweet[6] for tweet in tweets_data],
            "Tweet Link": [tweet[7] for tweet in tweets_data]
        }
        df = pd.DataFrame(data)

        current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"{folder_path}{current_time}_tweets_1-{len(tweets_data)}_1.csv"
        pd.set_option("display.max_colwidth", None)
        df.to_csv(file_path, index=False, encoding="utf-8")

        print("CSV Saved: {}".format(file_path))

# async def browser_health_check(driver, interval=60):
#     while True:
#         try:
#             driver.execute_script("return navigator.userAgent;")
#         except Exception as e:
#             print("Browser is unresponsive, restarting...")
#             driver.quit()
#             print("Setup WebDriver...")
#             header = Headers().generate()["User-Agent"]
#
#             browser_option = ChromeOptions()
#             browser_option.page_load_strategy = 'eager'
#             browser_option.add_argument('--blink-settings=imagesEnabled=false')  # 禁用图片
#             browser_option.add_argument("--headless")
#             browser_option.add_argument('--start-maximized')
#             browser_option.add_argument("--no-sandbox")
#             browser_option.add_argument("--disable-dev-shm-usage")
#             browser_option.add_argument("--ignore-certificate-errors")
#             browser_option.add_argument('--disable-extensions')
#             browser_option.add_argument('--disable-plugins')
#             browser_option.add_argument('--mute-audio')
#             browser_option.add_argument('--disable-web-security')
#             browser_option.add_argument('--disable-accelerated-video')  # 禁用视频
#             browser_option.add_argument('--disable-accelerated-video-encode')
#             browser_option.add_argument('--disable-accelerated-video-decode')
#             browser_option.add_argument("--disable-gpu")
#             browser_option.add_argument("--log-level=3")
#             browser_option.add_argument("--disable-notifications")
#             browser_option.add_argument('--disable-site-isolation-trials')
#             browser_option.add_argument("--disable-popup-blocking")
#             browser_option.add_argument('--disable-infobars')
#             browser_option.add_argument('--disable-renderer-backgrounding')
#             browser_option.add_argument('--disable-accelerated-2d-canvas')
#             browser_option.add_argument('--disable-software-rasterizer')
#             browser_option.add_argument('--disable-translate')
#             browser_option.add_argument("--user-agent={}".format(header))
#             chrome_service = ChromeService(log_path=os.devnull)
#             driver = webdriver.Chrome(options=browser_option, service=chrome_service)
#         await asyncio.sleep(interval)

if __name__ == "__main__":
    main()
