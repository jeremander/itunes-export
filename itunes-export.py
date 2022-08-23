from libpytunes import Library
from libpytunes import Playlist
from pathlib import Path
import os
import argparse

parser = argparse.ArgumentParser(description="An utility application to export iTunes playlists in m3u format.")
parser.add_argument("--output", "-o", help="The outpout folder for exporting the playlists.", required=True)
parser.add_argument("--ignore", help="Ignore a specific playlist.", action='append')
parser.add_argument("--library", "-l", help="The path to the iTunes Library XML.", default=str(Path.home().joinpath("Music/iTunes/iTunes Music Library.xml")))
parser.add_argument("--relative-to", help="Make track paths relative to this.")
parser.add_argument("--export-genius-playlists", action='store_true', dest='exportGeniusPlaylists')
parser.add_argument("--export-smart-playlists", action='store_true', dest='exportSmartPlaylists')
args = parser.parse_args()

libraryPath = args.library
playlistRootPath = Path(args.output)
ignoreList = args.ignore if args.ignore is not None else []

def cleanupPlaylistName(playlistName):
    return playlistName.replace("/", "").replace("\\", "").replace(":", "")

def exportPlaylist(playlist: Playlist, parentPath: Path, relPath):
        relPath = relPath or parentPath
        if(playlist.is_genius_playlist and not args.exportGeniusPlaylists):
                return

        if(playlist.is_smart_playlist and not args.exportSmartPlaylists):
                return

        if(playlist.is_folder):
                # Create Folder
                currentPath = parentPath.joinpath(playlist.name)
                if(not currentPath.exists()):
                        currentPath.mkdir()

                for childPlaylist in playlists.values():
                        if(childPlaylist.parent_persistent_id == playlist.playlist_persistent_id):
                                exportPlaylist(childPlaylist, currentPath, relPath)
        else:
                playlistContent = ""
                for track in playlist.tracks:
                        if track.location:
                                try:
                                        trackPath = '/' + track.location
                                        playlistContent += os.path.relpath(trackPath, start=relPath) + "\n"
                                except ValueError:
                                        print("Warning: Could not add the track \"" + track.location + "\" as relative path to the playlist \"" + playlistName + "\"; added the track as absolute path instead.")
                                        playlistContent += track.location + "\n"

                playlistPath = parentPath.joinpath(cleanupPlaylistName(playlist.name) + ".m3u")
                if playlistContent:
                    playlistPath.write_text(playlistContent, encoding="utf8")
                else:
                    print(f'could not add playlist {playlistPath}')

playlists = {}

library = Library(libraryPath)
for playlistName in library.getPlaylistNames(ignoreList=[
        "Library", "Music", "Movies", "TV Shows", "Purchased", "iTunes DJ", "Podcasts", "Audiobooks", "Downloaded"
] + ignoreList):
    playlist = library.getPlaylist(playlistName)
    playlists[playlist.playlist_persistent_id] = playlist

for playlist in playlists.values():
    if (playlist.parent_persistent_id == None):
        exportPlaylist(playlist, playlistRootPath, args.relative_to)