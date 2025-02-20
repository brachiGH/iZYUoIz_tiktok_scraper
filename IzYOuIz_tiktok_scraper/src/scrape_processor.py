import os
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
from .download import VideoDownloader
from uuid import uuid4



def random_delay(min_delay=3, max_delay=6):
    """
    Introduce a random delay to mimic human behavior.

    Args:
        min_delay (int): Minimum delay in seconds.
        max_delay (int): Maximum delay in seconds.

    Returns:
        None
    """
    delay = random.uniform(min_delay, max_delay)
    print(f"Sleeping for {round(delay, 2)} seconds...")
    time.sleep(delay)

class TikTokScraper:
    def __init__(self, user_data_dir=None, retry_delay=2, max_retries=10):
        self.user_data_dir = user_data_dir
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        self.last_count = 0
        self.retry_count = 0
        self.max_videos = 4
        self.max_scroll_count = 4
        
    def set_max_videos(self, max):
        self.max_videos = max
        
    def set_max_scroll_count(self, max):
        self.max_scroll_count = max

    def get_chrome_driver(self):
        """
        Sets up a full browser mode undetected Chrome WebDriver.

        Returns:
            WebDriver: Configured Selenium WebDriver instance.
        """
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")  # Disable unnecessary notifications

        if self.user_data_dir:
            options.add_argument(f"--user-data-dir={self.user_data_dir}")  # Load user session
            print(f"Using Chrome user data directory: {self.user_data_dir}")

        # Use undetected ChromeDriver
        print("Running Selenium in undetected full browser mode.")
        self.driver = uc.Chrome(options=options)
        return self.driver

    def scroll(self,min_s=300, max_s=800):
        scroll_count = 0
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        current_scroll_position = 0

        # Scroll and detect the bottom
        while current_scroll_position < scroll_height and self.max_scroll_count > scroll_count:
            current_scroll_position += random.randint(min_s, max_s)  # Mimic a human scroll
            self.driver.execute_script(f"window.scrollTo(0, {current_scroll_position});")
            print(f"Scrolled to {current_scroll_position}px.")
            random_delay(1, 3)
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count += 1
        
    def is_progress_stalled(self, len_):
        if len_ == self.last_count:
            self.retry_count += 1
            print(f"No new videos found. Attempt {self.retry_count}/{self.max_retries}. Waiting for {self.retry_delay} seconds...")
            random_delay(self.retry_delay, self.retry_delay + 3)
            if self.retry_count >= self.max_retries:
                print("Maximum retries reached. Stopping scraping.")
                return True
            self.driver.refresh()
            print("Page refreshed. Continuing scraping...")
        else:
            self.last_count = len_
        return False

    def scrape_tiktok_video_information(self, video_urls):
        """
        Scrape video information (comments, description, and music name) from TikTok video URLs.

        Args:
            video_urls (list): List of TikTok video URLs.

        Returns:
            list: List of dictionaries containing video information.
        """
        video_infos = []
        try:
            for video_url in video_urls:
                video_id = video_url.split("/")[-1]
                self.driver.get("https://www.tiktok.com/embed/v2/"+video_id)
                WebDriverWait(self.driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")

                # Scraping the video informations
                song = self.driver.execute_script('''return document.querySelector('[data-e2e="video-v2-Card-CardMusic"]').innerText''')
                vid_stats = self.driver.execute_script('''try {
                                                    return texts = Array.from(document.querySelectorAll('[data-e2e="Player-Layer-LayerText"]'))
                                                                    .map(e => e.innerText);
                                                } catch (error) {
                                                    return ['0', '0', '0']
                                                }''')
                userid = self.driver.execute_script('''return document.querySelector('[data-e2e="video-v2-Card-CardUserSpan"]').innerText''')
                video_infos.append({
                    "video": f"https://www.tiktok.com/{userid}/video/{video_id}",  # change it
                    "videotiktok": f"https://www.tiktok.com/{userid}/video/{video_id}",
                    "song": song,
                    "userid": userid,
                    "like_count": vid_stats[0],
                    "comment_count": vid_stats[1],
                    "share_count": vid_stats[2],
                })

        except Exception as e:
            print(f"Error scraping video information: {e}")

        return video_infos

    def scrape_tiktok_videos(self, url_param, batch_size=50, rest_seconds=5):
        """
        Scrapes TikTok video URLs from a page in batches with rest intervals.

        Args:
            url_param (str): URL parameter for the TikTok page.
            batch_size (int): Number of videos to scrape before resting.
            rest_seconds (int): Seconds to rest between batches.

        Returns: list of video information.
        """
        driver = self.get_chrome_driver()
        driver.get(f"https://www.tiktok.com/{url_param}")

        video_urls = []

        try:
            while len(video_urls) < self.max_videos:
                WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
                random_delay() # wait for video to load
                self.scroll(self.max_scroll_count)

                # Check for new videos
                videos = driver.find_elements(By.XPATH, '//a[contains(@href, "/video/")]')
                for video in videos:
                    url = video.get_attribute("href")
                    if url and url not in video_urls:
                        video_urls.append(url)
                        print(f"Scraped: {url} ({len(video_urls)}/{self.max_videos})")
                        if len(video_urls) >= self.max_videos:
                            break
                        
                if self.is_progress_stalled(len(video_urls)):
                    break

                if len(video_urls) % batch_size == 0:
                    print(f"Resting for {rest_seconds} seconds...")
                    random_delay(rest_seconds, rest_seconds + 5)

            return self.scrape_tiktok_video_information(video_urls)
        except Exception as e:
            print(f"Error scraping video URLs: {e}")
            return []
        finally:
            driver.quit()

        
    def scrape_business_tiktok_videos(self):
        """
        Scrapes TikTok video URLs from a page in batches with rest intervals.

        Returns: list of video information.
        """
        driver = self.get_chrome_driver()
        driver.get(f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/pc/en")

        video_urls = []

        try:
            while len(video_urls) < self.max_videos:
                WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
                random_delay()
                self.scroll()

                # Check for new videos
                videos = driver.find_elements(By.XPATH, '//iframe[contains(@src, "/embed/")]')
                for video in videos:
                    url = video.get_attribute("src")
                    if url and url not in video_urls:
                        video_urls.append(url.split("?")[0])
                        print(f"Scraped: {url} ({len(video_urls)}/{self.max_videos})")
                        if len(video_urls) >= self.max_videos:
                            break

                if self.is_progress_stalled(len(video_urls)):
                    break

                driver.execute_script('''document.querySelector('[data-testid="cc_contentArea_viewmore_btn"]').click()''')

            return self.scrape_tiktok_video_information(video_urls)
        except Exception as e:
            print(f"Error scraping video URLs: {e}")
            return []
        finally:
            driver.quit()
            
            
    
    def scrape_business_tiktok_hashtags(self, topic_index):
        """
        Scrapes TikTok video URLs from a page in batches with rest intervals.

        Returns: list of video information.
        """
        driver = self.get_chrome_driver()
        driver.get(f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en")
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
        driver.execute_script('''document.querySelector('[data-type="select-option"][data-option-id="SelectOption'''+str(topic_index)+'''"] .byted-list-item-container').click()''')

        hashtags = []
        max_hashtags = self.max_videos

        try:
            while len(hashtags) < max_hashtags:
                WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
                random_delay() # wait for hashtags to load
                self.scroll(min_s=200, max_s=400)

                # Check for new videos
                tags = driver.execute_script('''return Array.from(document.querySelectorAll('.CardPc_titleText__RYOWo')).map(element => element.innerText);''')
                for tag in tags:
                    if tag and tag not in hashtags:
                        hashtags.append(tag.replace("#", "").strip())
                        print(f"Scraped: {tag} ({len(hashtags)}/{max_hashtags})")
                        if len(hashtags) >= max_hashtags:
                            break
                        
                if self.is_progress_stalled(len(hashtags)):
                    break

                driver.execute_script('''document.querySelector('[data-testid="cc_contentArea_viewmore_btn"]').click()''')
            
            print("done scraping hashtags")
            return hashtags
        except Exception as e:
            print(f"Error scraping video URLs: {e}")
            return []
        finally:
            driver.quit()





class TikTokProcessor:
    task_status = {} # [processing, downloading, completed]
    
    def __init__(self, user_data_dir=None):
        self.scraper = TikTokScraper(user_data_dir, retry_delay=2, max_retries=10)
        self.downloader = VideoDownloader(api_url="http://cobalt-api:9000/", rate_limit_delay=10)
        self.task_id = str(uuid4())  # Generate unique task ID
        TikTokProcessor.task_status[self.task_id] = {"status": "processing"}  # Store initial status
        
    def get_Process_id(self):
        return self.task_id

    def process_scraping(self, request):
        """
        Process the scraping task based on the request.

        Args:
            request (SearchRequest): Search request object containing search parameters.

        Returns:
            dict: Task status and results.
        """
        search_type = request.search_type
        search_query = request.search_query
        max_videos = request.max_videos

        if search_type not in ["hashtag", "userid", "trending", "topic"]:
            TikTokProcessor.task_status[self.task_id] = {"status": "failed", "error": "Invalid search type."}

        self.scraper.set_max_videos(max_videos)
        video_infos = {}

        print(f"Scraping up to {max_videos} videos for {search_type} '{search_query}'...")
        try:
            if search_type == "hashtag":
                url_param = f'tag/{search_query.replace("#", "").strip()}'
            elif search_type == "trending":
                url_param = "channel/trending-now"
            elif search_type == "userid":
                url_param = "@"+search_query.replace("@", "")
            elif search_type == "topic":
                url_param = ""
                self.scraper.set_max_scroll_count(max_videos//4)
                if search_query == "0":
                    video_infos = self.scraper.scrape_business_tiktok_videos()
                else:
                    hashtags = self.scraper.scrape_business_tiktok_hashtags(int(search_query)-1)
                    TikTokProcessor.task_status[self.task_id] = {"status": "completed", "hashtags": hashtags}
                    
                
            if url_param != "":
                video_infos = self.scraper.scrape_tiktok_videos(url_param, batch_size=50, rest_seconds=5)
            
            if  url_param != "" or search_query == "0":
                TikTokProcessor.task_status[self.task_id] = {"status": "downloading"}

                video_folder = os.path.join("videos", f"{search_query}_{search_type}_videos")
                os.makedirs(video_folder, exist_ok=True)

                print(f"Downloading videos to: {video_folder}")
                video_infos = self.downloader.process_videos(video_infos, video_folder)

                TikTokProcessor.task_status[self.task_id] = {"status": "completed", "videos": video_infos}

        except Exception as e:
            TikTokProcessor.task_status[self.task_id] = {"status": "failed", "error": str(e)}