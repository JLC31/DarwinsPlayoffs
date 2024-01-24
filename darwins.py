import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

scope = ["https://spreadsheets.google.com/feeds",
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive.file",
"https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("config.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Darwin's Playoffs 2023").sheet1

sheet_data = sheet.get_values()

# data = all of the players on the rosters for specific league (hence the /rosters at the end)
# the numbers between 'league' and 'rosters' are the unique sleeper league ID

data = json.loads(requests.get("https://api.sleeper.app/v1/league/990374568424497152/rosters").text)

# all_players = information such as name, experience, position, player ID

all_players = json.loads(requests.get("https://api.sleeper.app/v1/players/nfl").text)

# stats = fantasy data from specified week, from each player who recorded a stat, sorted by highest fantasy points -> lowest
# can change the data returned by modifying the week or year:
# '/stats/nfl/2023/17?' will return the fantasy stats from the 2023 nfl season week 17

stats = json.loads(requests.get("https://api.sleeper.com/stats/nfl/2023/17?season_type=regular&position[]=DEF&position[]=FLEX&position[]=K&position[]=QB&position[]=RB&position[]=TE&position[]=WR&order_by=pts_ppr").text)


starters = []

darwins = [
    ["TOB", [], [], []],
    ["Henn", [], [], []],
    ["Tom", [], [], []],
    ["Chruma", [], [], []],
    ["Brad", [], [], []],
    ["Matteo", [], [], []],
    ["Logan", [], [], []],
    ["Dotz", [], [], []],
    ["John", [], [], []],
    ["Jake", [], [], []],
    ["Paul", [], [], []],
    ["Diez", [], [], []],
]

# darwins = [
#   [name, starter id, starter full name, starter fantasy points]
# ]

# fill darwins array with player ids to begin adding points and names below

count = 0
for i in data:
    darwins[count][1] = i['starters']
    count += 1
    for j in i['starters']: #j = playerID
        try:
            starters.append(j)
        except:
            starters.append(all_players[j]['team'])


def clean_up_defsense():
    items = ['yds_allow', 'fum_rec', 'int', 'sack', 'pts_allow']

current_stats = []

for b in stats:
    current_stats.append(b['player_id']) # all the playerIDs who have played in week 15 and recorded stats thus far
    # all_players is a list of all playerIDs
    # if the player is a starter but isn't in the stats, put a zero

# for all 12 darwins teams
#   for all starter playerIDs on a single team
#       for all players who have recorded stats
            # if starter is in all_players but not in the stats --> put a zero

print(current_stats)

for _count in range(12):
    for j in darwins[_count][1]:
        if j not in current_stats:
            try:
                darwins[_count][2].append(all_players[j]['full_name'])
                darwins[_count][3].append(0)
            except:
                darwins[_count][2].append(all_players[j]['team'])
                darwins[_count][3].append(0)
        else:
            # our league contains unique rulesets for positions that aren't the default returned
            # by the sleeper API for 0.5 PPR leagues - these following stat corrections help to
            # make sure the fantasy points in the sheet are the fantasy points received
            # on our app

            for p in stats:
                if j == p['player_id']: #the player will exist, but what if they get no points?
                    if 'pass_int' in p['stats']:
                        interception = -1 * p['stats']['pass_int']
                        qb_points = p['stats']['pts_half_ppr'] + interception

                        darwins[_count][2].append(p['player']['first_name'] + ' ' + p['player']['last_name'])
                        darwins[_count][3].append(qb_points)

                        print(p['player']['last_name'], qb_points)
                    elif 'fan_pts_allow' in p['stats']: 
                        def_points = 0
                        if 'pts_allow' in p['stats']:
                            if  1 <= p['stats']['pts_allow'] <= 6:
                                def_points+=4
                            elif 7 <= p['stats']['pts_allow'] <= 13:
                                def_points += 3
                            elif 14 <= p['stats']['pts_allow'] <= 20:
                                def_points +=2
                            elif 21 <= p['stats']['pts_allow'] <= 27:
                                def_points += 0
                            elif 28 <= p['stats']['pts_allow'] <= 34:
                                def_points -= 2
                            elif p['stats']['pts_allow'] >= 35:
                                def_points -= 5
                            else:
                                def_points += 5
                        if 'def_st_fum_rec' in p['stats']:
                            def_points += (p['stats']['def_st_fum_rec'] * 2)
                        if 'sack' in p['stats']:
                            def_points += p['stats']['sack']
                        if 'int' in p['stats']:
                            def_points += (p['stats']['int'] * 2)
                        if 'fum_rec' in p['stats']:
                            def_points += (p['stats']['fum_rec'] * 2)
                        if 'yds_allow' in p['stats']:
                            if 100 <= p['stats']['yds_allow'] <=199:
                                def_points += 4
                            elif 200 <= p['stats']['yds_allow'] <=349:
                                def_points += 3
                            elif 350 <= p['stats']['yds_allow'] <=499:
                                def_points -= 3
                            elif p['stats']['yds_allow'] >= 500:
                                def_points -= 6
                            else:
                                def_points += 5
                        if 'safe' in p['stats']:
                            def_points += (p['stats']['safe'] * 2)
                        if 'def_td' in p['stats']:
                            def_points += (p['stats']['def_td'] * 6)
                        if 'def_st_td' in p['stats']:
                            def_points += (p['stats']['def_st_td'] * 6)
                        if 'blk_kick' in p['stats']:
                            def_points += (p['stats']['blk_kick'] * 2)

                        darwins[_count][2].append(p['player']['last_name'])
                        darwins[_count][3].append(def_points)

                        print(p['player']['last_name'], def_points)
                    elif 'xpa' and 'fga' in p['stats']:
                        kick_points = 0
                        if 'fgm_yds' in p['stats']:
                            kick_points += (p['stats']['fgm_yds'] * 0.1)
                        if 'xpa' in p['stats']:
                            if p['stats']['xpa'] == p['stats']['xpm']:
                                kick_points += p['stats']['xpm']
                            elif p['stats']['xpa'] != p['stats']['xpm']:
                                kick_points -= (p['stats']['xpa'] - p['stats']['xpm'])
                        # print(kick_points)
                        darwins[_count][2].append(p['player']['first_name'] + ' ' + p['player']['last_name'])
                        darwins[_count][3].append(kick_points)
                        print(p['player']['last_name'], kick_points)
                    else:
                        try:

                            if p['stats']['pts_half_ppr'] > -100: 
                                darwins[_count][2].append(p['player']['first_name'] + ' ' + p['player']['last_name'])
                                darwins[_count][3].append(p['stats']['pts_half_ppr'])
                                print(p['player']['last_name'], p['stats']['pts_half_ppr'])
                        
                            else:
                                print('here')
                                darwins[_count][2].append(p['player']['first_name'] + ' ' + p['player']['last_name'])
                                darwins[_count][3].append(0)
                        except:
                            darwins[_count][2].append(p['player']['first_name'] + ' ' + p['player']['last_name'])
                            darwins[_count][3].append(0)
                         
# print to visually see player stats were properly added, if 0s were properly added

print(darwins)

# assign values for the columns for each matchup

team1_col = 2
team2_col = 4
team3_col = 6
team4_col = 8
team5_col = 10
team6_col = 12

pts1_col = 3
pts2_col = 5
pts3_col = 7
pts4_col = 9
pts5_col = 11
pts6_col = 13

# hard coded team #'s, sleeper assigns teams 1-12 (or 0-11) when joining fantasy league

tom_ = darwins[2][2]
wuk_ = darwins[6][2]
john_ = darwins[8][2]
brad_ = darwins[4][2]
paul_ = darwins[10][2]
jake_ = darwins[9][2]

# teams above are in the loser bracket

pts_tom_ = darwins[2][3]
pts_wuk_ = darwins[6][3]
pts_john_ = darwins[8][3]
pts_brad_ = darwins[4][3]
pts_paul_ = darwins[10][3]
pts_jake_ = darwins[9][3]

henn_ = darwins[1][2]
tob_ = darwins[0][2]
dotz_ = darwins[7][2]
matteo_ = darwins[5][2]
diez_ = darwins[11][2]
chruma_ = darwins[3][2]

# teams above are in the winner bracket

pts_henn_ = darwins[1][3]
pts_tob_ = darwins[0][3]
pts_dotz_ = darwins[7][3]
pts_matteo_ = darwins[5][3]
pts_diez_ = darwins[11][3]
pts_chruma_ = darwins[3][3]

_sheetcount = 0


for z in range(3, 13):
    # update winner bracket matchups
    # manually need to move previous week matchups down within the spreadsheet so that
    # you can make room for current weeks matchup at the top of the sheet
    # -- can be adapted upon further with additional movement of cells in code

    sheet.update_cell(z, team1_col, henn_[_sheetcount])
    sheet.update_cell(z, pts1_col, pts_henn_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z, team2_col, tob_[_sheetcount])
    sheet.update_cell(z, pts2_col, pts_tob_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z, team3_col, dotz_[_sheetcount])
    sheet.update_cell(z, pts3_col, pts_dotz_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z, team4_col, matteo_[_sheetcount])
    sheet.update_cell(z, pts4_col, pts_matteo_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z, team5_col, diez_[_sheetcount])
    sheet.update_cell(z, pts5_col, pts_diez_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z, team6_col, chruma_[_sheetcount])
    sheet.update_cell(z, pts6_col, pts_chruma_[_sheetcount])

    time.sleep(3)

    # update loser bracket

    sheet.update_cell(z+14, team1_col, tom_[_sheetcount])
    sheet.update_cell(z+14, pts1_col, pts_tom_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z+14, team2_col, wuk_[_sheetcount])
    sheet.update_cell(z+14, pts2_col, pts_wuk_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z+14, team3_col, paul_[_sheetcount])
    sheet.update_cell(z+14, pts3_col, pts_paul_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z+14, team4_col, jake_[_sheetcount])
    sheet.update_cell(z+14, pts4_col, pts_jake_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z+14, team5_col, john_[_sheetcount])
    sheet.update_cell(z+14, pts5_col, pts_john_[_sheetcount])
    time.sleep(2)
    sheet.update_cell(z+14, team6_col, brad_[_sheetcount])
    sheet.update_cell(z+14, pts6_col, pts_brad_[_sheetcount])
    time.sleep(2)


    _sheetcount += 1

print('done')