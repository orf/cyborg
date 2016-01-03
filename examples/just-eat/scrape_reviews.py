import asyncio
import sys
import string

from cyborg import scraper, Job
from aiopipes.filters import unique


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


@scraper("http://www.just-eat.co.uk{url}?page={page}")
def scrape_reviews(data, response, _continue):
    reviews = []

    for review in response.find(".restaurantRatings > li"):
        comments = review.get(".comments", "")
        if comments:
            comments = comments.text

        reviews.append({
            "date": review.get(".date").text,
            "name": review.get(".name").text,
            "comment": comments,
            "rating": review.get(".rating > img").attr["title"].split(" ")[0]
        })
    else:
        pass

    data["reviews"].extend(reviews)
    max_ratings_page = response.get(".reviewsPageCount").text.split(" of ")[1]

    if int(max_ratings_page) == data["page"]:
        return data

    data["page"] += 1

    return _continue(data, max=max_ratings_page)


if __name__ == "__main__":
    with open("output.json", "w") as output_fd:
        pipeline = Job("ReviewScraper") | scrape_places | unique("id") | scrape_reviews.parallel(5)
        pipeline < string.ascii_lowercase
        pipeline > output_fd

        pipeline.monitor() > sys.stdout

        pipeline.run_until_complete()
