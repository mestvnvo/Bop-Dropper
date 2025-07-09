# Bop Dropper
Dropping some EDM bops near you!

Paste in any song from this playlist!
https://open.spotify.com/playlist/2c8qTVOuNvJIl8UepuzHBb?si=8e68fd3da0b44dfe

## Notes

### Why? 
I recently started DJing and created this app for use in trying to find similar **EDM** songs through its musical elements and waveforms rather than just "important" factors like Key or Tempo.

### Next steps.
Songs need to be downloaded for them to be embedded and searched, and Spotify's API actually does NOT let you download music for ML purposes. 

While I had found a temporary "workaround" - Googling "spotify downloader" and attempting to use their APIs or using Playwright/Selenium to automate downloading songs - the owners of said API has added protection.

### Key Takeaways
1. Dockerized and deployed a live web app. DigitalOcean is so much cheaper than AWS.
2. ML computation is more intensive on hardware than I thought --> Pre-compute or use smaller models for demo purposes.
3. My definition of an API endpoints was misconstrued --> I'll work on this for the next project.
