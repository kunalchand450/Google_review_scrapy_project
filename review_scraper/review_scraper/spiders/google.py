import scrapy
from scrapy.http.request import Request
import re


class GoogleSpider(scrapy.Spider):
    name = 'google'

    HEADERS = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66",
        'referer': None
    }

    def start_requests(self):
        urls = [
            "https://www.google.com/search?q=mumbai+airport&rlz=1C1CHBF_enIN1007IN1007&sxsrf=ALiCzsZ6M6vaZgnVTrdsB5IzGZ8YdmzxmA%3A1670818598218&ei=JquWY5f4DNOxmgfTs57wCA&ved=0ahUKEwiXo5-onPP7AhXTmOYKHdOZB44Q4dUDCBA&uact=5&oq=mumbai+airport&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzINCAAQsQMQkQIQRhD7ATIICAAQsQMQkQIyBQgAEJECMggIABCxAxCRAjILCAAQsQMQgwEQkQIyCAgAEIAEELEDMgsIABCABBCxAxCDATIICAAQgAQQsQMyBQgAEIAEMgUIABCABDoKCAAQRxDWBBCwAzoHCAAQsAMQQzoNCAAQ5AIQ1gQQsAMYAToSCC4QxwEQ0QMQyAMQsAMQQxgCOhIILhDHARCvARDIAxCwAxBDGAI6DwguENQCEMgDELADEEMYAjoECCMQJzoKCC4QxwEQrwEQQzoECAAQQzoHCCMQ6gIQJzoSCC4QxwEQ0QMQ6gIQtAIQQxgDOhIILhDHARCvARDqAhC0AhBDGAM6DAgAEOoCELQCEEMYAzoSCC4QrwEQxwEQ6gIQtAIQQxgDOgQILhBDOgoIABCxAxCDARBDOg4ILhCxAxCDARDHARCvAToLCC4QgAQQsQMQgwE6DQgAEIAEEIcCELEDEBQ6CgguELEDENQCEEM6CAgAELEDEIMBSgQIQRgASgQIRhgBUK4FWNM0YJ05aAJwAXgEgAHgAYgBrhuSAQYwLjE0LjWYAQCgAQGwARTIARPAAQHaAQYIARABGAnaAQYIAhABGAjaAQYIAxABGAE&sclient=gws-wiz-serp#lrd=0x3be7c85099bd2947:0x1ecc1a60c474a8ae,1,,,"]
        

        for url in urls:
            async_id = url.split("lrd=")[1].split(",")[0]
            ajax_url = "https://www.google.com/async/reviewDialog?async=feature_id:" + str(
                async_id) + ",start_index:0,_fmt:pc,sort_by:newestFirst"
            yield Request(url=ajax_url, headers=self.HEADERS, callback=self.get_total_iteration)

    def get_total_iteration(self, response):
        total_reviews_text = response.css('.z5jxId::text').extract_first()
        total_reviews = int(re.sub(r'[^0-9]', '', total_reviews_text))

        temp = total_reviews / 10  # since
        new_num = int(temp)
        if temp > new_num:
            new_num += 1
        iteration_number = new_num

        j = 0
        print(iteration_number)
        if total_reviews > 10:
            for _ in range(0, iteration_number + 1):
                yield Request(url=response.request.url.replace('start_index:0', f'start_index:{j}'),
                              headers=self.HEADERS, callback=self.parse_reviews, dont_filter=True)
                j += 10
        else:
            yield Request(url=response.request.url, headers=self.HEADERS, callback=self.parse_reviews, dont_filter=True)

    def parse_reviews(self, response):
        all_reviews = response.xpath('//*[@id="reviewSort"]/div/div[2]/div')

        for review in all_reviews:
            # reviewer = review.xpath('.//div[@class="TSUbDb"]/a/text()').extract_first()
            reviewer = review.css('div.TSUbDb a::text').extract_first()
            description = review.xpath('.//span[@class="review-full-text"]').extract_first()
            if description is None:
                description = review.css('.Jtu6Td span::text').extract_first()
                if description is None:
                    description = ''

            review_rating = float(
                review.xpath('.//span[@class="Fam1ne EBe2gf"]/@aria-label').extract_first().split(" ")[1])
            review_date = review.xpath('.//span[@class="dehysf lTi8oc"]/text()').extract_first()
            print(reviewer)
            print(description)
            print(review_rating)
            print(review_date)
            yield {
                "reviewer": reviewer,
                "description": description,
                "rating": review_rating,
                "review_date": review_date
            }