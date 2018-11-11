#!/usr/bin/env python3

import getpass
from plexapi.myplex import MyPlexAccount

username = input("plex-scripts Username: ")
server = input("plex-scripts Server: ")
password = getpass.getpass()

account = MyPlexAccount(username, password)
plex = account.resource(server).connect()

movies = plex.library.section('Movies')
collections = {c.title: c.fetchItems(c.fastKey) for c in movies.listChoices('collection')}

for collection, movies in collections.items():
    if len(movies) < 3:
        for movie in movies:
            movie.removeCollection(collection)
            print('Removed {} from {}'.format(movie.title, collection))
