class Proxy:
    a = 0
    class Nothing:
        pass

    def __init__(self, element):
        self._element = element

    def __getattribute__(self, attribute):
        try:
            value = super(Proxy, self).__getattribute__(attribute) 
        except AttributeError:
            value = getattr(self._element, attribute, Proxy.Nothing())
            
        if not isinstance(value, Proxy.Nothing):
            return value
        else:
            raise AttributeError("%s is not an attribute of %s or %s" % (attribute, str(self), str(self._element)))

class A:
    b = 0


proxy_of_a = Proxy(A())
print(proxy_of_a.a)
print(proxy_of_a.b)
print(proxy_of_a.c)