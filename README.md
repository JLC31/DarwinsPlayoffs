# Darwin'sPlayoffs
Automated Python script to update a Google Sheet with fantasy football stats for Darwin's Gridiron Fantasy League

Automatically updates the playoff matchups in the Darwin's Gridiron Fantasy League with real time player fantasy points.

After looking through the data on Sleeper.com website, I found the API that returns weekly fantasy points which is used by their website to calculate matchups. By accessing

https://api.sleeper.com/stats/nfl/{YEAR}/{WEEK}?season_type=regular&position[]=DEF&position[]=FLEX&position[]=K&position[]=QB&position[]=RB&position[]=TE&position[]=WR&order_by=pts_ppr
(where {YEAR} and {WEEK} are integer values (for example, '/nfl/2023/15' to return the week 15 of the 2023 season stats)

you will be able to view all of the fantasy points for any player during any week (so long as the player is/has finished playing). 

I hope others looking for an API that returns fantasy information, such as PPR/0.5PPR/standard fantasy points, individual player stats, as well as game stats (such as first downs, turnovers, etc), will be able to use this API for their projects as I did.
