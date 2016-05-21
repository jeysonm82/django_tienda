class ShippingMethod(object):
    pass


class ShippingMethodRegister(object):
    _reg = []

    @classmethod
    def register(cls, shipping):
        cls._reg.append(shipping)

    @classmethod
    def unregister(cls, shipping):
        cls._reg.pop(shipping)
