from model import load_as_rows, dump_as_rows

def filter_rows(rows, fcn):
    new_rows = []
    for row in rows:
        if fcn(row):
            new_rows.append(row)
    return new_rows

filter_team_fcn = lambda team: (lambda row: row.game.has_team(team))
filter_year_fcn = lambda year: (lambda row: row.date.season == str(year))

def output_filtered_team(infile, outfile, team):
    rows = load_as_rows(infile)
    print 'LOADED'
    filter_fcn = filter_team_fcn(team)
    new_rows = filter_rows(rows, filter_fcn)
    print 'FILTERED'
    dump_as_rows(outfile, new_rows)
    print 'FINISHED'

def assert_invertible():
    rows = load_as_rows('nflplays_small.csv')
    print 'LOADED'
    dump_as_rows('nflplays_small_2.csv', rows)
    print 'WRITTEN'
    rows2 = load_as_rows('nflplays_small_2.csv')
    print 'RELOADED'
    for row1, row2 in zip(rows, rows2):
        assert str(row1.dump()) == str(row2.dump())
    print 'FINISHED'

def hist_yds(team='NE'):
    # from numpy import histogram
    import matplotlib.pyplot as plt

    rows = load_as_rows('nflplays.csv')
    rows = filter_rows(rows, filter_year_fcn(2011))

    off_yds = []
    def_yds = []
    for row in rows:
        val = int(row.play.yds_to_gl)
        off_yds.append(val)
        # if row.play.offense == team:
        #     off_yds.append(val)
        # else:
        #     def_yds.append(val)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # ax2 = fig.add_subplot(212)
    ax1.hist(off_yds, range(0, 101, 1))
    # ax2.hist(def_yds, range(0, 101, 5))
    plt.show()

# hist_yds()

def add_rel_play_id():
    rows = load_as_rows('nflplays_old.csv')
    next_play_id = 1
    prev_game_id = None
    seen_game_ids = set()
    for i,row in enumerate(rows):
        if i == 0:
            prev_game_id = None
        else:
            prev_game_id = rows[i-1].game.game_id
            seen_game_ids.add(prev_game_id)
        if prev_game_id and row.game.game_id != prev_game_id:
            next_play_id = 1
            assert row.game.game_id not in seen_game_ids, row.game.game_id
        row.play.rel_play_id = next_play_id
        next_play_id += 1
    dump_as_rows('nflplays.csv', rows)

def fix_off_def():
    rows = load_as_rows('nflplays_old.csv')
    for i, row in enumerate(rows):
        if not row.play.offense.strip():
            if row.play.defense.strip():
                if row.play.defense == row.game.home_team:
                    row.play.offense = row.game.away_team
                elif row.play.defense == row.game.away_team:
                    row.play.offense = row.game.home_team
                else:
                    print 'FUCK'
                    break
            else:
                print '.'
        elif not row.play.defense.strip():
            if row.play.offense.strip():
                if row.play.offense == row.game.home_team:
                    row.play.defense = row.game.away_team
                elif row.play.offense == row.game.away_team:
                    row.play.defense = row.game.home_team
                else:
                    print 'FUCK-2'
                    break
            else:
                print 'FUCK-3'
    dump_as_rows('nflplays.csv', rows)

def check_drives():
    rows = load_as_rows('nflplays_small_2.csv')
    last = False
    for i,row in enumerate(rows):
        if last and int(row.play.down) > 0:
            last = False
            if rows[i-2].play.offense == row.play.offense:
                print row.row
                1/0

        if int(row.play.down) == 0:
            last = True
        # else:
            # last = False

def check_kickoff():
    rows = load_as_rows('nflplays.csv')
    prev_game_id = rows[0].game.game_id
    for row in rows:
        cur_game_id = row.game.game_id
        if prev_game_id != cur_game_id:
            if int(row.play.down) != 0:
                print prev_game_id
        prev_game_id = cur_game_id

def add_drive_id():
    """
    Need to check logic here...

    Note that DOWN is 0 on kicks, and these should not be given a DRIVE_ID
    A DRIVE_ID should change if
        you cross a DOWN==0
        the team changed from the last play
        or something like that...too blurry to think right now
    """
    rows = load_as_rows('nflplays.csv')

    row = rows[0]
    cur_off = row.play.offense
    prev_off = cur_off
    cur_down = int(row.play.down)
    prev_game_id = row.game.game_id
    drive_lookup = {row.play.offense: 0, row.play.defense: 0}
    seen_zero_down = False

    for i, row in enumerate(rows):
        cur_game_id = row.game.game_id
        cur_off = row.play.offense
        cur_down = int(row.play.down)

        # reset for new game
        if cur_game_id != prev_game_id:
            prev_off = cur_off
            drive_lookup = {row.play.offense: 0, row.play.defense: 0}
            seen_zero_down = False
            if cur_down != 0:
                seen_zero_down = True

        # set drive
        if cur_down == 0:
            row.play.drive_id = -1
            seen_zero_down = True
        else:
            # check to see if this is first play of new drive
            if seen_zero_down or cur_off != prev_off:
                drive_lookup[cur_off] += 1
                seen_zero_down = False
            row.play.drive_id = drive_lookup[cur_off]

        prev_game_id = cur_game_id
        prev_off = cur_off

    dump_as_rows('nflplays_2.csv', rows)

assert_invertible()
# add_rel_play_id()
# fix_off_def()
# check_drives()
# check_kickoff()
# add_drive_id()
