import pandas as pd
import tqdm
from tqdm import tqdm, tqdm_notebook


def win(df):
    """Renvoie le résultat d'un match donné pour l'équipe à domicile."""
   #On définit les variables de buts.

    
    home_score = df[0] 
    away_score = df[1] 
    
    
    if home_score > away_score:
        return 'W'
    elif home_score < away_score:
        return 'L'
    else:
        return 'D'


def get_match_outcome(match):
    """Renvoie le résultat d'un match donné, pour l'équipe à domicile, mais sous forme de dataframe."""
    
    #On définit les variables de buts.
    home_goals = match['home_team_goal']
    away_goals = match['away_team_goal']
     
    outcome = pd.DataFrame()
    outcome.loc[0,'match_api_id'] = match['match_api_id'] 

    #On identifie le résultat d'une façon analogue à la fonction précédente:  
    if home_goals > away_goals:
        outcome.loc[0,'outcome'] = "Win"
    if home_goals == away_goals:
        outcome.loc[0,'outcome'] = "Draw"
    if home_goals < away_goals:
        outcome.loc[0,'outcome'] = "Defeat"

      
    return outcome.loc[0]



def get_last_matches(matches, date, team, x = 10):
    ''' Permet de récupérer les x derniers matches joués par une équipe avant une date donnée. '''
    #On récupère tous les matchs de l'équipe en question, qu'ils soient joués à domicile ou à l'extérieur.
    team_matches = matches[(matches['home_team_api_id'] == team) | (matches['away_team_api_id'] == team)]
                           
    #On récupère les x matches les plus récents.
    last_matches = team_matches[team_matches.date < date].sort_values(by = 'date', ascending = False).iloc[0:x,:]
    
    return last_matches
    
    

def get_last_team_stats(team_id, date, teams_stats):
    ''' Permet de récupérer les dernières statistiques d'une équipe donnée. Notons que cette fois, nous ne restreignons pas le nombre de statistiques récupérées. '''
    #La méthode est la même que précedemment.
    all_team_stats = teams_stats[teams_stats['team_api_id'] == team_id]
           
    last_team_stats = all_team_stats[all_team_stats.date < date].sort_values(by='date', ascending=False)
    if last_team_stats.empty:
        last_team_stats = all_team_stats[all_team_stats.date > date].sort_values(by='date', ascending=True)

    return last_team_stats.iloc[0:1,:]
    
    
def get_last_matches_against_eachother(matches, date, home_team, away_team, x = 10):  
    ''' Renvoie les x derniers matchs opposant deux équipes données, une "home_team" et une "away_team" '''
    #On récupère tous les matches opposant les deux équipes.
    home_matches = matches[(matches['home_team_api_id'] == home_team) & (matches['away_team_api_id'] == away_team)]    
    away_matches = matches[(matches['home_team_api_id'] == away_team) & (matches['away_team_api_id'] == home_team)]  
    total_matches = pd.concat([home_matches, away_matches])
    
    #On récupère les derniers matches opposant les deux équipes, pour peu qu'il y en ait assez.
    try:    
        last_matches = total_matches[total_matches.date < date].sort_values(by = 'date', ascending = False).iloc[0:x,:]
    except:
        last_matches = total_matches[total_matches.date < date].sort_values(by = 'date', ascending = False).iloc[0:total_matches.shape[0],:]
        
        #On renvoie une erreur permettant de comprendre pourquoi il y a moins de matches que demandés si on demande plus de matches que possible.
        if(last_matches.shape[0] > x):
            print("Error : not enough matches.")
            
    return last_matches


def get_goals(matches, team):
    ''' Renvoie les derniers buts marqués (à domicile ou à l'extérieur) d'une équipe donnée. '''

    home_goals = int(matches.home_team_goal[matches.home_team_api_id == team].sum())
    away_goals = int(matches.away_team_goal[matches.away_team_api_id == team].sum())

    total_goals = home_goals + away_goals
    
    return total_goals



def get_goals_conceided(matches, team):
    ''' Renvoie les derniers buts concédés (à domicile ou à l'extérieur) d'une équipe donnée '''
    home_goals = int(matches.home_team_goal[matches.away_team_api_id == team].sum())
    away_goals = int(matches.away_team_goal[matches.home_team_api_id == team].sum())

    total_goals = home_goals + away_goals

    return total_goals


def get_wins(matches, team):
    ''' Renvoie le nombre de victoires d'une équipe pour un set de matches donnés. '''
    
    home_wins = int(matches.home_team_goal[(matches.home_team_api_id == team) & (matches.home_team_goal > matches.away_team_goal)].count())
    away_wins = int(matches.away_team_goal[(matches.away_team_api_id == team) & (matches.away_team_goal > matches.home_team_goal)].count())

    total_wins = home_wins + away_wins

    return total_wins 



def get_match_features(match, matches, teams_stats, x = 10):
    ''' Renvoie les features d'un match précis pour les deux équipes concernées. 
    On y trouvera les buts marqués, encaissés, ainsi qu'un historique des derniers matchs des deux équipes et de leurs confrontations les plus récentes.'''
    #On définit les variables.
    date = match.date
    home_team = match.home_team_api_id
    away_team = match.away_team_api_id
    
     # On récupère les statistiques de l'équipe qui reçoit pour le match donné, et de l'équipe visiteuse pour le match donné. 
    home_team_stats = get_last_team_stats(home_team, date, teams_stats);
    away_team_stats = get_last_team_stats(away_team, date, teams_stats);
    
    # On récupère les derniers matchs pour chaque équipe.
    matches_home_team = get_last_matches(matches, date, home_team, x = 5)
    matches_away_team = get_last_matches(matches, date, away_team, x = 5)
    
    #On récupère un nombre plus restreint de leurs confrontations. Motivation: leurs confrontations sont souvent à des moments assez éloignés, et leur intégration peut donc devenir peu pertinente.
    last_matches_against = get_last_matches_against_eachother(matches, date, home_team, away_team, x = 3)
    
    #On utilise get_goals pour obtenir les buts marqués et concédés par chaque équipe.
    home_goals = get_goals(matches_home_team, home_team)
    away_goals = get_goals(matches_away_team, away_team)
    home_goals_conceided = get_goals_conceided(matches_home_team, home_team)
    away_goals_conceided = get_goals_conceided(matches_away_team, away_team)
    
    #On initialise le résultat:
    result = pd.DataFrame()
    
    #On y range les ID:
    result.loc[0, 'match_api_id'] = match.match_api_id
    result.loc[0, 'league_id'] = match.league_id
    
    #On y range ensuite les différentes statistiques des deux équipes, tant qu'elles existent.
    if(not home_team_stats.empty):
        result.loc[0, 'home_team_buildUpPlaySpeed'] = home_team_stats['buildUpPlaySpeed'].values[0]
        result.loc[0, 'home_team_buildUpPlayPassing'] = home_team_stats['buildUpPlayPassing'].values[0]
        result.loc[0, 'home_team_chanceCreationPassing'] = home_team_stats['chanceCreationPassing'].values[0]
        result.loc[0, 'home_team_chanceCreationCrossing'] = home_team_stats['chanceCreationCrossing'].values[0]
        result.loc[0, 'home_team_chanceCreationShooting'] = home_team_stats['chanceCreationShooting'].values[0]
        result.loc[0, 'home_team_defencePressure'] = home_team_stats['defencePressure'].values[0]
        result.loc[0, 'home_team_defenceAggression'] = home_team_stats['defenceAggression'].values[0]
        result.loc[0, 'home_team_defenceTeamWidth'] = home_team_stats['defenceTeamWidth'].values[0]
        result.loc[0, 'home_team_avg_shots'] = home_team_stats['avg_shots'].values[0]
        result.loc[0, 'home_team_avg_corners'] = home_team_stats['avg_corners'].values[0]
        result.loc[0, 'home_team_avg_crosses'] = away_team_stats['avg_crosses'].values[0]
    
    if(not away_team_stats.empty):
        result.loc[0, 'away_team_buildUpPlaySpeed'] = away_team_stats['buildUpPlaySpeed'].values[0]
        result.loc[0, 'away_team_buildUpPlayPassing'] = away_team_stats['buildUpPlayPassing'].values[0]
        result.loc[0, 'away_team_chanceCreationPassing'] = away_team_stats['chanceCreationPassing'].values[0]
        result.loc[0, 'away_team_chanceCreationCrossing'] = away_team_stats['chanceCreationCrossing'].values[0]
        result.loc[0, 'away_team_chanceCreationShooting'] = away_team_stats['chanceCreationShooting'].values[0]
        result.loc[0, 'away_team_defencePressure'] = away_team_stats['defencePressure'].values[0]
        result.loc[0, 'away_team_defenceAggression'] = away_team_stats['defenceAggression'].values[0]
        result.loc[0, 'away_team_defenceTeamWidth'] = away_team_stats['defenceTeamWidth'].values[0]
        result.loc[0, 'away_team_avg_shots'] = away_team_stats['avg_shots'].values[0]
        result.loc[0, 'away_team_avg_corners'] = away_team_stats['avg_corners'].values[0]
        result.loc[0, 'away_team_avg_crosses'] = away_team_stats['avg_crosses'].values[0]
    
    result.loc[0, 'home_team_goals_difference'] = home_goals - home_goals_conceided
    result.loc[0, 'away_team_goals_difference'] = away_goals - away_goals_conceided
    result.loc[0, 'games_won_home_team'] = get_wins(matches_home_team, home_team) 
    result.loc[0, 'games_won_away_team'] = get_wins(matches_away_team, away_team)
    result.loc[0, 'games_against_won'] = get_wins(last_matches_against, home_team)
    result.loc[0, 'games_against_lost'] = get_wins(last_matches_against, away_team)
    result.loc[0, 'B365H'] = match.B365H
    result.loc[0, 'B365D'] = match.B365D
    result.loc[0, 'B365A'] = match.B365A
    
    #On renvoie les résultats:
    return result.loc[0]


def get_features(matches, teams_stats, fifa, x = 10):  
    ''' Renvoie les statistiques des matches via la fonction get_match_features, ainsi que les données fifa.'''
    #On récupère d'abord les notes fifa. Voir plus bas.
    fifa_stats = get_overall_fifa_rankings(fifa)
    
    #On utilise get_match_features sur match_stats
    match_stats = matches.apply(lambda i: get_match_features(match=i, matches=matches, teams_stats=teams_stats, x = 10), axis = 1)
    
    #On crée des dummies pour les identifiants de ligue.
    dummies = pd.get_dummies(match_stats['league_id']).rename(columns = lambda x: 'League_' + str(x))
    match_stats = pd.concat([match_stats, dummies], axis = 1)
    match_stats.drop(['league_id'], inplace = True, axis = 1)
    

    #On récupère les résultats des matchs. Cette cellule étant longue, on utilise tqdm pour s'assurer qu'elle ne bloque pas.
    tqdm_notebook().pandas()
    outcomes = matches.progress_apply(get_match_outcome, axis = 1)

    #On fusionne le tout grâce aux identifiants.
    features = pd.merge(match_stats, fifa_stats, on = 'match_api_id', how = 'left')
    features = pd.merge(features, outcomes, on = 'match_api_id', how = 'left')
    
    #On retire les NA.
    features.dropna(inplace = True)
    
    return features


def get_overall_fifa_rankings(fifa):
    ''' Renvoie les notes FIFA des joueurs.'''
      
    temp_data = fifa
    
    #On récupère tout, sauf la date
    cols = fifa.loc[:,(fifa.columns.str.contains('date_stat'))]
    temp_data = fifa.drop(cols.columns, axis = 1)        
    data = temp_data
    
    return data