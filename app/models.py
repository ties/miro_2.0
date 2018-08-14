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
                elif key == "serial_nr":
                    result[key] = str(getattr(self, key))
                else:
                    result[key] = getattr(self, key)
        return result


class Roa(Base):
    __tablename__ = 'roa'

    def asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            if getattr(self, key) == None:
                result[key] = "None"
            else:
                result[key] = getattr(self, key)

            if key == 'prefixes':
                new = []
                res = result[key]
                res = res.replace('"', '').replace('{','').replace('}','')
                res = res.replace('(', '').replace(')','')
                i = 0
                res = res.split(',')
                while i < len(res):
                    new.append(res[i]+'_'+res[i+1])
                    i += 2
                result['prefixes'] = new
        #result['day'] = result['day'].strftime('%Y-%m-%d')
        return result


class Manifest(Base):
    __tablename__ = 'manifest'

    def asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            if getattr(self, key) == None:
                result[key] = "None"
            else:
                result[key] = getattr(self, key)
        return result


class Crl(Base):
    __tablename__ = 'crl'

    def asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            if getattr(self, key) == None:
                result[key] = "None"
            else:
                result[key] = getattr(self, key)
        return result

class CertificateTree(Base):
    __tablename__ = 'certificate_tree'

    def asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result
