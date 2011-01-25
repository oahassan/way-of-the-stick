class InputNode:
    
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.branches = {}
    
    def __str__(self):
        return "key: " + str(self.key) + " value: " + str(self.value)
    
    def add_node(self, key):
    
        if key in self.branches:
            return self.branches[key]
        else:
            new_node = InputNode(key)
            self.branches[key] = new_node
            
            return new_node
    
    def delete_branches(self, key_sequence):
        
        for i in range(len(key_sequence)):
            key = key_sequence[i]
            node = None
            
            if key in self.branches:
                node = self.branches[key]
            
                new_sequence = [key_sequence[j] for j in range(len(key_sequence)) if j != i]
            
                node.delete_branches(new_sequence)
                
                del self.branches[key]
    
    def delete_value(self, key_sequence):
        
        for i in range(len(key_sequence)):
            key = key_sequence[i]
            node = None
            
            if key in self.branches:
                node = self.branches[key]
            
                new_sequence = [key_sequence[j] for j in range(len(key_sequence)) if j != i]
            
            if len(new_sequence) == 0:
                node.value = None
            else:
                node.delete_value(new_sequence)
    
    def get_node(self, key_sequence):
        return self._get_node(key_sequence)
    
    def _get_node(self, key_sequence, start_index=0):
        
        for i in range(start_index, len(key_sequence)):
            key = key_sequence[i]
            
            if key in self.branches:
                node = self.branches[key]
                
                if start_index == len(key_sequence) - 1:
                    return node
                else:
                    return node._get_node(key_sequence, start_index + 1)
            
            else:
                return None
    
    def get_value(self, key_sequence):
        
        return self.get_node(key_sequence).value

class InputTree(InputNode):
    
    def add_branches(self, key_sequence, value, previous_node = None):
        
        for i in range(len(key_sequence)):
            key = key_sequence[i]
            node = None
            
            if previous_node == None:
                node = self.add_node(key)
            else:
                node = previous_node.add_node(key)
            
            new_sequence = [key_sequence[j] for j in range(len(key_sequence)) if j != i]
            if len(new_sequence) == 0:
                node.value = value
            
            else:
                self.add_branches(new_sequence, value, node)
    
    def __str__(self):
        return_string = ""
        
        for key, node in self.branches.iteritems():
            return_string += self.write_branch(node, "")
        
        return return_string
    
    def write_branch(self, node, tabs):
        return_string = "\n" + tabs + str(node)
        tabs += "    "
        
        for key, branch_node in node.branches.iteritems():
            return_string += self.write_branch(branch_node, tabs)
        
        return return_string

if __name__ == "__main__":
    tree = InputTree()

    tree.add_branches((1,2,3), "booyah")
    tree.add_branches((2,3), "two")
    
    print(tree)
    print(tree.get_node((2,3)))
    print(tree.get_node((3,2)))
    print(tree.get_value((3,1,2)))
    print(tree.get_value((2,1)))
    
    tree.delete_value((2,3))
    print(tree.get_value((2,3)))
    print(tree.get_value((3,2)))
    
    tree.delete_branches((1,2))
    print(tree)










