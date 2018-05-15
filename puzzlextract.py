import chess.pgn
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import time
from io import StringIO
import fileinput
import sys

file = sys.argv[1]
# puzzle counter
count = 1

json_puzzles = open(file, 'r')

def extract():
	global count
	# import json / parse last_pos & last_move & gameID
	json_tree = json.loads(line)
	gameID = json_tree['game_id']
	last_pos = json_tree['last_pos']
	last_move = json_tree['last_move']

	# final FEN position
	board = chess.Board(last_pos)
	board.push_uci(last_move)
	fen = board.fen()

	# whitch turn to move
	if board.turn == True:
		turn = '&#9711; White'
	else:
		turn = '&#9899; Black'

	# fetching pgn from lichess
	html = urlopen('https://lichess.org/{0}'.format(gameID))

	soup = BeautifulSoup(html, 'html.parser')
	pgnraw = soup.find("div", {"class": "pgn"})
	pgnclean = str(pgnraw)
	pgn_string = pgnclean[17:-6]
	pgn = StringIO(pgn_string)

	game = chess.pgn.read_game(pgn)

	# player name/elo & timecontrol
	w_player = game.headers["White"]
	w_player_elo =  game.headers["WhiteElo"]
	b_player = game.headers["Black"]
	b_player_elo =  game.headers["BlackElo"]
	timecontrol = game.headers["TimeControl"]

	# generate the html between each <td></td> using all the data
	td_str = """<td style="text-align: center;"><strong>{w} </strong>({we}) -<strong> {b} </strong>({be})<br /><a href="https://lichess.org/{id}">Gamelink</a>.<br />{t} to play.<br /><a href="https://lichess.org/analysis/{f}"><img src="http://www.fen-to-image.com/image/25/double/coords/{f}" /></a></td>"""
	td = td_str.format(w=w_player, b=b_player, we=w_player_elo, be=b_player_elo, id=gameID, f=fen, t=turn)

	print("Creation of puzzle n°{0}".format(count))
	count += 1
	time.sleep(1)

	return (td, timecontrol)

# declare the lists for the loop to fill
series = []
lichess4545 = []
lonewolf = []
others = []

# loop to generate all the data
for line in json_puzzles:
	puzzle = extract()
	# ordering puzzles by league
	if puzzle[1] == "5400+30":
		series.append(puzzle[0])
	elif puzzle[1] == "2700+45":
		lichess4545.append(puzzle[0])
	elif puzzle[1] == "1800+30":
		lonewolf.append(puzzle[0])
	else:
		others.append(puzzle[0])

json_puzzles.close()

# format to html
header = """<p style="text-align: justify; margin-left: 40px;"><em>Click on the images for the solution.</em></p><table align="center" style="width:90%">"""
tr_lichess4545 = """<tr><td colspan=4><p style="text-align:center"><span style="font-size:14px">Lichess4545</span></p></td></tr>"""
tr_lonewolf = """<tr><td colspan=4><p style="text-align:center"><span style="font-size:14px">Lonewolf</span></p></td></tr>"""
tr_series = """<tr><td colspan=4><p style="text-align:center"><span style="font-size:14px">Series</span></p></td></tr>"""
tr_others = """<tr><td colspan=4><p style="text-align:center"><span style="font-size:14px">others</span></p></td></tr>"""
tr_open = """<tr>"""
tr_close = """</tr>"""
foot = """</table>"""

print(header)

# repeat the script for each league separately
def each_league(league, tr_league):
	print(tr_league)

	# caculate the number of row needed
	row_calc = 0
	for x in league:
		row_calc += 1
	row = row_calc // 4
	rest = row_calc % 4

	# increment variable for targeting the correct element in the list
	u = 0

	# generating complete rows = 4 puzzles
	if row != 0:
		for x in range(row):
			print (tr_open)
			for i in range(4):
				print(league[u])
				u += 1
			print(tr_close)
			row -= 1

	# last row or less than 4 puzzles in this league
	if rest != 0:
		print (tr_open)
		for i in range(rest):
			print(league[u])
			u += 1
		print (tr_close)

# check if any entry before comiting the script
if lichess4545:
	each_league(lichess4545, tr_lichess4545)
if lonewolf:
	each_league(lonewolf, tr_lonewolf)
if series:
	each_league(series, tr_series)
if others:
	each_league(others, tr_others)

print (foot)
