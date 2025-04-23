class Image:
    def __init__(self, id_image, name, description, creator, time_creation, url,  state, size_byte, last_time):
        self.id_image=id_image
        self.name=name
        self.description=description
        self.creator= creator
        self.time_creation=time_creation
        self.url=url
        self.state=state
        self.size_byte=size_byte
        self.last_time= last_time


    def add_image(self, image):
        self.links.append(image)