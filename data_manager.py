import pandas as pd
import scrape_web
from datetime import datetime
import time

#cache to store data collected in one place
cache = {
    'games': {'data': None, 'timestamp': 0},
    'teamStats': {},
    'playerStats': {},
    'injuries': {}
}


#cache refresh rates
cacheTimeLimit = {
    'games': 300,  #5 minutes
    'teamStats': 3600,  #1 hour
    'playerStats': 3600,  #1 hour
    'injuries': 300  #5 minutes
}

#get future NBA games going to be played
def callGetGamesToday():
    #get current time
    currTime = time.time()
    
    #check if cache has no data or data needs updated
    if ((cache['games']['data'] is None) or 
        (currTime - cache['games']['timestamp'] > cacheTimeLimit['games'])):
        
        #get games being played next
        games = scrape_web.getGamesToday()
        
        #update cache
        cache['games'] = {
            'data': games,
            'timestamp': currTime
        }

    #return scraped games  
    return cache['games']['data']

#return team page data
def getTeamData(teamCity):
    #get URL associated with team
    teamUrl = scrape_web.getTeamUrl(teamCity)

    #parse through team URL
    teamPageData = scrape_web.scrapeTeamDetailPage(teamUrl)

    return teamPageData

#get injuries for specific team
def callGetInjuries(teamCity):
    #get currentTime to check if needed updated
    currentTime = time.time()
    
    #Check if data is not found or needs updated
    if (teamCity not in cache['injuries'] or 
        currentTime - cache['injuries'][teamCity]['timestamp'] > cacheTimeLimit['injuries']):

        #retrieve injury table
        injuryDf = scrape_web.getInjuryTable(getTeamData(teamCity))
        
        #Update cache to store teams injuries
        cache['injuries'][teamCity] = {
            'data': injuryDf,
            'timestamp': currentTime
        }
    
    return cache['injuries'][teamCity]['data']

#get team stats for specific team
def callGetTeamStats(teamName):
    #get current time for outdated data
    currentTime = time.time()
    
    #Check if data is already fetched and if cache is valid
    if (teamName not in cache['teamStats'] or 
        currentTime - cache['teamStats'][teamName]['timestamp'] > cacheTimeLimit['teamStats']):
        
        #get team stats data fram and player links for each player
        teamDf, playerLinks = scrape_web.getTeamStats(getTeamData(teamName))
        
        #update the cache
        cache['teamStats'][teamName] = {
            'data': teamDf,
            'player_links': playerLinks,
            'timestamp': currentTime
        }
    
    return cache['teamStats'][teamName]['data'], cache['teamStats'][teamName]['player_links']

#get player game logs for specfic player
def callGetPlayerGameLogs(playerName, teamCity):
    #get time for outdated data
    currentTime = time.time()
    
    #Create key for each player
    playerKey = f"{playerName}_{teamCity}"
    
    #Check if player game logs are stored and check if data is outdated
    if (playerKey not in cache['playerStats'] or 
        currentTime - cache['playerStats'][playerKey]['timestamp'] > cacheTimeLimit['playerStats']):
        
        #get team data to find player url
        x, playerLinks = callGetGamesToday(teamCity)
        
        #check to make sure player exists in found player links
        if playerName not in playerLinks:
            return pd.DataFrame()
        
        # Get player stats
        playerUrl = playerLinks[playerName]
        playerDf = scrape_web.getPlayerGames(playerUrl)
        
        # Update cache
        cache['playerStats'][playerKey] = {
            'data': playerDf,
            'timestamp': currentTime
        }
    
    return cache['playerStats'][playerKey]['data']

#get all data for selected matchup
def allMatchupData(game):
    awayTeam = game["awayTeam"]
    homeTeam = game["homeTeam"]

    #get team stats for both teams
    awayTeamStats, awayPlayerLinks = callGetTeamStats(awayTeam)
    homeTeamStats, homePlayerLinks = callGetTeamStats(homeTeam)

    #get injury tables for each team
    awayInjuries = callGetInjuries(awayTeam)
    homeInjuries = callGetInjuries(homeTeam)

    #return collected data
    return {
        "awayTeam": {
            "name": awayTeam,
            "stats": awayTeamStats,
            "playerLinks": awayPlayerLinks,
            "injuries": awayInjuries
        },
        "homeTeam": {
            "name": homeTeam,
            "stats": homeTeamStats,
            "playerLinks": homePlayerLinks,
            "injuries": homeInjuries
        },
        "gameline": game.get("gameline", ""),
        "overUnder": game.get("overUnder", "")
    }


callGetGamesToday()
allMatchupData(cache['games']['data'][1])

