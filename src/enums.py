import enum

from sprites import Warrior, Mage, Ranger, Enemy


class Class(enum.Enum):
    WARRIOR = enum.auto()
    RANGER = enum.auto()
    MAGE = enum.auto()
    ENEMY = enum.auto()

    def create_new(self, centerpos: tuple[int, int], *groups):
        match self:
            case self.WARRIOR:
                return Warrior(centerpos, *groups)
            case self.RANGER:
                return Ranger(centerpos, *groups)
            case self.MAGE:
                return Mage(centerpos, *groups)
            case self.ENEMY:
                return Enemy(centerpos, *groups)