from itertools import groupby

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
        assert not (qt < 5 and mm < 0)
        # if qt < 5 and mm < 0:# or not ss >= 0:
        #     pass #print row['PLAY_ID']

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
        new_secs = 15*60 - (mm*60 + ss)
        mm = new_secs / 60
        ss = new_secs % 60

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

def find_unordered_times(rows):
    for i,row in enumerate(rows):
        if i == 0:
            continue
        prev_row = rows[i-1]
        if prev_row['GAME_ID'] != row['GAME_ID']:
            continue
        if prev_row['QTR'] != row['QTR']:
            continue
        if int(row['MIN']) > int(prev_row['MIN']):
            print row['PLAY_ID']

def fix_unordered_times(rows, bad_ids):
    pass

def clean():
    FIXED_BAD_KICKOFF_TIMES = [1150, 1972, 3462, 3104, 5403, 6397, 12819, 12991, 13987, 13649, 18296, 22758, 25167, 26006, 27038, 26853, 28034, 30892, 33210, 38748, 38062, 40231, 44014, 45541, 46583, 49904, 52141, 54137, 54324, 54325, 54326, 53170, 56052, 56053, 58168, 59311, 60287, 63972, 65134, 64964, 68625, 67755, 74794, 76718, 79728, 82593, 83078, 83699, 89464, 94945, 95140, 94123, 98939, 105518, 105169, 104834, 116940, 117963, 117964, 117965, 121209, 123173, 125637, 126120, 132731, 134711, 139601, 140257, 144304, 150614, 154233, 153586, 155116, 153225, 159798, 163559, 167795, 173059, 172887, 175015, 179194, 185498, 199391, 201766, 204555, 206326, 209951, 210290, 212075, 213108, 217233, 216903, 230948, 232636, 231447, 237309, 236979, 240085, 240430, 243704, 247188, 250272, 252702, 253028, 255214, 259483, 260749, 261254, 263861, 265013, 269116, 271171, 274074, 274568, 279761, 278635, 290232, 288790, 293569, 293727, 296544, 298158, 306900, 309766, 308653, 312054, 322155, 321828, 326340, 326987, 332185, 334933, 336899, 340083, 342355, 345911, 347366, 352586, 354152, 353796, 356161, 358849, 361977, 361632, 363160, 364516, 366514, 368314, 372137, 375199, 376832, 378785, 389231, 390900, 400348, 405595, 403984, 406634, 410232, 413327, 415794, 418449, 421091, 422701, 426535, 428709, 430200, 435921, 435717, 435361, 438626, 443119, 443451, 445939, 446125, 448090, 453033, 453342, 454415, 453851, 454044, 455942, 457761, 459894, 458862, 462890, 465850, 466868]
    UNORDERED_TIMES = [3465, 3474, 3492, 3534, 3249, 5308, 10560, 14075, 17237, 17241, 16957, 18810, 20737, 21854, 24036, 24038, 24040, 24663, 25608, 27598, 29984, 33359, 38907, 38393, 47688, 57633, 57636, 62621, 65546, 67989, 67262, 67401, 68197, 72373, 75834, 82281, 83222, 83701, 83938, 86096, 86103, 86335, 88412, 87709, 89619, 89859, 90578, 91232, 93083, 93084, 93131, 93292, 96568, 96566, 97038, 96259, 103701, 109221, 108688, 114439, 115620, 117910, 117626, 117629, 121769, 121162, 127831, 127837, 130262, 138614, 143137, 142241, 142285, 141733, 143378, 143422, 143460, 147357, 147370, 147397, 147411, 147452, 147454, 147031, 147193, 148716, 154651, 153899, 155743, 157546, 158332, 158733, 158763, 159876, 160598, 170434, 172982, 177255, 179188, 178123, 182121, 182155, 184689, 184937, 188284, 188692, 195586, 195205, 197960, 198110, 202546, 205178, 204861, 207361, 209119, 210780, 209316, 209395, 209149, 209239, 212516, 213272, 214168, 213350, 214941, 216451, 215429, 218505, 220490, 221406, 221452, 221611, 222646, 223103, 223035, 225566, 224504, 224537, 228450, 229442, 231030, 232163, 232203, 231636, 232530, 235167, 235171, 235992, 240089, 240243, 239418, 239904, 240728, 241052, 241638, 241218, 253277, 256930, 256928, 255827, 259620, 262057, 261221, 263300, 263535, 266569, 269065, 269068, 269868, 270675, 275129, 275160, 276329, 278781, 282316, 285984, 284431, 284174, 288386, 293639, 294510, 298796, 301865, 307929, 309034, 308635, 308638, 310631, 311751, 313714, 313787, 319239, 322230, 322643, 322056, 323994, 325132, 324658, 333237, 334447, 337056, 339279, 337339, 339277, 337113, 340351, 343078, 343083, 341795, 348413, 348787, 349003, 349825, 348857, 348958, 351436, 352573, 352350, 354028, 356063, 356795, 357644, 357192, 357199, 356674, 356748, 356756, 358380, 360016, 360038, 359567, 359333, 360179, 360277, 360285, 360781, 362094, 360969, 360406, 360410, 363300, 363303, 364649, 365472, 366272, 366600, 366608, 366655, 367846, 367895, 367676, 368704, 369186, 368940, 370867, 372482, 374245, 374016, 374020, 374920, 377203, 377848, 378545, 378694, 380422, 382696, 380663, 383392, 383403, 384985, 386107, 386626, 387268, 388748, 388007, 388511, 387633, 388206, 388246, 390015, 392141, 392236, 390302, 390307, 390309, 390316, 391155, 392933, 393631, 395041, 395074, 395181, 397142, 396857, 396586, 398267, 397774, 398665, 400951, 402037, 406022, 405324, 404194, 404906, 406442, 407224, 408298, 408300, 408302, 408658, 408539, 408924, 408954, 408981, 410352, 409292, 410804, 410564, 410591, 411650, 413845, 414791, 415776, 416149, 416162, 416169, 416180, 416192, 416202, 416208, 416237, 416241, 416255, 416454, 418342, 417172, 418456, 418460, 418471, 418477, 418485, 418490, 418500, 418505, 418510, 418514, 418519, 418525, 420459, 423560, 424206, 424372, 425920, 427851, 428480, 428857, 430860, 433388, 433386, 436589, 436248, 436752, 438291, 440581, 442124, 442164, 442175, 442178, 442181, 445010, 447534, 447618, 448167, 451111, 451191, 454100, 454752, 454875, 457929, 457931, 458739, 458740, 458743, 458751, 458772, 458787, 458800, 458816, 458818, 458821, 458827, 458830, 458834, 458840, 458850, 458860, 464027, 464534, 465508, 467883, 471272, 471370]

    # def add_drive_id():
    xs = load('nflplays.csv')
    ys = sorted(xs, key=lambda row: (row["GAME_ID"], int(row["PLAY_ID"])))
    ys = fix_unordered_times(ys, UNORDERED_TIMES)
    find_bad_times(ys)
    # games, game_keys = group_by_game(ys)
    # assert_games_sorted_by_time(games)

    # dump('nflplays2.csv', ys)
