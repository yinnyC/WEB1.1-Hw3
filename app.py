from flask import Flask, request, render_template
from PIL import Image, ImageFilter, ImageOps
from pprint import PrettyPrinter
import json
import os
import random
import requests

app = Flask(__name__)


@app.route("/")
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template("home.html")


################################################################################
# COMPLIMENTS ROUTES
################################################################################


list_of_compliments = [
    "awesome",
    "beatific",
    "blithesome",
    "conscientious",
    "coruscant",
    "erudite",
    "exquisite",
    "fabulous",
    "fantastic",
    "gorgeous",
    "indubitable",
    "ineffable",
    "magnificent",
    "outstanding",
    "propitioius",
    "remarkable",
    "spectacular",
    "splendiferous",
    "stupendous",
    "super",
    "upbeat",
    "wondrous",
    "zoetic",
]


@app.route("/compliments")
def compliments():
    """Shows the user a form to get compliments."""
    return render_template("compliments_form.html")


@app.route("/compliments_results")
def compliments_results():
    """Show the user some compliments."""
    context = {
        "users_name": request.args.get("users_name"),
        "wants_compliments": request.args.get("wants_compliments"),
        "compliments": random.sample(
            list_of_compliments, k=int(request.args.get("num_compliments"))
        ),
    }

    return render_template("compliments_results.html", **context)


################################################################################
# ANIMAL FACTS ROUTE
################################################################################

animal_to_fact = {
    "koala": {
        "fact": "Koala fingerprints are so close to humans' that they could taint crime scenes.",
        "habitat": "Koalas live over a range of open forest and woodland communities",
        "physical characteristics": "large round head, big furry ears and big black nose.",
    },
    "parrot": {
        "fact": "Parrots will selflessly help each other out.",
        "habitat": "Most wild parrots live in the warm areas of the Southern Hemisphere",
        "physical characteristics": "Parrots have beaks that are strong and shaped rather like hooks.",
    },
    "mantis shrimp": {
        "fact": "The mantis shrimp has the world's fastest punch.",
        "habitat": "Mantis shrimp are usually found in shallow tropical or subtropical waters, with some species occasionally found in sub-Antarctic waters.",
        "physical characteristics": "Mantis shrimps are brightly colored.",
    },
    "lion": {
        "fact": "Female lions do 90 percent of the hunting.",
        "habitat": "Lions prefer grassland, savanna, dense scrub, and open woodland.",
        "physical characteristics": "Lions have strong, compact bodies and powerful forelegs, teeth and jaws for pulling down and killing prey.",
    },
    "narwhal": {
        "fact": 'Narwhal tusks are really an "inside out" tooth.',
        "habitat": "Narwhals spend their lives in the Arctic waters of Canada, Greenland, Norway and Russia.",
        "physical characteristics": "The narwhal is a chunky, stocky whale, with a small rounded head.",
    },
}


@app.route("/animal_facts")
def animal_facts():
    """Show a form to choose an animal and receive facts."""
    # Substract the key values and put them into a list
    animal_list = animal_to_fact.keys()
    chosen_animal = request.args.getlist("animal")
    if chosen_animal:  # Create New Dictionaries with chosen animals
        animal_fact = {animal: animal_to_fact[animal] for animal in chosen_animal}
    else:
        animal_fact = None
    context = {
        "animals": animal_list,
        "chosen_animal": chosen_animal,
        "animal_fact": animal_fact,
    }
    return render_template("animal_facts.html", **context)


################################################################################
# IMAGE FILTER ROUTE
################################################################################

filter_types_dict = {
    "blur": ImageFilter.BLUR,
    "contour": ImageFilter.CONTOUR,
    "detail": ImageFilter.DETAIL,
    "edge enhance": ImageFilter.EDGE_ENHANCE,
    "emboss": ImageFilter.EMBOSS,
    "sharpen": ImageFilter.SHARPEN,
    "smooth": ImageFilter.SMOOTH,
    "grey scale": ImageOps.grayscale,
}


def save_image(image, filter_type):
    """Save the image, then return the full file path of the saved image."""
    # Append the filter type at the beginning (in case the user wants to
    # apply multiple filters to 1 image, there won't be a name conflict)
    new_file_name = f"{filter_type}-{image.filename}"
    image.filename = new_file_name

    # Construct full file path
    file_path = os.path.join(app.root_path, "static/images", new_file_name)

    # Save the image
    image.save(file_path)

    return file_path


def apply_filter(file_path, filter_name):
    """Apply a Pillow filter to a saved image."""
    i = Image.open(file_path)
    i.thumbnail((500, 500))
    if filter_name == "grey scale":
        i = ImageOps.grayscale(i)
    else:
        i = i.filter(filter_types_dict.get(filter_name))
    i.save(file_path)


@app.route("/image_filter", methods=["GET", "POST"])
def image_filter():
    """Filter an image uploaded by the user, using the Pillow library."""
    filter_types = filter_types_dict.keys()

    if request.method == "POST":
        filter_type = request.form.get("filter_type")
        # Get the image file submitted by the user
        image = request.files.get("users_image")

        file_path = save_image(image, filter_type)
        apply_filter(file_path, filter_type)

        image_url = f"/static/images/{image.filename}"
        context = {
            "filter_types": filter_types,
            "image_url": image_url,
        }

        return render_template("image_filter.html", **context)

    else:

        context = {
            "filter_types": filter_types,
            "image_url": None,
        }
        return render_template("image_filter.html", **context)


################################################################################
# GIF SEARCH ROUTE
################################################################################

API_KEY = "LIVDSRZULELA"
TENOR_URL = "https://api.tenor.com/v1/search"
pp = PrettyPrinter(indent=4)


@app.route("/gif_search", methods=["GET", "POST"])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    if request.method == "POST":
        search_query = request.form.get("search_query")
        quantity = request.form.get("quantity")

        response = requests.get(
            TENOR_URL,
            {
                "q": search_query,
                "key": API_KEY,
                "limit": quantity,
            },
        )

        gifs = json.loads(response.content).get("results")

        context = {"gifs": gifs}

        # pp.pprint(gifs)

        return render_template("gif_search.html", **context)
    else:
        return render_template("gif_search.html")


if __name__ == "__main__":
    app.config["ENV"] = "development"
    app.run(debug=True)
