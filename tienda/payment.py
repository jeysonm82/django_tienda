class PaymentMethod(object):
    name = None
    ref = None

    def __unicode__(self):
        return self.name


class PaymentMethodRegister(object):
    _reg = {}

    @classmethod
    def register(cls, payment):
        cls._reg[payment.ref] = payment

    @classmethod
    def unregister(cls, payment):
        del cls._reg[payment.ref]

    @classmethod
    def get(cls, ref):
        return cls._reg[ref]

    @classmethod
    def all(cls):
        return cls._reg.values()
