from urllib.parse import unquote
from scrapy.http.response import Response

import re


class StoryParser:

    def parse_story(self, response: Response):
        story_title = self.extract_title(response)
        story_content = self.extract_story_content(response)
        age = self.extract_age(response)
        story_data = {
            "title": story_title,
            "content": story_content,
            "age": age,
            "value": "",
        }
        yield story_data

    def extract_age(self, response):

        # Use CSS selector to get the text that contains the age range
        age_text = response.css("div.breadcrumbs a::text").getall()

        # Combine the text elements into a single string
        combined_text = " ".join(age_text)

        # Use regex to find the age range, capturing any digits followed by any text
        match = re.findall(r"(\d+)", combined_text)
        if match and len(match) >= 2:
            # Return the age range as a string in the format "age1-age2"
            return f"{match[0]}-{match[1]}"

        return None  # Return None if no suitable ages are found

    def extract_story_content(self, response):

        content_patterns = [
            "div.blog-post_content p, div.blog-post_content h2, div.blog-post_content h3, div.blog-post_content h4",
            'main[id="main"] p, main[id="main"] h2, main[id="main"] h3, main[id="main"] h4',
        ]

        for pattern in content_patterns:
            content = self._process_pattern(pattern, response)
            if content:
                return content

        print(f"Could not extract content from {unquote(response.url)}")

    def extract_title(self, response):
        title_encoded = response.url.split("/")[-2]
        title = unquote(title_encoded)

        return title

    def _process_pattern(self, pattern, response):

        story_content = []
        content_elements = response.css(pattern)

        if len(content_elements) == 0:
            return None

        for element in content_elements:
            if element.root.tag == "p":
                # Get the text of the current <p> tag, including text from <span>
                paragraph_text = element.xpath(".//text()").getall()
                paragraph_text = " ".join(paragraph_text).strip()
                # Append the paragraph text to the story content if it's not empty
                if paragraph_text:  # Skip empty paragraphs
                    story_content.append(paragraph_text)
            else:
                # Handle headers (h2, h3, h4) by adding a newline before them
                header_text = element.xpath(".//text()").getall()
                header_text = " ".join(header_text).strip()
                if header_text:  # Skip empty headers
                    story_content.append(
                        "\n" + header_text + "\n"
                    )  # Add new lines around headers

            # Check for the end condition: If the next sibling is an <hr>
            next_sibling = element.xpath("following-sibling::*[1]")
            if next_sibling and next_sibling[0].root.tag == "hr":
                break  # End of story reached

        # Join all collected text into one string
        story_content = "".join(story_content).replace("\n", " ").replace("  ", " ")

        return story_content
