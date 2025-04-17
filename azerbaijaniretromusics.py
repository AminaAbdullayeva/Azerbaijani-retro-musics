#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import pandas as pd
from typing import List, Dict
from SPARQLWrapper import SPARQLWrapper, JSON
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster

class WikiDataQueryResults:
    """
    A class that can be used to query data from Wikidata using SPARQL and return the results 
    as a Pandas DataFrame or a list of dictionaries.
    """
    def __init__(self, query: str):
        """
        Initializes the WikiDataQueryResults object with a SPARQL query string.
        
        :param query: A SPARQL query string.
        """
        self.user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        self.endpoint_url = "https://query.wikidata.org/sparql"
        self.sparql = SPARQLWrapper(self.endpoint_url, agent=self.user_agent)
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)

    def __transform2dicts(self, results: List[Dict]) -> List[Dict]:
        """
        Helper function to transform SPARQL query results into a list of dictionaries.
        
        :param results: A list of query results returned by SPARQLWrapper.
        :return: A list of dictionaries, where each dictionary represents a result row.
        """
        new_results = []
        for result in results:
            new_result = {}
            for key in result:
                new_result[key] = result[key]['value']
            new_results.append(new_result)
        return new_results

    def _load(self) -> List[Dict]:
        """
        Helper function to load the data from Wikidata using the SPARQLWrapper query, 
        and transform the results into a list of dictionaries.
        
        :return: A list of dictionaries containing the query results.
        """
        results = self.sparql.query().convert()['results']['bindings']
        return self.__transform2dicts(results)

    def execute_query(self) -> pd.DataFrame:
        """
        Executes the SPARQL query and returns the results as a Pandas DataFrame.
        
        :return: A Pandas DataFrame containing the query results.
        """
        query_results = self._load()
        return pd.DataFrame(query_results)


# Define the SPARQL query for Retro Azerbaijani Music

# 1. Query to get Azerbaijani Retro Singers with Labels
query_singers = """
SELECT ?singer ?singerLabel ?birthDate WHERE {
  ?singer wdt:P31 wd:Q5;           # human
          wdt:P27 wd:Q227;         # Azerbaijan citizen
          wdt:P106 wd:Q177220;     # occupation: singer
          wdt:P569 ?birthDate.     # birth date
  FILTER(YEAR(?birthDate) < 1980)  # Limit to retro period (pre-1980)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
LIMIT 10
"""

# 2. Query to get Retro Azerbaijani Songs with Labels
query_songs = """
SELECT ?song ?songLabel ?performerLabel WHERE {
  ?song wdt:P31 wd:Q7366;                  # song (musical work)
        wdt:P364 wd:Q9292;                 # language: Azerbaijani
        wdt:P175 ?performer.               # performer
  ?performer wdt:P27 wd:Q227.              # Azerbaijan citizen
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
LIMIT 20
"""

# 3. Query to get Retro Azerbaijani Albums with Labels
query_albums = """
SELECT ?album ?albumLabel ?performerLabel ?publicationDate WHERE {
  ?album wdt:P31 wd:Q482994;         # music album
         wdt:P175 ?performer;        # performer
         wdt:P577 ?publicationDate.  # release date
  ?performer wdt:P27 wd:Q227.        # Azerbaijan citizen
  FILTER(YEAR(?publicationDate) < 2000)  # Retro period (pre-2000)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
ORDER BY ?publicationDate
LIMIT 20
"""

# Function to execute and get the results as a DataFrame
def get_wikidata_results(query):
    wiki_query = WikiDataQueryResults(query)
    return wiki_query.execute_query()

# Fetching results for Retro Azerbaijani Singers
singers_df = get_wikidata_results(query_singers)
print("Azerbaijani Retro Singers:")
print(singers_df)

# Fetching results for Retro Azerbaijani Songs
songs_df = get_wikidata_results(query_songs)
print("\nAzerbaijani Retro Songs:")
print(songs_df)

# Fetching results for Retro Azerbaijani Albums
albums_df = get_wikidata_results(query_albums)
print("\nAzerbaijani Retro Albums:")
print(albums_df)

# Data Visualization: Album Release Distribution (by Year)
albums_df['publicationDate'] = pd.to_datetime(albums_df['publicationDate'], errors='coerce')
albums_df['release_year'] = albums_df['publicationDate'].dt.year
release_years = albums_df['release_year'].dropna().astype(int)

# Plot the release year distribution (Bar Chart)
plt.figure(figsize=(12, 6))
release_years.value_counts().sort_index().plot(kind='bar', color='skyblue')
plt.title('Number of Retro Azerbaijani Albums Released by Year')
plt.xlabel('Year')
plt.ylabel('Number of Albums')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Visualization 2: Distribution of Performers and Their Number of Albums (Bar Chart)
performer_album_counts = albums_df['performerLabel'].value_counts()
plt.figure(figsize=(12, 6))
performer_album_counts.head(10).plot(kind='bar', color='lightcoral')
plt.title('Top 10 Performers and Their Number of Retro Albums')
plt.xlabel('Performer')
plt.ylabel('Number of Albums')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Visualization 3: Pie Chart Showing Distribution of Albums by Performer
performer_album_counts.head(10).plot(kind='pie', figsize=(8, 8), autopct='%1.1f%%', colors=sns.color_palette("pastel", 10))
plt.title('Top 10 Performers and Their Proportion of Albums')
plt.ylabel('')
plt.tight_layout()
plt.show()

# Visualization 4: Line Graph Showing Trend of Albums Released Over the Years
album_counts_by_year = albums_df.groupby('release_year').size()
plt.figure(figsize=(12, 6))
album_counts_by_year.plot(kind='line', marker='o', color='b', linestyle='-', linewidth=2, markersize=6)
plt.title('Trend of Retro Azerbaijani Albums Released Over the Years')
plt.xlabel('Year')
plt.ylabel('Number of Albums')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Visualization 5: Scatter Plot - Performers vs. Number of Albums
plt.figure(figsize=(12, 6))
sns.scatterplot(data=albums_df, x='performerLabel', y='release_year', hue='performerLabel', palette='Set2', s=100, legend=False)
plt.title('Scatter Plot: Performers vs Number of Albums')
plt.xlabel('Performer')
plt.ylabel('Release Year')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# In[ ]:




