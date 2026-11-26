import random

BANKROLL = 1000.00
MIN_BET = 5.00
MAX_BET = 100.00


def get_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer == 'y' or answer == 'n':
            return answer
        print("Invalid input. Please enter 'y' or 'n'.")


def roll_the_dice():
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    total = dice1 + dice2
    return total, dice1, dice2


def display_dice(total, dice1, dice2):
    print(f"Shooter rolled {dice1} and {dice2} for a total of {total}")


def get_bet_amount(bankroll):
    while True:
        try:
            amount = float(input(f"Enter bet amount (min ${MIN_BET:.2f} - max ${MAX_BET:.2f}): "))
            if amount < MIN_BET:
                print(f"Bet must be at least ${MIN_BET:.2f}.")
            elif amount > MAX_BET:
                print(f"Bet cannot exceed ${MAX_BET:.2f}.")
            elif amount > bankroll:
                print(f"You only have ${bankroll:.2f}.")
            else:
                return amount
        except ValueError:
            print("Please enter a valid number.")


def get_bet_type():
    while True:
        print("\n1) Pass Line Bet")
        print("2) Don't Pass Line Bet")
        choice = input("Choose 1 or 2: ").strip()
        if choice == "1":
            return "p"
        elif choice == "2":
            return "dp"
        else:
            print("That's not a valid choice.")


def come_out_decision(total, bet_type):
    if bet_type == "p":          
        if total == 7 or total == 11:
            print("Pass Line wins!")
            return "win"
        elif total == 2 or total == 3 or total == 12:
            print("Pass Line loses.")
            return "lose"
        else:
            print(f"The point is now {total}")
            return total                     
    else:                        
        if total == 2 or total == 3:
            print("Don't Pass wins!")
            return "win"
        elif total == 12:
            print("Don't Pass - Push (bet returned)")
            return "push"
        elif total == 7 or total == 11:
            print("Don't Pass loses.")
            return "lose"
        else:
            print(f"The point is now {total}")
            return total                     


def point_phase(point, bet_type):
    print(f"\n=== POINT PHASE (Point is {point}) ===")
    while True:
        total, dice1, dice2 = roll_the_dice()
        display_dice(total, dice1, dice2)

        if total == point:                   
            if bet_type == "p":
                print(f"Point {point} hit! Pass Line wins!")
                return "win"
            else:
                print(f"Point {point} hit! Don't Pass loses.")
                return "lose"
        elif total == 7:                     
            if bet_type == "p":
                print("7 out! Pass Line loses.")
                return "lose"
            else:
                print("7 out! Don't Pass wins!")
                return "win"
        else:
            print("No decision yet... rolling again.\n")


def update_bankroll(bankroll, bet_amount, result):
    if result == "win":
        return bankroll + (bet_amount * 2)
    elif result == "push":
        return bankroll + bet_amount
    else:  
        return bankroll


def main():
    bankroll = BANKROLL
    print("         CRAPS")
    print("Rules:")
    print("- Come-out: 7/11 Pass wins, 2/3/12 Pass loses")
    print("- 4-6,8-10 sets the POINT")
    print("- Then roll until POINT or 7")
    print("- Pass wins on point, loses on 7\n")

    while bankroll >= MIN_BET:
        print(f"\nYour current bankroll: ${bankroll:.2f}")

        play = get_yes_no("Would you like to play a round? (y/n): ")
        if play == "n":
            break

        bet_amount = get_bet_amount(bankroll)
        bankroll -= bet_amount

        bet_type = get_bet_type()

        print("\n--- COME OUT ROLL ---")
        total, dice1, dice2 = roll_the_dice()
        display_dice(total, dice1, dice2)

        
        result = come_out_decision(total, bet_type)

        if result != "win" and result != "lose" and result != "push":
            result = point_phase(result, bet_type)

        bankroll = update_bankroll(bankroll, bet_amount, result)

        print(f"Round complete. Your bankroll is now ${bankroll:.2f}")

    print("\nThanks for playing Craps!")
    print(f"Final bankroll: ${bankroll:.2f}")

if __name__ == "__main__":
    main()
