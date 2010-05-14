#!/usr/bin/env python

class SingletonClass( type ):#{{{
    def __call__( cls ):
        if getattr( cls, '__instance__', None ) is None:
            instance = cls.__new__( cls )
            instance.__init__( )
            cls.__instance__ = instance
        return cls.__instance__
#}}}

__all__ = [ 'SingletonClass' ]
