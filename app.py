from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"

def get_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = ranks * 4
    random.shuffle(deck)
    return deck

def card_value(card):
    if card in ['J', 'Q', 'K']:
        return 10
    elif card == 'A':
        return 11
    else:
        return int(card)

def calculate_hand(hand):
    total = sum(card_value(card) for card in hand)
    aces = hand.count('A')
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

@app.route("/", methods=["GET", "POST"])
def index():
    if "deck" not in session or "player_hand" not in session:
        reset_game()

    if request.method == "POST":
        if request.form["action"] == "Hit" and not session.get("game_over"):
            session["player_hand"].append(session["deck"].pop())
            session.modified = True
            if calculate_hand(session["player_hand"]) > 21:
                session["message"] = "You busted. Dealer wins."
                session["game_over"] = True

        elif request.form["action"] == "Stand":
            while calculate_hand(session["dealer_hand"]) < 17:
                session["dealer_hand"].append(session["deck"].pop())

            player_total = calculate_hand(session["player_hand"])
            dealer_total = calculate_hand(session["dealer_hand"])

            if dealer_total > 21:
                session["message"] = "Dealer busted. You win!"
            elif player_total > dealer_total:
                session["message"] = "You win!"
            elif dealer_total > player_total:
                session["message"] = "Dealer wins!"
            else:
                session["message"] = "Push"
            session["game_over"] = True

    return render_template("index.html", 
        player=session["player_hand"], 
        dealer=session["dealer_hand"] if session["game_over"] else ["??", session["dealer_hand"][1]],
        total=calculate_hand(session["player_hand"]), 
        message=session.get("message", ""), 
        game_over=session.get("game_over", False)
    )

@app.route("/reset")
def reset():
    reset_game()
    return redirect(url_for("index"))

def reset_game():
    session["deck"] = get_deck()
    session["player_hand"] = [session["deck"].pop(), session["deck"].pop()]
    session["dealer_hand"] = [session["deck"].pop(), session["deck"].pop()]
    session["game_over"] = False
    session["message"] = ""

if __name__ == "__main__":
    app.run(debug=True)
