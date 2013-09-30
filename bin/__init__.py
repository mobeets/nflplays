import csv
from itertools import groupby

COLNAMES = ["PLAY_ID", "GAME_ID", "QTR", "MIN", "SEC", "OFF", "DEF", "DOWN", "YARDS_TO_FIRST", "YARDS_TO_GOAL", "DESCRIPTION", "OFF_SCORE", "DEF_SCORE", "SEASON", "YEAR", "MONTH", "DAY", "HOME_TEAM", "AWAY_TEAM", "PLAY_TYPE"]
NEW_COLNAMES = ["PLAY_ID", "GAME_ID", "QTR", "MIN", "SEC", "OFF", "DEF", "DOWN", "YARDS_TO_FIRST", "YARDS_TO_GOAL", "DESCRIPTION", "OFF_SCORE", "DEF_SCORE", "SEASON", "YEAR", "MONTH", "DAY", "HOME_TEAM", "AWAY_TEAM", "PLAY_TYPE"]

def load(infile):
    with open(infile, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, fieldnames=COLNAMES, delimiter='\t', quotechar='"')
        colnames = csvreader.next()
        assert set(colnames.values()) == set(COLNAMES)
        return list(csvreader)

def dump(outfile, rows):
    if not rows:
        return
    with open(outfile, 'wb') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=COLNAMES, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        csvwriter.writeheader()
        for row in rows:
            csvwriter.writerow(row)

def group_by_keyfcn(rows, keyfcn):
    groups = []
    uniquekeys = []
    for k, g in groupby(rows, keyfcn):
        groups.append(list(g))    # Store group iterator as a list
        uniquekeys.append(k)
    return groups, uniquekeys

def group_by_game(rows):
    return group_by_keyfcn(rows, lambda row: row["GAME_ID"])

def fix_game_times(rows):
    if not rows:
        return

    def fixed_time(row):
        mm = int(row["MIN"])
        ss = int(row["SEC"])
        qt = int(row["QTR"])
        if qt < 5 and mm < 0:# or not ss >= 0:
            pass #print row['PLAY_ID']

        if qt < 5 and (mm > 0 or ss > 0):
            secs = mm*60 + ss
            new_secs = 60*60 - secs
        elif qt == 5:
            secs = (-mm - 1)*60 + (60 - ss)
            new_secs = secs if (-mm > 0 or ss > 0) else 0
            # mm = 15 - mm - 1
            # secs = mm*-60 + ss
            # new_secs = 60*60 + secs
        else:
            new_secs = mm*60 + ss
        mm = new_secs / 60
        ss = new_secs % 60

        # times are relative to quarter, counting up
        mm = mm if (qt == 1 or qt > 4) else mm % ((qt-1) * 15)
        row["MIN"] = mm
        row["SEC"] = ss

        return row

    return [fixed_time(row) for row in rows]

def assert_games_sorted_by_time(games):
    for game in games:
        qt_mm_ss = lambda row: (int(row["QTR"]), int(row["MIN"]), int(row["SEC"]), int(row["PLAY_ID"]))
        game2 = sorted(game, key=qt_mm_ss)
        if game != game2:
            x = [(i, a, b) for i, (a,b) in enumerate(zip(game, game2)) if a!=b][0]
            1/0
        assert game == game2

"""
* add game_play_id (since play_id is currently primary key for some reason)
* add game_drive_id
"""

def fix_kickoff_times(rows, bad_ids):
    new_rows = []
    for j in range(len(rows)):
        if j in bad_ids:
            bad_id = j
            i = 1
            row = rows[bad_id-i]
            while int(row['PLAY_ID']) != bad_id:
                i += 1
                row = rows[bad_id - i]
            prev_row = rows[bad_id - i - 1]

            if row['QTR'] == '1' and prev_row['GAME_ID'] != row['GAME_ID']:
                # set to have opening kickoff time of 0:00
                row['MIN'] = '0'
                row['SEC'] = '0'
                rows[bad_id - i] = row
            elif int(prev_row['PLAY_ID']) in bad_ids:
                # set to corrected time of previous row
                row['MIN'] = prev_row['MIN']
                row['SEC'] = prev_row['SEC']
                rows[bad_id - i] = row
            else:
                print bad_id
        new_rows.append(rows[j])
    return new_rows

# def add_drive_id():
WRONG_TIMES = [1150, 1972, 3462, 3104, 5403, 6397, 12819, 12991, 13987, 13649, 18296, 22758, 25167, 26006, 27038, 26853, 28034, 30892, 33210, 38748, 38062, 40231, 44014, 45541, 46583, 49904, 52141, 54137, 54324, 54325, 54326, 53170, 56052, 56053, 58168, 59311, 60287, 63972, 65134, 64964, 68625, 67755, 74794, 76718, 79728, 82593, 83078, 83699, 89464, 94945, 95140, 94123, 98939, 105518, 105169, 104834, 116940, 117963, 117964, 117965, 121209, 123173, 125637, 126120, 132731, 134711, 139601, 140257, 144304, 150614, 154233, 153586, 155116, 153225, 159798, 163559, 167795, 173059, 172887, 175015, 179194, 185498, 199391, 201766, 204555, 206326, 209951, 210290, 212075, 213108, 217233, 216903, 230948, 232636, 231447, 237309, 236979, 240085, 240430, 243704, 247188, 250272, 252702, 253028, 255214, 259483, 260749, 261254, 263861, 265013, 269116, 271171, 274074, 274568, 279761, 278635, 290232, 288790, 293569, 293727, 296544, 298158, 306900, 309766, 308653, 312054, 322155, 321828, 326340, 326987, 332185, 334933, 336899, 340083, 342355, 345911, 347366, 352586, 354152, 353796, 356161, 358849, 361977, 361632, 363160, 364516, 366514, 368314, 372137, 375199, 376832, 378785, 389231, 390900, 400348, 405595, 403984, 406634, 410232, 413327, 415794, 418449, 421091, 422701, 426535, 428709, 430200, 435921, 435717, 435361, 438626, 443119, 443451, 445939, 446125, 448090, 453033, 453342, 454415, 453851, 454044, 455942, 457761, 459894, 458862, 462890, 465850, 466868]
xs = load('nflplays.csv')
xs = fix_kickoff_times(xs, WRONG_TIMES)
dump('nflplays2.csv', xs)

# ys = sorted(xs, key=lambda row: (row["GAME_ID"], int(row["PLAY_ID"])))
# ys = fix_game_times(ys)
# games, game_keys = group_by_game(ys)
# assert_games_sorted_by_time(games)
# dump('nflplays2.csv', ys)
