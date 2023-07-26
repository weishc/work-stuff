class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None
        

class DoublyLinkedList:
    def __init__(self, value):
        new_node = Node(value)
        self.head = new_node
        self.tail = new_node
        self.length = 1

    def print_list(self):
        temp = self.head
        while temp is not None:
            print (temp.value)
            temp = temp.next
        
    
    def make_empty(self):
        self.head = None
        self.tail = None
        self.length = 0
        
    def append(self, value):
        new_node = Node(value)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.length += 1
        return True

    def pop(self):
        if self.length == 0:
            return None
        temp = self.tail
        if self.length == 1:
            self.head = None
            self.tail = None 
        else:       
            self.tail = self.tail.prev
            self.tail.next = None
            temp.prev = None
        self.length -= 1
        return temp
    
    def prepend(self, value):
        new_node = Node(value)
        self.length += 1
        if not self.head:
            self.head = new_node
            self.tail = new_node
            return True
        new_node.next = self.head
        self.head.prev = new_node
        self.head = new_node
        return True
    
    def pop_first(self):
        if self.length == 0:
            return None
        temp = self.head
        if self.length == 1:
            self.head = None
            self.tail = None
        else:
            self.head = self.head.next
            self.head.prev = None
            temp.next = None      
        self.length -= 1
        return temp
    
    def get(self, idx):
        if idx < 0 or idx >= self.length:
            return None
        temp = self.head
        if idx < self.length/2:
            for _ in range(idx):
                temp = temp.next
        else:
            temp = self.tail
            for _ in range(self.length - 1, idx, -1):
                temp = temp.prev  
        return temp
    
    def set_value(self, idx, value):
        temp = self.get(idx)
        if temp:
            temp.value = value
            return True
        return False
    
    def insert(self, idx, value):
        if idx < 0 or idx > self.length:
            return False
        if idx == 0:
            return self.prepend(value)
        if idx == self.length:
            return self.append(value)
        new_node = Node(value)
        before = self.get(idx - 1)
        after = before.next
        new_node.prev = before
        new_node.next = after
        before.next = new_node
        after.prev = new_node
        self.length += 1   
        return True
    
    def remove(self, idx):
        if idx < 0 or idx >= self.length:
            return None
        if idx == 0:
            return self.pop_first()
        if idx == self.length - 1:
            return self.pop()
        temp = self.get(idx - 1)
        temp.next.prev = temp.prev
        temp.prev.next = temp.next
        temp.next = None
        temp.prev = None
        self.length -= 1
        return temp
    