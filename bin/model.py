import csv

# COLNAMES = ["PLAY_ID", "GAME_ID", "REL_PLAY_ID", "QTR", "MIN", "SEC", "OFF", "DEF", "DOWN", "YARDS_TO_FIRST", "YARDS_TO_GOAL", "DESCRIPTION", "OFF_SCORE", "DEF_SCORE", "SEASON", "YEAR", "MONTH", "DAY", "HOME_TEAM", "AWAY_TEAM", "PLAY_TYPE"]
COLNAMES = ["PLAY_ID", "GAME_ID", "REL_PLAY_ID", "QTR", "MIN", "SEC", "OFF", "DEF", "DRIVE_ID", "DOWN", "YARDS_TO_FIRST", "YARDS_TO_GOAL", "DESCRIPTION", "OFF_SCORE", "DEF_SCORE", "SEASON", "YEAR", "MONTH", "DAY", "HOME_TEAM", "AWAY_TEAM", "PLAY_TYPE"]
NEW_COLNAMES = ["PLAY_ID", "GAME_ID", "REL_PLAY_ID", "QTR", "MIN", "SEC", "OFF", "DEF", "DRIVE_ID", "DOWN", "YARDS_TO_FIRST", "YARDS_TO_GOAL", "DESCRIPTION", "OFF_SCORE", "DEF_SCORE", "SEASON", "YEAR", "MONTH", "DAY", "HOME_TEAM", "AWAY_TEAM", "PLAY_TYPE"]

def load(infile):
    with open(infile, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, fieldnames=COLNAMES, delimiter='\t', quotechar='"')
        colnames = csvreader.next()
        assert all([x in COLNAMES for x in colnames.values()]) and all([x in colnames.values() for x in COLNAMES])
        # assert set(colnames.values()) == set(COLNAMES)
        return list(csvreader)

def dump(outfile, rows):
    if not rows:
        return
    with open(outfile, 'wb') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=NEW_COLNAMES, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        csvwriter.writeheader()
        for row in rows:
            csvwriter.writerow(row)

def load_as_rows(infile):
    return [Row(row) for row in load(infile)]

def dump_as_rows(outfile, rows):
    dump(outfile, [row.dump() for row in rows])

class Row:
    def __init__(self, row):
        self.row = row
        self.date = Date(row)
        self.game = Game(row)
        self.game_state = GameState(row)
        self.play = Play(row)

    def dump(self):
        val1 = [self.play.play_id, self.game.game_id, self.play.rel_play_id, self.game_state.qtr, self.game_state.min, self.game_state.sec, self.play.offense, self.play.defense]
        val2 = [self.play.drive_id, self.play.down, self.play.yds_to_fst, self.play.yds_to_gl, self.play.desc, self.game_state.off_score, self.game_state.def_score]
        val3 = [self.date.season, self.date.year, self.date.month, self.date.day, self.game.home_team, self.game.away_team, self.play.play_type]
        vals = val1 + val2 + val3
        return dict(zip(NEW_COLNAMES, vals))

class Date:
    def __init__(self, row):
        self.season = row['SEASON']
        self.year = row['YEAR']
        self.month = row['MONTH']
        self.day = row['DAY']

class Game:
    def __init__(self, row):
        self.game_id = row['GAME_ID']
        self.home_team = row['HOME_TEAM']
        self.away_team = row['AWAY_TEAM']

    def has_team(self, team_name):
        return team_name.upper() == self.home_team or team_name.upper() == self.away_team

class GameState:
    def __init__(self, row):
        self.qtr = row['QTR']
        self.min = row['MIN']
        self.sec = row['SEC']
        self.off_score = row['OFF_SCORE']
        self.def_score = row['DEF_SCORE']

class Play:
    def __init__(self, row):
        self.play_id = row['PLAY_ID']
        self.offense = row['OFF']
        self.defense = row['DEF']
        self.down = row['DOWN']
        self.yds_to_fst = row['YARDS_TO_FIRST']
        self.yds_to_gl = row['YARDS_TO_GOAL']
        self.desc = row['DESCRIPTION']
        self.play_type = row['PLAY_TYPE']

        self.rel_play_id = row['REL_PLAY_ID']
        self.drive_id = None # row['DRIVE_ID']
