import os
import random
from models import Location, Tag
from genanki import Deck, Model, Package, Note
from tqdm import tqdm

from plotting import plot_tag_plain


DEFAULT_COLOR = [0, 0, 0]


def rgb_list_to_hex(rgb: list[int]) -> str:
    return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])


def json_to_tag_list(json_data) -> list[Tag]:
    """
    Convert a json object to a list of tags
    """

    # Check that the json has tags stored in the extra data
    if 'extra' not in json_data:
        print('ERROR: JSON contains no extra section')
        exit(1)
    if 'tags' not in json_data['extra']:
        print('ERROR: JSON extra data contains no tags')
        exit(1)

    # Keep a dictionary of every tag
    #   Key:   The tags name
    #   Value: The tag object
    tags_dict: dict[str, Tag] = {}

    # Get all the tags from the global extra data of the json
    extra_data_tags = json_data['extra']['tags']

    # For every tag defined in the extra data
    for tag in extra_data_tags:
        # Get the data for the current tag
        tag_data = extra_data_tags[tag]

        # Get the color from the json if present, else use the default color
        color = tag_data['color'] if 'color' in tag_data else DEFAULT_COLOR

        # Create the tag object and put it in the dictionary.
        # Start with an empty coordinates list. The list wil 
        # be filled later when iterating through the actual 
        # coordinates.
        tags_dict[tag] = Tag(tag, rgb_list_to_hex(color), [])

    # Get the coordinates from the JSON
    coordinates = json_data['customCoordinates']

    # For every defined coordinate
    for coordinate in coordinates:
        # If the coordinate has no extra data defnied
        if 'extra' not in coordinate:
            # Skip this coordinate, since it doesn't have tags
            continue

        # Get the extra data of the coordinate
        extra_data = coordinate['extra']

        # If the extra data contains no tags
        if 'tags' not in extra_data:
            # Skip this coordinate, since it doesn't have tags
            continue

        # Extract the fields from the json
        tags = extra_data['tags']
        lat = coordinate['lat']
        lng = coordinate['lng']

        # Add the coordinate to every tag it has in its extra
        # data 
        for tag in tags:
            # It appears that not every tag must be in the global
            # extra section. So we check here if the tag exists
            # and if not, create it
            if tag not in tags_dict:
                tags_dict[tag] = Tag(tag, rgb_list_to_hex(DEFAULT_COLOR), [])

            # Append the coordinate to the tags locations
            tags_dict[tag].locations.append(Location(lat, lng))

    return list(tags_dict.values())


def tag_list_to_anki_package(tags: list[Tag], deck_name: str) -> Package:
    """
    Convert a list of tags to an anki package
    """

    # Generate random ids
    MODEL_ID = random.randrange(1 << 30, 1 << 31)
    DECK_ID = random.randrange(1 << 30, 1 << 31)

    # Create the model
    model = Model(
        MODEL_ID,
        'JSON Card Model',
        fields=[
            {'name': 'Label'},
            {'name': 'PlotAnswer'}
        ],
        templates=[{
            'name': 'Card 1',
            'qfmt': '<div style="text-align: center; ">{{Label}}</div>',
            'afmt': '<div style="text-align: center; ">{{FrontSide}}<hr id="answer">{{PlotAnswer}}</div>'
        }]
    )

    # Create a deck, a package and a list of media files.
    # The list of media files will store the locations of 
    # the images. Images are referenced by path.
    deck = Deck(DECK_ID, deck_name)
    package = Package(deck)
    media = []

    # For every tag
    for tag in tqdm(tags, desc='Generating cards', unit='tags'):
        # Plot the tags location and save to an image file
        plot_image_file = plot_tag_plain(tag)

        # Append the path to the file to the media list
        media.append(plot_image_file)

        # Create the image tag for the backside of the anki 
        # card. Use just the image name as the src since 
        # anki will resolve the full path and it wouldn't 
        # even work when specifying the full path here.
        plot_image_tag = f'<img src="{os.path.basename(plot_image_file)}">'

        # Create the note
        note = Note(
            model=model,
            fields=[tag.tag_name, plot_image_tag]
        )

        # Add the note to the deck
        deck.add_note(note)

    # Set the media files list on the package so that
    # the files are bundled inside the generated .apkg
    # file
    package.media_files = media

    return package