import unittest
import player
import mathfuncs

class AttackTests(unittest.TestCase):
    def test_add_damage(self):
        point_damage = player.Attack.PointDamage()
        
        point_damage.set_last_relative_position((0,0))
        point_damage.cache_new_damage((0,10))
        
        self.assertTrue(point_damage.damage == 10, "Cached damage is incorrect: " + str(point_damage.damage))
        
    def test_set_last_relative_position(self):
        point_damage = player.Attack.PointDamage()
        
        point_damage.set_last_relative_position((0,0))
        
        self.assertTrue(point_damage.last_relative_position[0] == 0, "Last relative position is incorrect: " + str(point_damage.last_relative_position))
        self.assertTrue(point_damage.last_relative_position[0] == 0, "Last relative position is incorrect: " + str(point_damage.last_relative_position))
