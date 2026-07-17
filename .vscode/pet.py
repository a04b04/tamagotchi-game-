import random


class Pet:
    def __init__(self):
        self.hunger = 60
        self.happiness = 60
        self.energy = 60
        self.cleanliness = 60

        self.alive = True

    def feed(self):
        self.hunger += 5

        if self.hunger > 100:
            self.hunger = 100

    def play(self):
        self.happiness += 25
        self.energy -= 5

        if self.happiness > 100:
            self.happiness = 100

        if self.energy < 0:
            self.energy = 0

    def clean(self):
        self.cleanliness += 5

        if self.cleanliness > 100:
            self.cleanliness = 100

    def sleep(self):
        self.energy += 5

        if self.energy > 100:
            self.energy = 100

    def decrease_stats(self):
        stats = [
            "hunger",
            "happiness",
            "energy",
            "cleanliness"
        ]

        random_index = random.randint(0, len(stats) - 1)
        stat_to_decrease = stats[random_index]

        decrease_amount = random.randint(1, 20)

        current_value = getattr(self, stat_to_decrease)
        new_value = current_value - decrease_amount

        if new_value < 0:
            new_value = 0

        setattr(self, stat_to_decrease, new_value)

    def check_alive(self):
        if (
            self.hunger <= 0
            or self.happiness <= 0
            or self.energy <= 0
            or self.cleanliness <= 0
        ):
            self.alive = False