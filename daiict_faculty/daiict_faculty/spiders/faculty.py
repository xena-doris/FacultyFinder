import scrapy
from daiict_faculty.items import FacultyItem

class FacultySpider(scrapy.Spider):
    name = "faculty"
    allowed_domains = ["daiict.ac.in"]
    start_urls = [
        "https://www.daiict.ac.in/faculty"  # faculty listing page
        #"https://www.daiict.ac.in/adjunct-faculty"
        #"https://www.daiict.ac.in/adjunct-faculty-international"
        #"https://www.daiict.ac.in/distinguished-professor"
        #"https://www.daiict.ac.in/professor-practice"
    ]

    def clean_list(self, values):
        return [v.strip() for v in values if v and v.strip()]

    def parse(self, response):
        """
        Parse the main faculty listing page
        """
        faculty_cards = response.css("div.facultyInformation ul li")

        for faculty in faculty_cards:
            profile_link = faculty.css(
                "div.personalDetails h3 a::attr(href)" #faculty, distinguished professors
                #"div.personalDetail h3 a::attr(href)" #adjuct faculty
                #"div.personalsDetails h3 a::attr(href)" #professor of practice
            ).get()

            name = faculty.css(
                "div.personalDetails h3 a::text" #faculty, distinguished professor
                #"div.personalDetail h3 a::text"   #adjunct faculty
                #"div.personalsDetails h3 a::text" #professor of practice
            ).get()

            if profile_link:
                yield response.follow(
                    profile_link,
                    callback=self.parse_faculty_profile,
                    meta={"name": name, "profile_url": profile_link}
                )

    def parse_faculty_profile(self, response):
        """
        Parse individual faculty profile page
        """
        item = FacultyItem()

        item["name"] = response.meta.get("name")
        item["profile_url"] = response.meta.get("profile_url")

        # -------- LEFT SIDE --------
        item["education"] = response.css(
            "div.contact-box-p.pb0.EducationIcon div.detail div.field-content div.field.field--name-field-faculty-name.field--type-string.field--label-hidden.field__item::text"
        ).getall()

        item["email"] = response.css(
            "div.contact-box-p.emailIcon div.field__item::text"
        ).get()


        item["phone"] = response.css(
            "div.contact-box-p.pb0.mobileIcon div.detail div.field-content div.field.field--name-field-contact-no.field--type-string.field--label-hidden.field__item::text"
        ).get()

        item["address"] = response.css(
            "div.contact-box-p.pb0.addressIcon div.detail div.field-content div.field.field--name-field-address.field--type-string-long.field--label-hidden.field__item::text"
        ).get()

        item['faculty_web'] = response.css(
            "div.contact-box-p.facultyweb a::attr(href)"
        ).get()

        # -------- RIGHT SIDE --------
        item["biography"] = response.css(
            "div.about p::text"
        ).getall()


        item["specialization"] = response.xpath(
            "//div[@class='work-exp margin-bottom-20']//text()"
        ).getall()


        item["teaching"] = response.xpath(
            "//div[contains(@class,'work-exp') "
            "and not(contains(@class,'margin-bottom-20')) "
            "and not(contains(@class,'work-exp1'))]"
            "//text()"
        ).getall()


        #item["publications"] = response.xpath(
        #    "//div[contains(@class,'education') and contains(@class,'overflowContent')]"
        #    "//ul/li//text()"
        #).getall()

        item["publications"] = [
            " ".join(self.clean_list(li.xpath(".//text()").getall()))
            for li in response.xpath(
                "//div[contains(@class,'education') and contains(@class,'overflowContent')]//ul/li | "
                "//div[contains(@class,'education') and contains(@class,'overflowContent')]//ol/li"
            )
        ]




        item['research'] = response.xpath(
            "//div[@class='work-exp1']//text()"
        ).getall()

        yield item
