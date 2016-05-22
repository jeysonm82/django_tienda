class ShippingMethod(object):
    ref = None
    data = None
    def __unicode__(self):
        return self.ref

    def calculate(self):
        pass

class ShippingMethodRegister(object):
    _reg = {}

    @classmethod
    def register(cls, shipping):
        cls._reg[shipping.ref] = shipping

    @classmethod
    def unregister(cls, shipping):
        del cls._reg[shipping.ref]

    @classmethod
    def get(cls, ref):
        return cls._reg[ref]

    @classmethod
    def all(cls):
        return cls._reg.values()
