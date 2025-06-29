from argparse import ArgumentParser, BooleanOptionalAction
import json
import os
from pathlib import Path
import shutil

from convert import json_to_tag_list, tag_list_to_anki_package
from plotting import IMG_OUTPUT_FOLDER

def create_argparser() -> ArgumentParser:
    # Create the command line argument parser
    parser = ArgumentParser(
                    prog='json2anki',
                    description='Converts a json file with tags to an anki deck')

    # Add the arguments
    parser.add_argument('-f', '--file', default='locs.json', help='The input json file')
    parser.add_argument('-d', '--deck', default=None, help='The name of the generated anki deck')
    parser.add_argument('-o', '--output', default='deck.apkg', help='The name of the generated file')
    parser.add_argument('-fl', '--flat', action=BooleanOptionalAction, help='Generate a flat map with no labels and colors instead of the default map')

    return parser

def main():
    parser = create_argparser()

    # Parse the arguments
    args = parser.parse_args()

    # If the input json file does not exist
    if not os.path.isfile(args.file):
        print(f'ERROR: Input JSON file "{args.file}" does not exist.')
        return

    # Open the json file
    with open(args.file) as json_file:
        # Read the json data from the file
        json_data = json.load(json_file)

    # Convert the json to list of tags
    tags = json_to_tag_list(json_data)

    # Remove output image folder if exists
    if os.path.isdir(IMG_OUTPUT_FOLDER):
        shutil.rmtree(IMG_OUTPUT_FOLDER)
    
    # Create image output folder if not exists
    Path(IMG_OUTPUT_FOLDER).mkdir()

    try:
        # Generate anki package
        deck_name = args.deck if args.deck else json_data['name']
        anki_package = tag_list_to_anki_package(tags, deck_name, args.flat)

        # Save the package file
        anki_package.write_to_file(args.output)

        # Print finished message
        print(f'FINISHED: Created deck at output file "{args.output}"')
    except:
        pass

    # Remove output image folder
    shutil.rmtree(IMG_OUTPUT_FOLDER)

if __name__ == '__main__':
    main()