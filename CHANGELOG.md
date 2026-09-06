## 0.2.0 (2026-09-06)

### Feat

- **backgroundplayer**: add queue to background player and pagination
- **youtube**: update background player to use a new provider
- **autoplayer**: add queue to autoplayer modal
- **account**: update account page to also include updating webdav credentials
- **webdav**: add new webdav tag and rtk api to client
- **client**: add new generated schema files
- **client**: add new generate command to create rtk queries, move config to root, add new endpoints for webdav and admin
- **webdav**: add a check to ensure webdav server is reachable
- **settings**: add new test webdav variables
- **music**: add webdav upload to music tasks
- **webdav**: create new webdav endpoints for creating, deleting and updating
- **webdav**: create webdav model and migration

### Fix

- **user**: fix webdav and cookies not properly encrypting when handling updates
- **client**: fix type issues with react mutable ref
- **client**: fix react player import
- **authentication**: update session tokens to store token ids to jwts rather than the jwt itself to avoid large token headers
- **backgroundplayer**: fix slider being reset when video is watched
- **youtube**: fix bad prop in videosview
- **music**: fix auto player not tracking pause and play events
- **music**: sync player states to local react state
- **music**: fix auto player not going away when switching pages
- **music**: fix form not resetting after successfully starting a job
- **tasks**: only run scheduled tasks in production environment
- **music**: fix wrong extensions being used for base64 images
- **github-workflow**: fix env file placement from infisical
- **github-workflow**: fix env slug in infisical secrets
- **github-workflow**: fix infisical project slug
- **github-workflow**: fix variable interpolation when outputting to env file
- **webdav**: update request model to accept normal string
- **webdav**: fix file uploading to a connected webdav
- **webdav**: fix fernet key used in encryption
- **webdav**: add webdav router to app, remove return typing for tests
- **webdav**: fix user relationship for webdav instances
- **webdav**: fix migration file that was created
- **music**: fix downloading files from jobs leading to 0 byte files
- **client**: fix missing styles for mantine notifications and dropzone
- **music**: add failure handler for music jobs
- **music**: fix default artwork url for job card to use the correct asset url
- **websockets**: fix the wrong key being used to parse data from pub sub messages
- **music**: fix download filename when triggering a download
- **music**: fix creating a music job from sending a json instead of formdata
- **music**: fix download button url used to trigger a download
- **music**: fix generating filename for musicjob by using sanitize on specific strings rather than the entire name
- **music**: don't attempt to read file from form if there is no file

### Refactor

- **user**: move decrypting values and encrypting values into a single register function setup
- **client**: remove unused util causing build error
- **httpclient**: create new base async client to be used throughout the server
- **server**: update 422 references to use the new version
- **client**: adjust footer to instead toggle display instead of unmounting it
- **music**: convert video dialog to a custom overlay for seamless switching in expanding autoplayer
- **music**: rework auto player to sit in footer and to handle mobile layout
- **music**: rework the way auto player is displayed, introduce new footer provider
- **music**: use footer in mantine app shell and utilize portal to display video auto player
- **music**: replace isValidLink helper with url functions
- **webdav**: update exception handling for connecting to webdav to handle all exception cases
- **webdav**: update tests to use new fixture
- **conftest**: add new webdav pytest fixture
- **webdav**: update webdav tests to not decrypt values
- **webdav**: update endpoints and remove decrypt calls from webdav endpoints
- **webdav**: update model to automatically decrypt values on loading an instance
- **music**: remove download job endpoint
- **music**: update the way downloading works for music jobs
