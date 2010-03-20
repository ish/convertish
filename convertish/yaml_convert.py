

from datetime import date

from convertish.convert import BaseConverter, ConvertError

import logging
log = logging.getLogger(__name__)

class YAMLConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        items = []
        for name, attr in schema.attrs:
            log.info('checking name, attr %s, %s'%( name, attr))
            items.append( (name, converter.from_type( attr, data[name], converter,
                                             k=k+[name]), attr) )
        for key, value, attr in items:
            log.info('looping on key, value, schema %s, %s %s'%( key, value, attr))
            if isinstance(attr, schemaish.Structure):
                return '[%s]\n%s'%(key, value)
            else:
                return '%s = %s'%(key, value)


    def to_type(self, schema, data, converter, k):
        pass


class SecondLevelStructureToIniConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        items = []
        for name, attr in schema.attrs:
            log.info('2. checking name, attr %s, %s'%( name, attr))
            items.append( (name, converter.from_type( attr, data[name], converter,
                                             k=k+[name])) )
        for key, value in items:
            log.info('2. looping on key, value, schema %s, %s %s'%( key, value, attr))
            return '%s = %s'%(key, value)


    def to_type(self, schema, data, converter, k):
        pass

