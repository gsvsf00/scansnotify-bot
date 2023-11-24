import atexit
import logging
import os
import shutil
from threading import Thread
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# from ..core.exeptions import LNException
# from ..core.sources import crawler_list, prepare_crawler
# from ..models import Chapter, CombinedSearchResult, OutputFormat
# from .browser import Browser
# from .crawler import Crawler

logger = logging.getLogger(__name__)

class App:
    """Bots are based on top of an instance of this app"""

    def __init__(self):
        self.progress: float = 0
        self.user_input: Optional[str] = None
        self.crawler_links: List[str] = []
        #self.crawler: Optional[Crawler] = None
        self.login_data: Optional[Tuple[str, str]] = None
        #self.search_results: List[CombinedSearchResult] = []
        #self.output_path = C.DEFAULT_OUTPUT_PATH
        self.pack_by_volume = False
        #self.chapters: List[Chapter] = []
        self.book_cover: Optional[str] = None
        #self.output_formats: Dict[OutputFormat, bool] = {}
        self.archived_outputs = None
        self.good_file_name: str = ""
        self.no_suffix_after_filename = False
        atexit.register(self.destroy)
        print("_init_")

    def __background(self, target_method, *args, **kwargs):
        print("__background__")
        t = Thread(target=target_method, args=args, kwargs=kwargs)
        t.start()
        while t.is_alive():
            t.join(1)

    # ----------------------------------------------------------------------- #

    def initialize(self):
        logger.info("Initialized App")
        print("Initialized App")

    def destroy(self):
        print("App destroyed")
        #if self.crawler:
            #self.crawler.__del__()
        #self.chapters.clear()
        logger.info("App destroyed")

    # ----------------------------------------------------------------------- #

    # def prepare_search(self):
    #     """Requires: user_input"""
    #     """Produces: [crawler, output_path] or [crawler_links]"""
    #     if not self.user_input:
    #         raise LNException("User input is not valid")

    #     if self.user_input.startswith("http"):
    #         logger.info("Detected URL input")
    #         self.crawler = prepare_crawler(self.user_input)
    #     else:
    #         logger.info("Detected query input")
    #         self.crawler_links = [
    #             str(link)
    #             for link, crawler in crawler_list.items()
    #             if crawler.search_novel != Crawler.search_novel
    #         ]

    # def guess_novel_title(self, url: str) -> str:
    #     try:
    #         scraper = Scraper(url)
    #         response = scraper.get_response(url)
    #         reader = Document(response.text)
    #     except ScraperErrorGroup as e:
    #         if logger.isEnabledFor(logging.DEBUG):
    #             logger.exception("Failed to get response: %s", e)
    #         with Browser() as browser:
    #             browser.visit(url)
    #             browser.wait("body")
    #             reader = Document(browser.html)
    #     return reader.short_title()

    # def search_novel(self):
    #     """Requires: user_input, crawler_links"""
    #     """Produces: search_results"""
    #     logger.info("Searching for novels in %d sites...", len(self.crawler_links))

    #     search_novels(self)

    #     if not self.search_results:
    #         raise LNException("No results for: %s" % self.user_input)

    #     logger.info(
    #         "Total %d novels found from %d sites",
    #         len(self.search_results),
    #         len(self.crawler_links),
    #     )

    # # ----------------------------------------------------------------------- #

    # def can_do(self, prop_name):
    #     if not hasattr(self.crawler.__class__, prop_name):
    #         return False
    #     if not hasattr(Crawler, prop_name):
    #         return True
    #     return getattr(self.crawler.__class__, prop_name) != getattr(Crawler, prop_name)

    # def get_novel_info(self):
    #     """Requires: crawler, login_data"""
    #     """Produces: output_path"""
    #     if not isinstance(self.crawler, Crawler):
    #         raise LNException("No crawler is selected")

    #     if self.can_do("login") and self.login_data:
    #         logger.debug("Login with %s", self.login_data)
    #         self.crawler.login(*list(self.login_data))

    #     self.__background(self.crawler.read_novel_info)

    #     format_novel(self.crawler)
    #     if not len(self.crawler.chapters):
    #         raise Exception("No chapters found")
    #     if not len(self.crawler.volumes):
    #         raise Exception("No volumes found")

    #     if not self.good_file_name:
    #         self.good_file_name = slugify(
    #             self.crawler.novel_title,
    #             max_length=50,
    #             separator=" ",
    #             lowercase=False,
    #             word_boundary=True,
    #         )

    #     source_name = slugify(urlparse(self.crawler.home_url).netloc)
    #     self.output_path = os.path.join(
    #         C.DEFAULT_OUTPUT_PATH, source_name, self.good_file_name
    #     )

    # ----------------------------------------------------------------------- #