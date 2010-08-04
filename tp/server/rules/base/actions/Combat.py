#!/usr/bin/env python

import random

class Ship( object ):#{{{
    draw_damage = 0
    win_damage = 0

    def __init__(self):
        self.damage = 0

    def hit(self, hp):
        self.hp -= hp

    def alive(self):    
        return self.hp > 0
#}}}

class Frigate( Ship ):#{{{
    """
    I cause 2 hp of damage on win. I always fire first.
    I move 2 units per turn.
    I have 4 HP
    I can be built in 2 turns.
    I can colonise planets.
    """
    win_damage = 2
    type = 'Frigate'
    def __init__(self):
        Ship.__init__(self)
        self.hp = 4

    def own(self, fleet):
        fleet.frigates.append(self)
#}}}

class Battleship( Ship ):#{{{
    """
    I cause 3 hp of damage on win. 1 HP on draw
    I move 1 units per turn.
    I have 6 HP
    I can be built in 4 turns.
    """
    win_damage = 3
    draw_damage = 1
    type = 'Battleship'

    def __init__(self):
        Ship.__init__(self)
        self.hp = 6

    def own(self, fleet):
        fleet.battleships.append(self)
#}}}

class Scout( Ship ):#{{{
    """
    If I win a match I may escape.
    I move 3 units per turn.
    I have 2 HP
    I can be built in 1 turn.
    """
    type = 'Scout'
    def __init__(self):
        Ship.__init__(self)
        self.hp = 2

    def own(self, fleet):
        fleet.scouts.append(self)
#}}}

class Planet( Ship ):#{{{
    win_damage = 6
    draw_damage = 2

    type = 'Planet'
    def __init__(self):
        Ship.__init__(self)
        self.hp = 12

    def own(self, fleet):
        fleet.planets.append(self)
#}}}

class Fleet( object ):#{{{
    def __init__(self, ships):
        # For scouts, so they can run away.
        self.running = 0

        self.battleships = []
        self.frigates = []
        self.scouts = []
        self.planets = []
        self.ships = ships

        for ship in ships:
            ship.own(self)

    def shake(self):
        """
        I return "Rock", "Paper" or "Scissors"
        """
        return ["Rock", "Paper", "Scissors"][random.randint(0,2)]

    def most_damaged(self, ships):
        dlist = [(ship.hp, ship) for ship in ships if ship.alive()]
        if len(dlist) == 0:
            return None

        dlist.sort()
        return dlist[0][1]

    def hit(self, hp):
        hits = []
        while hp > 0 and self.alive():
            most_damaged = self.most_damaged(self.battleships) \
                or self.most_damaged(self.frigates) \
                or self.most_damaged(self.scouts) \
                or self.most_damaged(self.planets)

            if most_damaged.hp > hp:
                hits.append((hp, most_damaged))
                most_damaged.hit(hp)
                hp = 0
            else:
                hits.append((most_damaged.hp, most_damaged))
                hp -= most_damaged.hp
                most_damaged.hit(most_damaged.hp)
        return hits

    def draw_damage(self):
        return sum([s.draw_damage for s in self.ships if s.alive()])

    def win_damage(self):
        if sum([1 for s in self.ships if s.alive()]) \
            == sum([1 for s in self.scouts if s.alive()]):
            self.running = 1

        return sum([s.win_damage for s in self.ships if s.alive()])

    def alive(self):
        if self.running:
            return False

        return sum([1 for s in self.ships if s.alive()])
#}}}

__all__ = [ 'Ship', 'Frigate', 'Battleship', 'Scout', 'Planet', 'Fleet' ]
