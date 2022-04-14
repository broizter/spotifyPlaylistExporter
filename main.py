#!/usr/bin/env python3

import requests
import config

def authenticate():
	authUrl = 'https://accounts.spotify.com/api/token'
	data = {
		'grant_type': 'refresh_token',
		'refresh_token': f'{config.REFRESH_TOKEN}',
		'Content-Type': 'application/x-www-form-urlencoded',
		'client_id': f'{config.CLIENT_ID}',
		'client_secret': f'{config.CLIENT_SECRET}'
	}
	r = (requests.post(authUrl, data=data))
	token = r.json()['access_token']
	return token

def extractTracks(response):
	tracks = response['items']
	output = ''

	for t in tracks:
		unseparatedArtists = []
		searchArtists = t['track']['artists']
		for a in searchArtists:
			unseparatedArtists.append(a['name'])

		mySong = t['track']['name']
		myAlbum = t['track']['album']['name']
		myArtists = ', '.join(unseparatedArtists)

		output += f'{myArtists} - {myAlbum} - {mySong}\n'

	return output

def processPlaylists(playlist, token):
	headers = {
		'Authorization': f'Bearer {token}',
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	baseUrl = f'https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=items(track(name%2Cartists(name)%2Calbum(name))),next'
	doloop = True

	result = ''
	while doloop:
		r = requests.get(baseUrl, headers=headers) # curl
		response = r.json() # jq
		result += extractTracks(response)

		if response['next'] is not None:
			baseUrl = response['next']
		else:
			doloop = False
			with open(f'{config.OUTPUTFOLDER}/{playlist}.txt', 'w', encoding='utf-8') as f:
				print(result, end='', file=f)

token = authenticate()
for p in config.PLAYLISTS:
	processPlaylists(p, token)