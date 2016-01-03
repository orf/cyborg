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
    - This scrapes the list of takeaways from a particular area. The area is found by the first letter of the postcode, so we brute-force this by inputting a-z (`pipeline < string.ascii_lowercase`)

  2. `unique('id')`
    - Takeaways may serve more than one area, this filters out any duplicate takeaways based on their ID

  3. `scrape_reviews.parallel(5)`
    - This starts 5 parallel tasks to scrape the reviews from a particular takeaway.