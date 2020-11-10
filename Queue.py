class Queue:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if len(self.items) > 0:
            result = self.items[0]
            self.items = self.items[1::]
            return result
        else:
            return None

    def peek(self):
        if len(self.items) > 0:
            return self.items[0]
        else:
            return None