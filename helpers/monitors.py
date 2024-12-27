import sys

# ANSI escape codes for colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_info(info_json):
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()

    # Define the ASCII box for the display
    box_width = 50
    print(f"{BLUE}=" * box_width + f"{RESET}")
    print(f"{BLUE}{'Match Information':^50}{RESET}")
    print(f"{BLUE}=" * box_width + f"{RESET}")
    
    # Print each field in the JSON with alignment and borders, applying colors
    print(f"{YELLOW}Time:{RESET}       {info_json['time']:<35} ")
    print(f"{YELLOW}Division:{RESET}   {info_json['division']:<35} ")
    print(f"{YELLOW}Match:{RESET}      {info_json['matchnum']:<35} ")
    print(f"{YELLOW}Details:{RESET}    {info_json['matchdetails']:<35} ")

    print(f"{BLUE}=" * box_width + f"{RESET}")

    print(f"{GREEN}{info_json['saved']:<35} ")
    print(f"{GREEN}{info_json['runtime']:<35} ")

    # Handling errors as a list and printing them in red
    print(f"{BLUE}=" * box_width + f"{RESET}")
    print(f"{RED}Errors:{RESET}")
    if isinstance(info_json['errors'], list):
        for error in info_json['errors']:
            print(f"  - {RED}{error}{RESET}")  # Color the errors in red
    else:
        print(f"  - {RED}{info_json['errors']}{RESET}")  # In case 'errors' is not a list

    # Closing the box
    print(f"{BLUE}=" * box_width + f"{RESET}")

# USAGE : print_info(info_json)