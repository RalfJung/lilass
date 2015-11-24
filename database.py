import sqlite3
import os.path
from binascii import hexlify, unhexlify
from screen import ScreenSetup, Resolution, RelativeScreenPosition

class InvalidDBFile(Exception):
    pass

class Database:
    def __init__(self, dbfilename):
        self._create = False
        assert(os.path.isdir(os.path.dirname(dbfilename)))
        if not os.path.isfile(dbfilename):
            if os.path.lexists(dbfilename):
                raise Exception("Database must be a file: '%s'" % dbfilename)
            # database will be created on __enter__ because we need a dbconnection for it
            self._create = True
        self._dbfilename = dbfilename
        self._connection = None
    def __enter__(self):
        self._connection = sqlite3.connect(self._dbfilename)
        c = self._c()
        if self._create:
            c.execute("""CREATE TABLE meta (key text, value text, PRIMARY KEY(key))""")
            c.execute("""INSERT INTO meta VALUES ('version', '1')""")
            c.execute("""CREATE TABLE known_configs (edid blob, resinternal text, resexternal text, mode text, ext_is_primary integer, PRIMARY KEY(edid))""")
            # edid in binary format
            # resindernal, resexternal = "1024x768" or NULL if display is off
            # mode: the enum text of screen.RelativeScreenPosition or NULL if one display is off
        else: # check compatibility
            dbversion = int(self._getMeta("version"))
            if dbversion > 1:
                raise InvalidDBFile("Database is too new: Version %d. Please update lilass." % dbversion)
        return self
    def _getMeta(self, key):
        c = self._c()
        c.execute("""SELECT value FROM meta WHERE key=?""", (key,))
        got = c.fetchone()
        if got is None: # to differentiate between the value being NULL and the row being not there
            raise KeyError("""Key "%s" is not in the meta table.""" % key)
        assert c.fetchone() is None # uniqueness
        assert len(got) == 1
        return got[0]
    def putConfig(self, extconn_edid, conf):
        c = self._c()
        b_edid = unhexlify(extconn_edid)
        intres = conf.intResolution.forDatabase() if conf.intResolution else None
        extres = conf.extResolution.forDatabase() if conf.extResolution else None
        mode = conf.relPosition.text if conf.relPosition else None
        extprim = int(conf.extIsPrimary) # False => 0, True => 1
        c.execute("""INSERT OR REPLACE INTO known_configs VALUES (?,?,?,?,?)""", (b_edid, intres, extres, mode, extprim))
    def getConfig(self, extconn_edid):
        c = self._c()
        b_edid = unhexlify(extconn_edid)
        c.execute("""SELECT * FROM known_configs WHERE edid=?""", (b_edid,))
        result = c.fetchone()
        if result is None:
            return None
        assert c.fetchone() is None # uniqueness
        _, intres, extres, mode, extprim = result
        intres = Resolution.fromDatabase(intres) # this method is safe for NULLs
        extres = Resolution.fromDatabase(extres)
        mode = RelativeScreenPosition(mode)
        extprim = bool(extprim) # 0 => False, 1 => True
        return ScreenSetup(intres, extres, mode, extprim)
    def __exit__(self, type, value, tb):
        if self._connection:
            self._connection.commit()
            self._connection.close()
    def _c(self):
        assert(self._connection)
        return self._connection.cursor()
