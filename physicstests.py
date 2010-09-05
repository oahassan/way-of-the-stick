import unittest
import physics
import stick

class ModelTests(unittest.TestCase):
    def setUp(self):
        self.model1 = physics.Model((10,10))
        self.model1.init_stick_data()
        
        for point in self.model1.points.values():
            point.pos = (10,20)
        
        self.model1.points[stick.PointNames.HEAD_TOP].pos = (10,10)
    
    def test_get_point_relative_position(self):
        """tests the get_point_relative_position function"""
        expected_head_top_relative_position = (5,0)
        actual_head_top_relative_position = self.model1.get_point_relative_position(stick.PointNames.HEAD_TOP)
        
        self.assertEqual(expected_head_top_relative_position[0], 
                         actual_head_top_relative_position[0],
                         "actual head top position {0} does not match expected head top position {1}".format(str(actual_head_top_relative_position),
                                                                                                               str(expected_head_top_relative_position)))
        self.assertEqual(expected_head_top_relative_position[1], 
                         actual_head_top_relative_position[1],
                         "actual head top position {0} does not match expected head top position {1}".format(str(actual_head_top_relative_position),
                                                                                                               str(expected_head_top_relative_position)))

class ModelCollisionTests(unittest.TestCase):
    def setUp(self):
        self.model1 = physics.Model((0,0))
        self.model1.init_stick_data()
        self.model2 = physics.Model((0,0))
        self.model2.init_stick_data()
        
        self.modelCollision = physics.ModelCollision(self.model1, self.model2)
        
        self.head_model1 = physics.Model((0,0))
        self.head_model1.lines[stick.LineNames.HEAD] = \
            self.model1.lines[stick.LineNames.HEAD]
        self.head_model1.lines[stick.LineNames.HEAD].endPoint1.pos = (0,10)
        
        self.head_model2 = physics.Model((0,0))
        self.head_model2.lines[stick.LineNames.HEAD] = \
            self.model2.lines[stick.LineNames.HEAD]
        self.head_model2.lines[stick.LineNames.HEAD].endPoint1.pos = (0,10)
        
        self.head_model_collision = physics.ModelCollision(self.head_model1, 
                                                         self.head_model2)
    
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
    
    def test_create_hitbox(self):
        model1_head = self.model1.lines[stick.LineNames.HEAD]
        hitbox = physics.Hitbox(self.model1, 
                                model1_head,
                                [model1_head.get_reference_position(),
                                 (model1_head.length,
                                  model1_head.length)])
        self.assertEqual(hitbox.model, self.model1)
        self.assertEqual(hitbox.line, model1_head)
        self.assertEqual(id(hitbox), hitbox.id)
    
    def test_get_colliding_hitboxes(self):
        colliding_hitboxes = self.head_model_collision.get_colliding_hitboxes()
        
        self.assertTrue(len(colliding_hitboxes) > 0, "heads aren't knocking?!")
        self.assertEqual(colliding_hitboxes[0][0].model, self.head_model1)
        self.assertEqual(colliding_hitboxes[0][1][0].model, self.head_model2)
