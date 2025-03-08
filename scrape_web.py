import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

#map for team names to abbreviations
TeamAbrMap = {
    "Atlanta": "ATL",
    "Boston": "BOS",
    "Brooklyn": "BRK",
    "Charlotte": "CHO",
    "Chicago": "CHI",
    "Cleveland": "CLE",
    "Dallas": "DAL",
    "Denver": "DEN",
    "Detroit": "DET",
    "Golden State": "GSW",
    "Houston": "HOU",
    "Indiana": "IND",
    "LA": "LAC",
    "Los Angeles": "LAL",
    "Memphis": "MEM",
    "Miami": "MIA",
    "Milwaukee": "MIL",
    "Minnesota": "MIN",
    "New Orleans": "NOP",
    "New York": "NYK",
    "Oklahoma City": "OKC",
    "Orlando": "ORL",
    "Philadelphia": "PHI",
    "Phoenix": "PHO",
    "Portland": "POR",
    "Sacramento": "SAC",
    "San Antonio": "SAS",
    "Toronto": "TOR",
    "Utah": "UTA",
    "Washington": "WAS",
}

#function to scrape for all NBA teams
def getTeams():
    #url that displays all nba teams
    teams_url = "https://www.espn.com/nba/teams"   
    #copied headers from geeks for geeks
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

    #send a response and check if response is valid
    response = requests.get(teams_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve NBA teams data. Status Code: {response.status_code}")
        exit()

    #use beautiful soap to format html request
    data = BeautifulSoup(response.text, "html5lib")
    
    team_dictionary = {} #team dictionary
    
    #iterate through all divisions of teams
    for team_section in data.find_all("section", class_="TeamLinks"):
        #extract the <h2> tags associated
        team_data = team_section.find_previous("h2")

        if team_data:
            #Strip the team data to extract the team name
            team_name = team_data.text.strip()

            #extract the schedule link for each team
            schedule_link_data = team_section.find("a", text="Schedule")
            if schedule_link_data and "href" in schedule_link_data.attrs:
                #concat url and add to dictionary
                schedule_url = "https://www.espn.com" + schedule_link_data["href"]
                team_dictionary[team_name] = schedule_url

    #return created dictionary
    return team_dictionary      


#function that gets information about today's games
def getGamesToday():
    #URL that holds todays NBA schedule
    url = "https://www.espn.com/nba/schedule"
    #copied from geeks for geeks
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    #check for valid response
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve schedule. Status Code: {response.status_code}")
        exit()
    
    #use Beautiful soup to format html request
    data = BeautifulSoup(response.text, "html5lib")
    
    #scrape page for table of games
    allGames = data.find("div", class_="Table__Scroller")
    if not allGames:
        print("Could not find the table container.")
        exit()

    #within the huge table find todays table
    todaysGames = allGames.find("table", class_="Table")
    if not todaysGames:
        print("Could not locate todays games.")
        exit()

    #find the tbody that contains data within table
    todayData = todaysGames.find("tbody")
    if not todayData:
        print("Error locating todays game data")
        exit()

    games = [] #table to store game info

    gameRows = todayData.find_all("tr", attrs={"data-idx": True})
    #iterate through each game and schedule data
    for game in gameRows:
        gameContent = game.find_all("td")

        #filter useful information
        awayTeam = gameContent[0].get_text()
        homeTeam = gameContent[1].get_text()
        homeTeam = homeTeam.replace('@', '').strip()

        gamblingStats = gameContent[5].get_text()
        #if game stats are changing they won't show up on espn
        if gamblingStats and "O/U:" in gamblingStats:
            gameline, totalPoints = gamblingStats.split("O/U:")
            gameline = gameline.replace("Line:", "").strip()
            totalPoints = totalPoints.strip()
        else:
            gameline = ""
            totalPoints = ""
    
        #add information to dictionary and append to game array
        gameDetails = {
            "awayTeam": awayTeam,
            "homeTeam": homeTeam,
            "gameline": gameline,
            "overUnder": totalPoints
        }
        games.append(gameDetails)

    return games
    
#shows matchups for suer to select
def displayMatchup(games):
    print("Today's Matchups:")

    #iterate through all games and ad values for the user to select
    for i, game in enumerate(games, start=1):
        print(f"{i}. {game['awayTeam']} at {game['homeTeam']} "
              f"(Line: {game['gameline']}, O/U: {game['overUnder']})")

#function to allow user to investigate specific game
def userSelectGame(games):
    displayMatchup(games)
    while True:
        try:
            userInput = int(input("Enter the number of the matchup you want to see: "))
            #check for valid input
            if 1 <= userInput <= len(games):
                return games[userInput - 1]
            else:
                print(f"Please enter a number between 1 and {len(games)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

#function gets teams basketball refrence url based on entering city name
def getTeamUrl(team):
    #get mapped abbreviation
    teamAbbr = TeamAbrMap[team]
    #format the new url and return it
    url = f"https://www.basketball-reference.com/teams/{teamAbbr}/2025.html"
    return url

#function to scrape data from table
def scrapeTeamDetailPage(teamURL):
    #check for valid url and html data
    response = requests.get(teamURL)
    if response.status_code != 200:
        print("Can't reach team page")
        exit()
    
    #Remove html comments
    repsonse = re.sub(r'<!--|-->', '', response.text)

    #get data of url and pass through beautiful soup
    data = BeautifulSoup(repsonse, 'html.parser')

    #returns the data on the page
    return data

#function returns df of team injuries
def getInjuryTable(pageData):
    #find table by id of injuries and check if valid
    table = pageData.find("table", id="injuries")
    if not table:
        print("Couldn't find injury table")
        exit()

    #get the column headers and save in array
    header = table.find("thead").find("tr")
    columnNames= [th.get_text(strip=True) for th in header.find_all("th")]

    rows = [] #array for row data

    #iterate through table and scrape each row for data
    for row in table.find("tbody").find_all("tr"):
        cells = row.find_all(["th", "td"])
        rowData = [cell.get_text(strip=True) for cell in cells]
        rows.append(rowData)

    #create data frame with columns and rows found
    df = pd.DataFrame(rows, columns=columnNames)
    return df

#function returns df of the team stats per game
def getTeamStats(pageData):
    #find table by id of per_game_stats and check if valid
    table = pageData.find("table", id="per_game_stats")
    if not table:
        print("Couldn't find stats table")
        exit()
    
    #get column headers and save in array
    header = table.find("thead").find("tr")
    columnNames= [th.get_text(strip=True) for th in header.find_all("th")]
    
    rows = [] #array for row data

    #iterate through table and scrape each row for data
    for row in table.find("tbody").find_all("tr"):
        cells = row.find_all(["th", "td"])
        rowData = [cell.get_text(strip=True) for cell in cells]
        rows.append(rowData)

    #create data frame with columns and rows found
    df = pd.DataFrame(rows, columns=columnNames)
    df.drop(['Rk', 'Awards'], axis=1, inplace=True) #clean df a bit
    return df

selectedGame = userSelectGame(getGamesToday())
x = getTeamUrl(selectedGame["awayTeam"])
y = getTeamStats(scrapeTeamDetailPage(x))
print(y)

    
        