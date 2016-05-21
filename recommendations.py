# python code chapter 1 Sushmit Roy
# A dictionary of movie critics and their ratings of a small
# set of movies
from math import sqrt
import pandas as pd
from scipy.spatial import distance
from itertools import permutations

critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                         'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                         'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                'Superman Returns': 3.5, 'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                            'The Night Listener': 4.5, 'Superman Returns': 4.0,
                            'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                            'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                             'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
    # Get the list of shared_items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
            # if they have no ratings in common, return 0
        if len(si) == 0: return 0
        #  Add up the squares of all the differences
        sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                              for item in prefs[person1] if item in prefs[person2]])
    return 1 / (1 + sum_of_squares)


# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1
    # Find the number of elements
    n = len(si)
    # if they are no ratings in common, return 0
    if n == 0:
        return 0
    # Add up all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    # Sum up the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
    # Sum up the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])
    # Calculate Pearson score
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0:
        return 0

    return num / den


# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson2(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1
    # Find the number of elements
    n = len(si)
    # if they are no ratings in common, return 0
    if n == 0:
        return 0
    # Use correlation from numpy
    x_series = pd.Series([prefs[p1][it] for it in si])
    y_series = pd.Series([prefs[p2][it] for it in si])
    return x_series.corr(y_series)


# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similarity=sim_pearson2):
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]
    # Sort the list so the highest scores appear at the top scores.sort( )
    scores.sort(reverse= True)
    return scores[0:n]


# Gets recommendations for a person by using a weighted average
# of every other user's rankings
def getRecommendations(prefs, person, similarity=sim_pearson2):
    totals = {}
    simSums = {}
    for other in prefs:
        # don't compare me to myself
        if other == person:
            continue
        sim = similarity(prefs, person, other)
        # ignore scores of zero or lower
        if sim <= 0:
            continue
        for item in prefs[other]:
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim
    # Create the normalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]

    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n=10):
    # Create a dictionary of items showing which other items they
    # are most similar to.
    result = {}
    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # Status updates for large datasets
        c += 1
        if c % 100 == 0:
            print("%d / %d" % (c, len(itemPrefs)))
        # Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result


def getRecommendedItems(prefs,itemMatch,user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # Loop over items rated by this user
    for (item, rating) in userRatings.items():
        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:
            # Ignore if this user has already rated this item
            if item2 in userRatings:
                continue
            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
    # Divide each total score by total weighting to get an average
    rankings=[(score/totalSim[item],item) for item,score in scores.items()]
    # Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings

########## All functions using pandas ###########
# Calculating euclidean distance
def pd_sim_distance(df_critics, person1, person2):
    ser1 = df_critics[person1] - df_critics[person2]
    return 1 / (1 + (ser1**2).sum())

## to calculate pearson distance
def pd_sim_pearson(df_critics, person1, person2):
    return df_critics[person1].corr(df_critics[person2])


def pd_top_matches(df_critics, person, n=5, similarity=pd_sim_pearson):
    rankings = [(similarity(df_critics, person1, person),person1) for person1 in
            list(set(df_critics.columns) - set({person}))]
    rankings.sort(reverse = True)
    return rankings[0:n]


def pd_getRecommendations(df_critics, person, similarity=pd_sim_pearson):
    rec_list = []
    similarity_series = pd.Series(
        {item[1]: 0.5*(item[0] + abs(item[0])) for item in pd_top_matches(df_critics, person, similarity=similarity)})
    for movie in list(df_critics[person][df_critics[person].isnull()].index):
        # To get rating people who have rated the movie
        rating_series = df_critics.loc[movie][df_critics.loc[movie].notnull()]
        #score = (similarity_series * rating_series).sum()/(similarity_series*(rating_series/rating_series).sum())
        total = (similarity_series * rating_series).sum()
        sim_sum = (similarity_series*(rating_series/rating_series)).sum()
        if sim_sum > 0:
            rec_list.append((total/sim_sum,movie))
    rec_list.sort(reverse=True)

    return rec_list


def pd_calculateSimilarItems(df_critics, n=10):
    df_movies = df_critics.transpose()
    result = {}
    c = 0
    for movie in df_movies.columns:
        c += 1
        if c % 100 == 0:
            print("%d / %d" % (c, len(df_movies)))
        ret_tuple = pd_top_matches(df_movies, movie, n=n, similarity=pd_sim_distance)
        result[movie] = { item[1]:item[0]  for item in ret_tuple}
    return pd.DataFrame.from_dict(result)


def pd_getRecommendedItems(df_critics, df_item_sim, person):
    result = []

    for movie_not_watched in df_critics[person][df_critics[person].isnull()].index:
        movies_watched_series = df_critics[person][df_critics[person].notnull() & df_critics[person] != 0]
        ser = df_item_sim[movie_not_watched] * movies_watched_series
        ser1 = movies_watched_series / movies_watched_series
        ser2 = df_item_sim[movie_not_watched] * ser1
        if ser2.sum() > 0: result.append((ser.sum() / ser2.sum(), movie_not_watched))
    result.sort(reverse=True)
    return result
