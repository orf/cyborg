# Cyborg

[![](https://travis-ci.org/orf/cyborg.svg)](https://travis-ci.org/orf/cyborg)

Cyborg is an asyncio Python 3 web scraping framework that helps you write programs to extract information
from websites by reading and inspecting their HTML.

## What?

Scraping websites for data can be fairly complex when you are dealing with data across multiple pages, request limits
and error handling. Cyborg aims to handle all of this for you transparently, so that you can focus on the actual
extraction of data rather than all the stuff around it. It does this by helping you break the process down into
smaller chunks, which can be combined into a Pipeline, for example below is a Pipeline that scrapes takeaway
reviews from Just-Eat (the complete example can be found in examples/just-eat):

    with open("output.json", "w") as output_fd:
        pipeline = Job("ReviewScraper") | scrape_places | unique("id") | scrape_reviews.parallel(5)
        pipeline < string.ascii_lowercase
        pipeline > output_fd

        pipeline.monitor() > sys.stdout

        pipeline.run_until_complete()


The pipeline has several stages:

    1. `scrape_places`
        - This scrapes the list of takeaways from a particular area. The area is found by the first letter of the postcode,
          so we brute-force this by inputting a-z (`pipeline < string.ascii_lowercase`)

    2. `unique('id')`
        - Takeaways may serve more than one area, this filters out any duplicate takeaways based on their ID

    3. `scrape_reviews.parallel(5)`
        - This starts 5 parallel tasks to scrape the reviews from a particular takeaway.


# Writing a scraper

A scraper is just a simple function that takes the page response and returns one or more tasks to be processed by
functions further down the pipeline. Here's a simple one from the examples directory:

    @scraper("http://www.just-eat.co.uk/london-{data}-takeaway")
    def scrape_places(data, response, output):
        for place in response.find(".restaurant"):
            if place.has_class("offlineRestaurant"):
                continue

            rating = place.get("p.rating a", None)
            if not rating:
                continue

            yield from output({
                "url": rating.attr["href"],
                "name": place.get("h2.name").text,
                "id": int(place.attr["data-restaurant-id"]),
                "page": 1,
                "reviews": []
            })

This goes through a list of places on Just-Eat, does some checks to make sure they are not offline and have been rated
before, and then yields a new task (using `yield from output`). The output contains all the data we need to carry on
processing, and this will be passed to the next stage in the pipeline.