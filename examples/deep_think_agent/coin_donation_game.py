import time
import os

from isek.models.openai.chat import OpenAIModel
from isek.agent.persona import Persona
from isek.node.isek_center_registry import IsekCenterRegistry
from isek.agent.distributed_agent import DistributedAgent
from dotenv import load_dotenv


load_dotenv()

model = OpenAIModel(
    model_name=os.environ.get("OPENAI_MODEL_NAME"),
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)

P1_info = {
    "name": "Doe",
    "bio": "An experienced game player",
    "lore": "Your mission is to win the game",
    "knowledge": "probability calculation, game theory, game strategies",
    "routine": [
        "you are a player, you need to win the game",
        "you are asked to donate at least one coin each round",
        "if you donate the least coins, you will have to donate extra 10 coins as punishment",
        "if you run out of coins, you will be lose the game",
        "the last player with coins wins the game",
        "you donate different amount of coins each round to confuse other players",
        "output only the donation amount number without any explanation and nothing else",
    ],
}

P2_info = {
    "name": "Eddie",
    "bio": "An experienced game player",
    "lore": "Your mission is to win the game",
    "knowledge": "probability calculation, game theory, game strategies",
    "routine": [
        "you are a player, you need to win the game",
        "you are asked to donate at least one coin each round",
        "if you donate the least coins, you will have to donate extra 10 coins as punishment",
        "if you run out of coins, you will be lose the game",
        "the last player with coins wins the game",
        "you are smart and able to adjust based on other players' action",
        "you donate different amount of coins each round to confuse other players",
        "output only the donation amount number without any explanation and nothing else",
    ],
}

P3_info = {
    "name": "Bob",
    "bio": "An experienced game player",
    "lore": "Your mission is to win the game",
    "knowledge": "probability calculation, game theory, game strategies",
    "routine": [
        "you are a player, you need to win the game",
        "you are asked to donate at least one coin each round",
        "if you donate the least coins, you will have to donate extra 10 coins as punishment",
        "if you run out of coins, you will be lose the game",
        "you always act based on other players' action",
        "the last player with coins wins the game",
        "you donate different amount of coins each round to confuse other players",
        "output only the donation amount number without any explanation and nothing else",
    ],
}

P4_info = {
    "name": "Alice",
    "bio": "An experienced game player",
    "lore": "Your mission is to win the game",
    "knowledge": "probability calculation, game theory, game strategies",
    "routine": [
        "you are a player, you need to win the game",
        "you are asked to donate at least one coin each round",
        "if you donate the least coins, you will have to donate extra 10 coins as punishment",
        "if you run out of coins, you will be lose the game",
        "the last player with coins wins the game",
        "you are super smart and you know how to win the game",
        "you donate different amount of coins each round to confuse other players",
        "output only the donation amount number without any explanation and nothing else",
    ],
}

info_array = [P1_info, P2_info, P3_info, P4_info]

Agent_array = []
registry = registry = IsekCenterRegistry()
for index, player in enumerate(info_array):
    # print(player)
    persona_temp = Persona.from_json(player)

    Agent_temp = DistributedAgent(
        persona=persona_temp,
        host="localhost",
        port=int(8080 + index),
        registry=registry,
        model=model,
        deepthink_enabled=True,
    )
    Agent_temp.build(daemon=True)
    Agent_array.append(Agent_temp)

time.sleep(2)


def print_participants_status(participants):
    """Prints the status of all participants"""
    print("\n--- Current Status ---")
    for p in participants:
        # To clearly show who is out, 0 or negative coins can be displayed
        status = "Eliminated" if p["coins"] <= 0 else f"{p['coins']} coins"
        print(f"{p['name']}: {status}")
    print("------------------")


def get_player_donation(player):
    """Gets valid donation input from the player"""
    while True:
        # If the player has no coins left, skip input directly (theoretically shouldn't happen, as they'd be filtered by active_participants)
        if player["coins"] <= 0:
            print(f"{player['name']} is eliminated and cannot donate.")
            return 0

        try:
            donation = int(
                input(
                    f"{player['name']} (you have {player['coins']} coins), please enter the amount of coins you want to donate (1 - {player['coins']}): "
                )
            )
            if donation < 1:
                print("Error: Donation amount must be at least 1.")
            elif donation > player["coins"]:
                print(
                    f"Error: You only have {player['coins']} coins, you cannot donate {donation}."
                )
            else:
                return donation
        except ValueError:
            print("Error: Please enter a valid number.")


def get_computer_donation(computer, donations_last_round):
    # convert donations_last_round to string
    donations_last_round_str = str(donations_last_round)
    print(f"index {computer['index']} is thinking...")
    """Gets the computer's donation"""
    if computer["coins"] <= 0:
        return 0  # Cannot donate anymore
    # The computer donates an amount based on agent's decision
    max_donation = computer["coins"]
    donation_amount = Agent_array[int(computer["index"]) - 1].run(
        f"you are {computer['name']}, you have {max_donation} coins, in last round, the donation status is {donations_last_round_str}, now, please, donate coins, output only the donation amount number without any explanation and nothing else"
    )

    #  remove chars in donation_amount to get number only
    donation_amount = "".join(filter(str.isdigit, donation_amount))
    return int(donation_amount)


def run_game(num_computers):
    """Runs the coin donation game"""
    participants = []
    start_coins = 100

    # Initialize player
    participants.append(
        {"name": "Player", "index": "1", "coins": start_coins, "is_player": True}
    )

    # Initialize computers
    for i in range(num_computers):
        participants.append(
            {
                "name": f"Computer {i+1}",
                "index": f"{i+1}",
                "coins": start_coins,
                "is_player": False,
            }
        )

    round_number = 1
    donations_last_round = {}
    while True:
        print(f"\n=============== Round {round_number} Begins ===============")

        # --- Check if the game should end before the round starts ---
        active_participants = [p for p in participants if p["coins"] > 0]
        if len(active_participants) <= 1:
            print("\n--- Game Over ---")
            if len(active_participants) == 1:
                print(f"Only {active_participants[0]['name']} remains!")
                print(f"{active_participants[0]['name']} is the final winner!")
            else:
                # This situation can occur if two players are eliminated simultaneously in the last round
                print("Everyone is eliminated! No winner.")
            print_participants_status(participants)  # Display final status
            break  # End the main game loop

        # Print status at the beginning of the round
        print_participants_status(participants)

        donations_this_round = {}
        # The participants_in_round list is now active_participants
        participants_in_round = active_participants

        # --- Get donations (only request from active players) ---
        for p in participants_in_round:
            donation = 0
            if p["is_player"]:
                donation = get_player_donation(p)
            else:
                print(f"{p['name']} is thinking...")
                time.sleep(0.5)  # Simulate computer thinking
                donation = get_computer_donation(p, donations_last_round)
                print(f"{p['name']} decides to donate {donation}")

            donations_this_round[p["name"]] = donation
        time.sleep(0.5)  # Simulate computer thinking
        # If no one can donate this round (unlikely to happen), end the game
        if not donations_this_round:
            print("\nError: No one donated this round, game ended unexpectedly!")
            break

        print("\n--- Round Donation Settlement ---")
        donations_last_round = (
            donations_this_round.copy()
        )  # Backup this round's donations
        for name, donation_amount in donations_this_round.items():
            # print(f"{name} donated: {donation_amount}") # Computer's donation is already printed when obtained, player's is self-inputted
            # Actually deduct the donated coins here
            for p in participants:
                if p["name"] == name:
                    p["coins"] -= donation_amount
                    break  # If found, break the inner loop

        # --- Find the person who donated the least and penalize them ---
        if donations_this_round:  # Ensure someone has donated
            # Find the donation amounts of those who participated in this round's donations
            valid_donations = {
                name: amount
                for name, amount in donations_this_round.items()
                if name in [p["name"] for p in participants_in_round]
            }

            if valid_donations:  # Ensure there are valid donors (people with coins > 0)
                min_donation = min(valid_donations.values())
                losers = [
                    name
                    for name, donation_amount in valid_donations.items()
                    if donation_amount == min_donation
                ]

                print(f"\nMinimum donation this round: {min_donation}")
                if len(losers) > 0:
                    print(
                        "Penalty! The following participants will have an additional 10 coins deducted:"
                    )
                    for loser_name in losers:
                        print(f"- {loser_name}")
                        # Find the corresponding participant and deduct coins
                        for p in participants:
                            if p["name"] == loser_name:
                                p["coins"] -= 10
                                break
                # else: # This else should theoretically not be triggered, as there will always be a minimum value
                #    print("No one was penalized this round.")
            else:
                print("No valid donors this round for comparison.")

        # --- Check if the game should end after this round ---
        active_participants_after_round = [p for p in participants if p["coins"] > 0]
        if len(active_participants_after_round) <= 1:
            print("\n--- Game Over ---")
            # Optionally print who was eliminated this round
            eliminated_this_round = []
            current_active_names = {p["name"] for p in active_participants_after_round}
            for p_start in (
                participants_in_round
            ):  # Check players who were active at the start but are no longer active
                if p_start["name"] not in current_active_names:
                    eliminated_this_round.append(p_start["name"])

            if eliminated_this_round:
                print(
                    "Players who ran out of coins this round:",
                    ", ".join(eliminated_this_round),
                )

            if len(active_participants_after_round) == 1:
                print(f"\nOnly {active_participants_after_round[0]['name']} remains!")
                print(
                    f"{active_participants_after_round[0]['name']} is the final winner!"
                )
            else:
                print("\nEveryone is eliminated! No winner.")
            print_participants_status(participants)  # Display final status
            break  # End the main game loop

        # --- Prepare for the next round ---
        round_number += 1
        # time.sleep(1) # This pause can be removed or kept


# --- Game Start ---
if __name__ == "__main__":
    print(
        "    ▗▖ ▗▄▖ ▗▖ ▗▖▗▄▄▄▖▗▄▄▖      ▗▄▄▖ ▗▄▖ ▗▖  ▗▖▗▄▄▄▖    ▗▖  ▗▖    ▗▄▄▄▖ ▗▄▄▖▗▄▄▄▖▗▖ ▗▖"
    )
    print(
        "    ▐▌▐▌ ▐▌▐▌▗▞▘▐▌   ▐▌ ▐▌    ▐▌   ▐▌ ▐▌▐▛▚▞▜▌▐▌        ▝▚▞▘       █  ▐▌   ▐▌   ▐▌▗▞▘"
    )
    print(
        "    ▐▌▐▌ ▐▌▐▛▚▖ ▐▛▀▀▘▐▛▀▚▖    ▐▌▝▜▌▐▛▀▜▌▐▌  ▐▌▐▛▀▀▘      ▐▌        █   ▝▀▚▖▐▛▀▀▘▐▛▚▖ "
    )
    print(
        " ▗▄▄▞▘▝▚▄▞▘▐▌ ▐▌▐▙▄▄▖▐▌ ▐▌    ▝▚▄▞▘▐▌ ▐▌▐▌  ▐▌▐▙▄▄▖    ▗▞▘▝▚▖    ▗▄█▄▖▗▄▄▞▘▐▙▄▄▖▐▌ ▐▌"
    )
    print()

    print("\nWelcome to the Coin Donation Game!")
    print("=========== How to Play ===============")
    print("1. In this game, each player starts with 100 coins.")
    print("2. In each round, each player must donate at least one coin to the bank.")
    print(
        "3. The player who donates the least coins to the bank will have to donate an extra 10 coins as punishment."
    )
    print("4. If a player runs out of coins, they lose the game.")
    print("5. The last player with coins left wins the game.")
    print("=========== Copy Right ===============")
    print(
        "This game is designed by Joker Game (www.thejokergame.com) and authorized to Isek to use this game as demo, all rights reserved."
    )
    print()
    while True:
        try:
            # Print("This game is ")
            num_cpu = int(
                input("Please enter the number of computer players (e.g., 3): ")
            )
            if num_cpu >= 0:
                break
            else:
                print("Number of computers cannot be negative.")
        except ValueError:
            print("Please enter a valid number.")

    run_game(num_cpu)
    print("\nGame simulation finished.")
