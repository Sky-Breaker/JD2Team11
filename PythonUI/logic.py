import time
import sys
import os

def clear_console():
    #clears console 
    os.system('cls' if os.name == 'nt' else 'clear')

def show_help():
    #Display help information for each g code command
    clear_console()
    print("="* 50)
    print("HELP - COMMAND DESCRIPTIONS")
    print("="*50)
    print()
    print("Available Commands:")
    print("G0")
    print("G1")
    print("G90")
    print("G20")
    print("G21")
    print("M2")
    print("M6")
    print()
    print("Press 'b' to go back to the selection menu")
    print("="*50)
    print()

    while True: 
        choice = input("Enter your choice").strip().lower()
        if choice == 'g0':
            print("Move arm at maximum speed to given coordinate")
        elif choice == 'g1':
            print("Move arm to specific position at a specific controlled speed")
        elif choice == 'g90':
            print("Sets arm to Absolute Position Mode, where the output is 'X' distance from the origin")
        elif choice == 'g20':
            print("Sets units to imperial system")
        elif choice == 'g21':
            print("Sets unit of measurement to millimeters (metric)")
        elif choice == 'g2':
            print("End program")
        elif choice == 'g6':
            print("Change tool command")
        elif choice == 'b':
            return False
        else: 
            print("Invalid Input. Commands are case sensitive")
        
def execute_command(command):
    print(f"\nProgram is busy executing G-code command {command}")

def main_menu():
    while True:
        clear_console()
        print("=" * 50)
        print("MAIN MENU")
        print("=" * 50)
        print()
        print("Please select from the available G-code commands")
        print("g0\ng1\ng90\ng20\ng21\nm2\nm6\n")
        print("Or press 'E' to exit\n")
        print("Enter '?' for help on commands")
        print("=" * 50)
        print()

        choice = input("Enter command:").strip().lower()

        if choice == '?':
            show_help()
            continue

        if choice == 'e':
            print("Exiting program...")
            time.sleep(1)
            sys.exit(0)
        if choice in ['g0', 'g1', 'g90', 'g20', 'g21', 'm2', 'm6']:
            execute_command(choice)
            input("\nPress Enter to continue")
        else:
            print("Invalid input. Try again")
            time.sleep(1)
        
def main():
    main_menu()

   

if __name__ ==  "__main__":
    main