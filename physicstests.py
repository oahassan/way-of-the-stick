import unittest
import physics
import stick

class ModelCollisionTests(unittest.TestCase):
    def setUp(self):
        self.model1 = physics.Model((0,0))
        self.model1.init_stick_data()
        self.model2 = physics.Model((0,0))
        self.model2.init_stick_data()
        
        self.modelCollision = physics.ModelCollision(self.model1, self.model2)
    
    def test_get_model_hitboxes(self):
        self.assertRaises(Exception,
                          self.modelCollision.get_model_hitboxes,
                          None)
        self.assertRaises(KeyError,
                          self.modelCollision.get_model_hitboxes,
                          physics.Model((0,0)))
        self.assertTrue(len(self.modelCollision.get_model_hitboxes(self.model1)) > 0,
                        "no hitboxes added for model1")
        self.assertTrue(len(self.modelCollision.get_model_hitboxes(self.model2)) > 0,
                        "no hitboxes added for model2")

