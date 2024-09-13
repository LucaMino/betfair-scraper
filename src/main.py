import json
import os
import helper
from Betfair import Betfair

def main():
    helper.print_c('Start')

    # retrieve events
    betfair = Betfair()
    response = betfair.get_markets()

    # set file name
    current_date = helper.get_current_date()
    filename = os.path.join('src/data', f"betfair-events-{current_date}.json")

    # save json file
    with open(filename, 'w') as json_file:
        json.dump(response, json_file, indent=4)

    # exit()

# call main function
if __name__ == "__main__":
    main()