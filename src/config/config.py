# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0


# @author Daniel McCoy Stephenson
# @since October 2nd, 2022
class Config:
    def __init__(self):
        self.godMode = False  # Disable god mode
        self.maxTicks = 1000
        self.tickLength = 0.1
        
        # Early-game survival settings
        self.earlyGameGracePeriod = 50  # Number of ticks of protection for player
        self.playerDamageReduction = 0.25  # 25% damage reduction for player during grace period
        # During grace period, other creatures have 75% chance to avoid attacking player
