import scrapy


class HakawatySpider(scrapy.Spider):
    name = "hakawaty"
    allowed_domains = ["al-hakawati.net"]
    start_urls = ["https://al-hakawati.net/Stories/"]

    CATEGORY_NAME_XPATH = ".//span[@class='title-6']/text()"
    STORY_TABLE_ROWS_XPATH = "//table"
    CATEGORY_DIV_XPATH = "/html/body/div[2]/div[2]/div[3]/span"
    STORY_TITLE_XPATH = ".//span[@class='title-5']"
    STORY_CONTENT_XPATH = ".//span/p"
    children_categories = ["قصص للصغار", "ألف ليلة وليلة"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "main.pipelines.HakawatyPipeline": 1,
        }
    }

    def parse(self, response: scrapy.http.response.Response):
        categories = response.xpath(self.CATEGORY_DIV_XPATH)
        for category in categories:
            category_name = category.xpath(self.CATEGORY_NAME_XPATH).get().strip()

            category_link = category.xpath(".//a/@href").get()
            if category_name in self.children_categories and category_link is not None:

                yield response.follow(
                    category_link,
                    self.parse_category,
                    meta={"category_name": category_name},
                )

    def parse_category(self, response: scrapy.http.response.Response):
        category_name = response.meta["category_name"]
        stories = []

        table = response.xpath(self.STORY_TABLE_ROWS_XPATH)
        story_rows = table.xpath(".//tr")

        for row in story_rows:
            story_link = row.xpath(".//td/a/@href").get()
            if story_link:
                yield response.follow(
                    story_link, self.parse_story, meta={"category_name": category_name}
                )

    def parse_story(self, response: scrapy.http.response.Response):
        category_name = response.meta["category_name"]

        story_title_element = response.xpath(self.STORY_TITLE_XPATH)
        story_title = story_title_element.xpath("text()").get(default="").strip()

        story_content_element = response.xpath(self.STORY_CONTENT_XPATH)
        story_content = "\n".join(
            story_content_element.xpath(".//text()").getall()
        ).strip()
        story_content = story_content.replace("\n", " ").replace("  ", " ")

        if story_title and story_content:
            story_data = {
                "title": story_title,
                "content": story_content,
            }
            yield {category_name: story_data}
