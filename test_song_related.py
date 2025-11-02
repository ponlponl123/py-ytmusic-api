from ytmusicapi import YTMusic

yt = YTMusic()

# Test problematic song ID
song_id = "b3rFbkFjRrA"

print(f"Testing problematic song ID: {song_id}")

# Test 1: Direct get_song_related
try:
    related = yt.get_song_related(song_id)
    print("✅ Direct get_song_related: SUCCESS")
    print(f"Found {len(related)} related sections")
except Exception as e:
    print(f"❌ Direct get_song_related: FAILED - {e}")

# Test 2: Get song info first
try:
    song = yt.get_song(song_id)
    print(f"✅ get_song keys: {list(song.keys()) if song else 'None'}")
except Exception as e:
    print(f"❌ get_song: FAILED - {e}")

# Test 3: Try watch playlist approach
try:
    playlist = yt.get_watch_playlist(song_id)
    print(f"✅ get_watch_playlist keys: {list(playlist.keys()) if playlist else 'None'}")
    if playlist and 'related' in playlist:
        print("Has 'related' key in watch playlist")
        if playlist['related']:
            print(f"Related browse ID: {playlist['related']}")
except Exception as e:
    print(f"❌ get_watch_playlist: FAILED - {e}")

# Test 4: Try with MPLA prefix (common for browse IDs)
try:
    browse_id = f"MPLA{song_id}"
    related = yt.get_song_related(browse_id)
    print(f"✅ MPLA prefix worked! Found {len(related)} related sections")
except Exception as e:
    print(f"❌ MPLA prefix: FAILED - {e}")

# Test 5: Try with VL prefix (common for playlists)
try:
    browse_id = f"VL{song_id}"
    related = yt.get_song_related(browse_id)
    print(f"✅ VL prefix worked! Found {len(related)} related sections")
except Exception as e:
    print(f"❌ VL prefix: FAILED - {e}")