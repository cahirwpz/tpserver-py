import sys

# Have to add atlas to the path
sys.path.append("Atlas-Python")

from config import *
from core import CoreServer, AnonymousClient

from atlas.transport.connection import args2address

if __name__=="__main__":
    s = CoreServer("Thousand Parsec Interactive Server, Version: " + Version, args2address(sys.argv), AnonymousClient)
    s.loop()
