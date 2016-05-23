class ShippingMethod(object):
    ref = None
    _data = None

    def __unicode__(self):
        return self.ref

    def calculate(self):
        pass

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

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
