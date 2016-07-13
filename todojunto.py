#!/usr/bin/python
import m3u8
from lxml import html
import lxml.html
import requests
import ast
from subprocess import call
import string

url_serie = 'http://cda.gob.ar/serie/1134/quien-mato-al-bebe-uriarte-'

#Si debug es 0 omite los mensajes 
debug = 0
descargar = 1

def busca_capitulos(serie):
    urlbase = "http://www.cda.gob.ar"
    
    #Extrae Lista de Capitulos de una serie dada
    page = requests.get(serie)
    tree = html.fromstring(page.content)
    
    capitulos = tree.xpath('//meta[@itemprop="url"]')
    
    #<meta itemprop="url" content="/serie/6551/cromo#!/6771/cap01">
    #//meta[@itemprop="url"]/text()
    
    urlcapitulos = []
    for capitulo in capitulos:
        texto = lxml.html.tostring(capitulo)
        url = texto.split('content="')[1].split('"')[0]
        urlcompleta = urlbase + url
        print urlcompleta
        urlcapitulos.append(urlcompleta)
    
    #print "\nTodos:"
    #print urlcapitulos
    return urlcapitulos

def video_id_from_capitulo(url_capitulo):
    #Obtiene VideoId haciendo request a webservice
    clip_id = url_capitulo.split('!/')[1].split('/')[0]
    #print clip_id
    url = "http://cda.gob.ar/clip/ajax/" + clip_id
    page = requests.get(url)
    texto = page.content
    dicc = ast.literal_eval(texto)
    video_id = dicc.get("video_id")
    return video_id

def video_title_from_capitulo(url_capitulo):
    #Obtiene Title haciendo request a webservice
    clip_id = url_capitulo.split('!/')[1].split('/')[0]
    #print clip_id
    url = "http://cda.gob.ar/clip/ajax/" + clip_id
    page = requests.get(url)
    texto = page.content
    dicc = ast.literal_eval(texto)
    title = dicc.get("title")
    return title


# A partir de la url_capitulo de tipo http://www.cda.gob.ar/serie/6551/cromo#!/6914/cap05
# obtiene http://186.33.226.132/vod/smil:content/videos/clips/1234.smil/playlist.m3u8
def playlist_from_capitulo(url_capitulo):
    
    #Extrae URL Playlist desde un capitulo dado <-- Obsoleto ya que siempre obtiene del trailer
    #page = requests.get(url_capitulo)
    #tree = html.fromstring(page.content)    
    #player = tree.xpath('//*[@id="video"]/script')
    #textoScript = lxml.html.tostring(player[0])
    #print textoScript
    #playlistCapitulo = textoScript.split('file:"')[1].split('"}]')[0]

    #Nueva forma:
    video_id =  video_id_from_capitulo(url_capitulo)
    playlistCapitulo = "http://186.33.226.132/vod/smil:content/videos/clips/" + video_id +".smil/playlist.m3u8"
    
    if debug:
        print "\nCapitulo: " + url_capitulo
        print "Playlist completa:"
        print playlistCapitulo

    return playlistCapitulo

def calidad2m_from_playlist(url_playlist):
    #Extrae la url a la mejor calidad de una Playlist dada
    variant_m3u8 = m3u8.load(url_playlist)

    #print variant_m3u8.is_variant    # in this case will be True

    playlist2m = ""
    for playlist in variant_m3u8.playlists:
        #print playlist.uri
        #print playlist.stream_info.bandwidth
        if (playlist.stream_info.bandwidth >= 2000000):
            playlist2m = playlist.base_uri + playlist.uri
            if debug:
                print url_playlist
                print playlist.uri
                print "\nPlaylist 2M:"
                print playlist2m
    return playlist2m



capitulos = busca_capitulos(url_serie)

if debug:
    print capitulos

enlaces = []
for url_capitulo in capitulos:
    #print url
    playlist = playlist_from_capitulo(url_capitulo)
    calidad2m = calidad2m_from_playlist(playlist)
    title = video_title_from_capitulo(url_capitulo)
    datos = [title, calidad2m]
    enlaces.append(datos)

if debug: 
    print enlaces

for enlace in enlaces:
    print enlace

if descargar:
    i= 0
    for enlace in enlaces:
        i=i+1
        print enlace
        video = enlace[1]
        salida = enlace[0] + " - " + str(i) +".mp4"
        if 1:#debug:
            print video 
            print salida
        call(["ffmpeg", "-i", video, "-c", "copy", "-bsf:a", "aac_adtstoasc", salida])
    
