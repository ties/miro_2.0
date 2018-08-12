from collections import OrderedDict
from app.database import Base


class ResourceCertificate(Base):
    __tablename__ = 'resource_certificate'

    def asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            if getattr(self, key) == None:
                result[key] = "None"

            else:
                if key == "asn_ranges":
                    hurr = getattr(self, key)
                    if hurr:
                        rngs = []
                        for num_range in hurr:
                            d = {'lower':num_range.lower, 'upper':num_range.upper}
                            rngs.append(d)
                        result[key] = rngs
                else:
                    result[key] = getattr(self, key)
        return result


class Roa(Base):
    __tablename__ = 'roa'

    def asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        #result['day'] = result['day'].strftime('%Y-%m-%d')
        return result


class Manifest(Base):
    __tablename__ = 'manifest'

    def asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result


class Crl(Base):
    __tablename__ = 'crl'

    def asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result

class CertificateTree(Base):
    __tablename__ = 'certificate_tree'

    def asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result
