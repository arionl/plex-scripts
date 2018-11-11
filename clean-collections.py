#!/usr/bin/env python3

'''

Collections is cool but Plex auto-creates them, even when where is only one movie in a collection.
You can turn this off, but when you have to create *all* collections by hand.. I figured I'd leave it on and then
just prune the extra collections once in a while.. at least that was the thought for this script (picked up most of
it from a Reddit thread).

'''

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
