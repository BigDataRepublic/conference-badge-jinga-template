# Conference Badge Template in Jinja

This is a Flask application that generates conference badges for attendees. It uses a 4-fold model and Jinja templating to create unique badges for each visitor.

## Usage

### Run the Flask Webserver with help of the Dockerfile

build & run `docker` image

```
docker build . -t template && docker run -it --name badge_template --rm -e FLASK_DEBUG="1" -e WEB_CONCURRENCY="2" -p 80:80 template
```

### Using & printing Badges;

- `/all_badges` can be used to view all badges, but is not recommended to use for printing (will result in large file)
- `/badge/1`, will print the first 25, `badge/2` the second 25 etc... This is re recommended way to print.
- `/empty_badge` can be used to print an empty badge.
- All remaining URL's are for info/debug purposes

### Important files & Settings

- `./data/visitors.csv` - `.CSV` file containing visitors name, email, and company
- `./data/breakout.csv` - `.CSV` file containing visitors signup for sattelite/workshop/breakout sessions
- `./data/email_mapping.yaml` - If previous are loosely linked, this `.yaml` can be used to manually link email adresses.
- `./templates/` - containing all Jinja Templates.

### Quicky Test new static files

```
docker cp app badge_template:/ 
```
Once the server is running, you can access the badge generator by navigating to localhost:80 (or the specified port number) in your web browser.

## Todo - use Prettier?

Currently `prettier` is not installed/supported but one could manually throw it with;
```
docker run --rm -it -v $(pwd):/vol node /bin/bash
```
Install `prettier`
```
npm install --global prettier
```

And apply with e.g.

```
prettier --write *
```
