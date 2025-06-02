# osu-db
For Version 20250107 and below
Tested on DB Version: 20250401

data from https://github.com/ppy/osu/wiki/Legacy-database-file-structure

# Usage
```Python
# Usage In This File
if __name__ == "__main__":
    db_data = OsuDBReader.read_db("osu!.db")

# Usage OutSide
from osudb import OsuDBreader
if __name__ == "__main__":
    db_data = OsuDBReader.read_db("osu!.db")
```
