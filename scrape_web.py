import requests
from bs4 import BeautifulSoup

def scrapeTeamSchedule(team):
    print("Hi")


def userSelectTeam():
    print("Hi")

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

            
        
def main():
    x = getTeams()

if __name__ == "__main__":
    main()