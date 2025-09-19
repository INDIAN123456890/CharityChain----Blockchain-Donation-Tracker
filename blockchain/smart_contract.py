class CharityContract:
    def __init__(self, initial_balance=100):
        self.initial_balance = initial_balance
        self.donations = {}          # donor -> total donated
        self.charity_balances = {}   # charity -> total received
        self.donor_balances = {}     # donor -> remaining balance
        self.events = []             # logs

    def donate(self, donor, charity, amount):
        if amount <= 0:
            raise ValueError("Donation must be > 0")

        # initialize donor balance if first time
        if donor not in self.donor_balances:
            self.donor_balances[donor] = self.initial_balance

        if self.donor_balances[donor] < amount:
            raise ValueError("Insufficient funds for donor")

        # Deduct from donor, add to charity
        self.donor_balances[donor] -= amount
        self.donations[donor] = self.donations.get(donor, 0) + amount
        self.charity_balances[charity] = self.charity_balances.get(charity, 0) + amount

        # Log donation event
        event = {"event": "DonationMade", "donor": donor, "charity": charity, "amount": amount}
        self.events.append(event)
        return event

    def withdraw(self, charity):
        balance = self.charity_balances.get(charity, 0)
        if balance == 0:
            raise ValueError("No funds available to withdraw")
        self.charity_balances[charity] = 0

        event = {"event": "Withdrawal", "charity": charity, "amount": balance}
        self.events.append(event)
        return event
