import scrapy
from urllib.parse import urljoin

import scrapy.http
from scrapy.http.response import Response

import re

from main.spiders.hala_halpers.story_parser import StoryParser


class HalaSpider(scrapy.Spider):
    name = "hala"
    allowed_domains = ["hala-stories.com"]
    start_urls = ["https://hala-stories.com/"]

    def parse(self, response: Response):

        CATEGORY_LINKS_XPATH = (
            "/html/body/header/div[1]/div/div/div/div/div[2]/div/nav/ul/li[1]/a",
            "/html/body/header/div[1]/div/div/div/div/div[2]/div/nav/ul/li[2]/a",
            "/html/body/header/div[1]/div/div/div/div/div[2]/div/nav/ul/li[3]/a",
        )
        for category_link_xpath in CATEGORY_LINKS_XPATH:
            category_link = response.xpath(category_link_xpath).attrib["href"]
            yield response.follow(category_link, self.parse_category, meta={"page": 1})

    def parse_category(self, response: Response):
        # CSS selector targeting <a> inside the <h3> with class 'blog-post_title'
        STORY_CSS_SELECTOR = "h3.blog-post_title a"

        # Select story links using the CSS selector
        story_links = response.css(STORY_CSS_SELECTOR)
        # Follow each story link
        for story_link in story_links:
            yield response.follow(story_link.attrib["href"], self.parse_story)

        # Handle pagination by incrementing the page number in the URL
        if len(story_links) > 0:
            # Extract the current page number from the URL, default to 1 if not present
            match = re.search(r"page/(\d+)", response.url)
            current_page = int(match.group(1)) if match else 1
            next_page_url = re.sub(
                r"page/\d+", f"page/{current_page + 1}", response.url
            )

            # If 'page' is not in the URL, append the pagination format
            if not match:
                next_page_url = urljoin(response.url, f"page/{current_page + 1}")

            # Follow the next page if there are stories on the current page
            yield response.follow(
                next_page_url, self.parse_category, meta={"page": current_page + 1}
            )

    def parse_story(self, response: Response):
        # Extract the story title
        yield from StoryParser().parse_story(response)
