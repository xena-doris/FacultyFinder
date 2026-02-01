import scrapy
from daiict_faculty.items import FacultyItem


FACULTY_TYPES = {
    "faculty": {
        "url": "https://www.daiict.ac.in/faculty",
        "card_class": "personalDetails",
    },
    "adjunct": {
        "url": "https://www.daiict.ac.in/adjunct-faculty",
        "card_class": "personalDetail",
    },
    "international_adjunct": {
        "url": "https://www.daiict.ac.in/adjunct-faculty-international",
        "card_class": "personalDetail",
    },
    "distinguished": {
        "url": "https://www.daiict.ac.in/distinguished-professor",
        "card_class": "personalDetails",
    },
    "practice": {
        "url": "https://www.daiict.ac.in/professor-practice",
        "card_class": "personalsDetails",
    },
}


class FacultySpider(scrapy.Spider):
    name = "faculty"
    allowed_domains = ["daiict.ac.in"]

    def __init__(self, faculty_type="faculty", *args, **kwargs):
        super().__init__(*args, **kwargs)

        if faculty_type not in FACULTY_TYPES:
            raise ValueError(
                f"Invalid faculty_type '{faculty_type}'. "
                f"Choose from {list(FACULTY_TYPES.keys())}"
            )

        self.faculty_type = faculty_type
        self.start_urls = [FACULTY_TYPES[faculty_type]["url"]]
        self.card_class = FACULTY_TYPES[faculty_type]["card_class"]

    def clean_list(self, values):
        """
        Remove empty and whitespace-only strings from a list.
        """
        return [v.strip() for v in values if v and v.strip()]

    def parse(self, response):
        """
        Parse the faculty listing page.
        """
        faculty_cards = response.css("div.facultyInformation ul li")

        for faculty in faculty_cards:
            profile_link = faculty.css(
                f"div.{self.card_class} h3 a::attr(href)"
            ).get()

            name = faculty.css(
                f"div.{self.card_class} h3 a::text"
            ).get()

            if profile_link:
                yield response.follow(
                    profile_link,
                    callback=self.parse_faculty_profile,
                    meta={
                        "name": name,
                        "profile_url": profile_link,
                        "faculty_type": self.faculty_type,
                    },
                )

    def parse_faculty_profile(self, response):
        """
        Parse an individual faculty profile page.
        """
        item = FacultyItem()

        item["name"] = response.meta.get("name")
        item["profile_url"] = response.meta.get("profile_url")
        item["faculty_type"] = response.meta.get("faculty_type")

        # -------- LEFT COLUMN --------
        item["education"] = self.clean_list(
            response.css(
                "div.contact-box-p.pb0.EducationIcon "
                "div.field__item::text"
            ).getall()
        )

        item["email"] = response.css(
            "div.contact-box-p.emailIcon div.field__item::text"
        ).get()

        item["phone"] = response.css(
            "div.contact-box-p.pb0.mobileIcon div.field__item::text"
        ).get()

        item["address"] = response.css(
            "div.contact-box-p.pb0.addressIcon div.field__item::text"
        ).get()

        item["faculty_web"] = response.css(
            "div.contact-box-p.facultyweb a::attr(href)"
        ).get()

        # -------- RIGHT COLUMN --------
        item["biography"] = self.clean_list(
            response.css("div.about p::text").getall()
        )

        item["specialization"] = self.clean_list(
            response.xpath(
                "//div[@class='work-exp margin-bottom-20']//text()"
            ).getall()
        )

        item["teaching"] = self.clean_list(
            response.xpath(
                "//div[contains(@class,'work-exp') "
                "and not(contains(@class,'margin-bottom-20')) "
                "and not(contains(@class,'work-exp1'))]"
                "//text()"
            ).getall()
        )

        item["publications"] = [
            " ".join(self.clean_list(li.xpath(".//text()").getall()))
            for li in response.xpath(
                "//div[contains(@class,'education') and contains(@class,'overflowContent')]"
                "//ul/li | "
                "//div[contains(@class,'education') and contains(@class,'overflowContent')]"
                "//ol/li"
            )
        ]

        item["research"] = self.clean_list(
            response.xpath("//div[@class='work-exp1']//text()").getall()
        )

        yield item
