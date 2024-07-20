from time import sleep
import os

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium import webdriver

from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import TimeoutException, NoSuchElementException




# if os.path.exists("twitter_photos")==False:
#     os.mkdir("twitter_photos")
#
# if os.path.exists("twitter_videos")==False:
#     os.mkdir("twitter_videos")

class Tweet:
    def __init__(
        self,
        card: webdriver,
        driver: webdriver,
        actions: ActionChains,
        scrape_poster_details=False,
    ) -> None:
        self.card=card
        self.driver = driver
        self.error = False
        self.tweet = None


        try:
            self.user = card.find_element(
                "xpath", './/div[@data-testid="User-Name"]//span'
            ).text
        except NoSuchElementException:
            self.error = True
            self.user = "skip"

        try:
            self.handle = card.find_element(
                "xpath", './/span[contains(text(), "@")]'
            ).text
        except NoSuchElementException:
            self.error = True
            self.handle = "skip"

        try:
            self.date_time = card.find_element("xpath", ".//time").get_attribute(
                "datetime"
            )

            if self.date_time is not None:
                self.is_ad = False
        except NoSuchElementException:
            self.is_ad = True
            self.error = True
            self.date_time = "skip"

        if self.error:
            return

        try:
            card.find_element(
                "xpath", './/*[local-name()="svg" and @data-testid="icon-verified"]'
            )

            self.verified = True
        except NoSuchElementException:
            self.verified = False

        self.content = ""
        contents = card.find_elements(
            "xpath",
            '(.//div[@data-testid="tweetText"])[1]/span | (.//div[@data-testid="tweetText"])[1]/a',
        )

        for index, content in enumerate(contents):
            self.content += content.text

        try:
            self.reply_cnt = card.find_element(
                "xpath",
                './/button[contains(@aria-label,"Reply")]'
            ).get_attribute("aria-label").split(" ")[0]

            if self.reply_cnt == "":
                self.reply_cnt = "0"
        except NoSuchElementException:
            self.reply_cnt = "0"

        try:
            self.retweet_cnt = card.find_element(
                "xpath", './/button[contains(@aria-label,"Repost")]'
            ).get_attribute("aria-label").split(" ")[0]

            if self.retweet_cnt == "":
                self.retweet_cnt = "0"
        except NoSuchElementException:
            self.retweet_cnt = "0"
        # // span[ @ data - testid = "app-text-transition-container"]
        try:
            self.like_cnt = card.find_element(
                "xpath",'.//button[contains(@aria-label,"Like")]'
            ).get_attribute("aria-label").split(" ")[0]

            if self.like_cnt == "":
                self.like_cnt = "0"
        except NoSuchElementException:
            self.like_cnt = "0"

        try:
            self.analytics_cnt = card.find_element(
                "xpath", './/a[contains(@href, "/analytics")]'
            ).get_attribute("aria-label").split(" ")[0]


            if self.analytics_cnt == "":
                self.analytics_cnt = "0"
        except NoSuchElementException:
            self.analytics_cnt = "0"

        try:
            self.tags = card.find_elements(
                "xpath",
                './/a[contains(@href, "src=hashtag_click")]',
            )

            self.tags = [tag.text for tag in self.tags]
        except NoSuchElementException:
            self.tags = []

        try:
            self.mentions = card.find_elements(
                "xpath",
                '(.//div[@data-testid="tweetText"])[1]//a[contains(text(), "@")]',
            )

            self.mentions = [mention.text for mention in self.mentions]
        except NoSuchElementException:
            self.mentions = []

        try:
            raw_emojis = card.find_elements(
                "xpath",
                '(.//div[@data-testid="tweetText"])[1]/img[contains(@src, "emoji")]',
            )

            self.emojis = [
                emoji.get_attribute("alt").encode("unicode-escape").decode("ASCII")
                for emoji in raw_emojis
            ]
        except NoSuchElementException:
            self.emojis = []

        try:
            self.profile_img = card.find_element(
                "xpath", './/div[@data-testid="Tweet-User-Avatar"]//img'
            ).get_attribute("src")
        except NoSuchElementException:
            self.profile_img = ""

        try:
            self.tweet_link = card.find_element(
                "xpath",
                ".//a[contains(@href, '/status/')]",
            ).get_attribute("href")
            self.tweet_id = str(self.tweet_link.split("/")[-1])
        except NoSuchElementException:
            self.tweet_link = ""
            self.tweet_id = ""

        # try:
        #     # 找到所有图片元素
        #     image_elements = card.find_elements("xpath", './/div[@data-testid="tweetPhoto"]//img')
        #     image_urls = [img.get_attribute("src") for img in image_elements]
        #
        #     # 创建保存图片的文件夹
        #     image_folder = "twitter_photos"
        #     os.makedirs(image_folder, exist_ok=True)
        #
        #     for idx, image_url in enumerate(image_urls):
        #         img_name = f"{self.tweet_id}_{idx + 1}.jpg"
        #         img_path = os.path.join(image_folder, img_name)
        #
        #         # 下载并保存图片
        #         with open(img_path, mode='wb') as file:
        #             file.write(requests.get(image_url).content)
        #
        #     self.tweet_images = image_urls
        #
        # except NoSuchElementException:
        #     self.tweet_images = []


        # try:
        #     # from fake_headers import Headers
        #     # header = Headers().generate()["User-Agent"]
        #     # browser_option=Options()
        #     # browser_option.add_argument("--no-sandbox")
        #     # browser_option.add_argument("--disable-dev-shm-usage")
        #     # browser_option.add_argument("--ignore-certificate-errors")
        #     # browser_option.add_argument("--disable-gpu")
        #     # browser_option.add_argument("--log-level=3")
        #     # browser_option.add_argument("--disable-notifications")
        #     # browser_option.add_argument("--disable-popup-blocking")
        #     # browser_option.add_argument("--user-agent={}".format(header))
        #     # new_driver=webdriver.Firefox(options=browser_option)
        #     #
        #     # new_driver.get(self.tweet_link)
        #     # # 定义请求拦截器
        #     # def request_interceptor(request):
        #     #     if ".m3u8" in request.url:
        #     #         print(f"Intercepted m3u8 request: {request.url}")
        #     #         # 你可以在这里修改请求，例如添加或删除头部
        #     #         request.headers['User-Agent'] = 'MyCustomUserAgent'
        #     #
        #     # new_driver.request_interceptor = request_interceptor
        #     #
        #     # #  # 打开目标网页
        #     # # handles=driver.window_handles
        #     # #
        #     # # driver.switch_to.window(handles[1])
        #     #
        #     # try:
        #     #     # 等待推文加载
        #     #     try:
        #     #         WebDriverWait(new_driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "article")))
        #     #     except TimeoutException:
        #     #         print("Timeout: No tweet found within the given time.")
        #     #         new_driver.quit()
        #     #
        #     #     # 等待推文中的视频加载
        #     #     try:
        #     #         WebDriverWait(new_driver, 15).until(
        #     #             EC.presence_of_element_located((By.XPATH, "//div[@data-testid='videoPlayer']"))
        #     #         )
        #     #     except TimeoutException:
        #     #         print("Timeout: No video found within the given time.")
        #     #         new_driver.quit()
        #     #
        #     #
        #     #     # 等待一段时间，让视频的请求被发送
        #     #     try:
        #     #         WebDriverWait(new_driver, 30).until(
        #     #             lambda d: any('.m3u8' in request.url for request in d.requests)
        #     #         )
        #     #         print("m3u8 request found.")
        #     #     except TimeoutException:
        #     #         print("Timeout: No m3u8 request found within the given time.")
        #     #         new_driver.quit()
        #     #
        #     #     # 打印所有捕获的请求，调试用
        #     #     for request in driver.requests:
        #     #         print(f"Request URL: {request.url}, Method: {request.method}, Headers: {request.headers}")
        #     #
        #     #     # 从捕获的请求中提取m3u8 URL
        #     #     m3u8_urls = [request.url for request in new_driver.requests if '.m3u8' in request.path]
        #     #
        #     #     if m3u8_urls:
        #     #         print(f"Found m3u8 URL: {m3u8_urls[0]}")
        #     #         # 假设我们只需要第一个找到的m3u8 URL
        #     #         self.tweet_videos = m3u8_urls[0]
        #     #     else:
        #     #         print("m3u8 URL not found")
        #     self.tweet_videos = ""
        #
        #     # except Exception as e:
        #     #     print(f"An error occurred: {e}")
        #     #     self.tweet_videos = ""
        #     #     new_driver.quit()


        except TimeoutException:
            print("Loading the tweet took too much time.")
            self.tweet_videos = ""
        except NoSuchElementException:
            print("Video element not found on the page.")
            self.tweet_videos = ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.tweet_videos = ""




        self.following_cnt = "0"
        self.followers_cnt = "0"
        self.user_id = None

        if scrape_poster_details:
            el_name = card.find_element(
                "xpath", './/div[@data-testid="User-Name"]//span'
            )

            ext_hover_card = False
            ext_user_id = False
            ext_following = False
            ext_followers = False
            hover_attempt = 0

            while (
                not ext_hover_card
                or not ext_user_id
                or not ext_following
                or not ext_followers
            ):
                try:
                    actions.move_to_element(el_name).perform()

                    hover_card = driver.find_element(
                        "xpath", '//div[@data-testid="hoverCardParent"]'
                    )

                    ext_hover_card = True

                    while not ext_user_id:
                        try:
                            raw_user_id = hover_card.find_element(
                                "xpath",
                                '(.//div[contains(@data-testid, "-follow")]) | (.//div[contains(@data-testid, "-unfollow")])',
                            ).get_attribute("data-testid")

                            if raw_user_id == "":
                                self.user_id = None
                            else:
                                self.user_id = str(raw_user_id.split("-")[0])

                            ext_user_id = True
                        except NoSuchElementException:
                            continue
                        except StaleElementReferenceException:
                            self.error = True
                            return

                    while not ext_following:
                        try:
                            self.following_cnt = hover_card.find_element(
                                "xpath", './/a[contains(@href, "/following")]//span'
                            ).text

                            if self.following_cnt == "":
                                self.following_cnt = "0"

                            ext_following = True
                        except NoSuchElementException:
                            continue
                        except StaleElementReferenceException:
                            self.error = True
                            return

                    while not ext_followers:
                        try:
                            self.followers_cnt = hover_card.find_element(
                                "xpath",
                                './/a[contains(@href, "/verified_followers")]//span',
                            ).text

                            if self.followers_cnt == "":
                                self.followers_cnt = "0"

                            ext_followers = True
                        except NoSuchElementException:
                            continue
                        except StaleElementReferenceException:
                            self.error = True
                            return
                except NoSuchElementException:
                    if hover_attempt == 3:
                        self.error
                        return
                    hover_attempt += 1
                    sleep(0.5)
                    continue
                except StaleElementReferenceException:
                    self.error = True
                    return

            if ext_hover_card and ext_following and ext_followers:
                actions.reset_actions()

        self.tweet = (
            self.user,
            self.handle,
            self.date_time,
            self.verified,
            self.content,
            self.reply_cnt,
            self.retweet_cnt,
            self.like_cnt,
            self.analytics_cnt,
            self.tags,
            self.mentions,
            self.emojis,
            self.profile_img,
            self.tweet_link,
            self.tweet_id,
            # self.tweet_images,
            # self.tweet_videos,
            self.user_id,
            self.following_cnt,
            self.followers_cnt,
        )

        pass
