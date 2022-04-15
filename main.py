#!/usr/bin/env python3

import requests
import configparser

def authenticate():
	authUrl = 'https://accounts.spotify.com/api/token'
	data = {
		'grant_type': 'refresh_token',
		'refresh_token': f'{refreshToken}',
		'Content-Type': 'application/x-www-form-urlencoded',
		'client_id': f'{clientId}',
		'client_secret': f'{clientSecret}'
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
			with open(f'{outputFolder}/{playlist}.txt', 'w', encoding='utf-8') as f:
				print(result, end='', file=f)

config = configparser.ConfigParser()
config.read('config.ini')

playlists = config['main']['playlists'].split(", ")
outputFolder = config['main']['output_folder']
clientId = config['auth']['client_id']
clientSecret = config['auth']['client_secret']
refreshToken = config['auth']['refresh_token']

token = authenticate()
for p in playlists:
	processPlaylists(p, token)