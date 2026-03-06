---
name: add-to-portfolio-app
description: 
    🟢 Adds a new Talk or Article to Riccardo personal portfolio application. This is a placeholder and needs to be filled out.
---
# Add to Portfolio App Skill

This skill allows the agent to add a new project to a portfolio application.

## Description

Adds a new Talk or Article from Riccardo to a portfolio application.

The goal is to add this information to:

1. https://portfolio-app-272932496670.europe-west1.run.app/about

## Usage

Activate this skill when the user wants to add a new project to their portfolio or simply pings you a link to something they did (youtube video, article written, ...)

## Instructions for Apps Portfolio

1.  Go to `~/git/vibecoding/apps-portfolio` and read GEMINI.md instructions there. Basically, this means adding the new article/info onto `etc/data.yaml` and running a script to update the sqlite DB. 
2.  Run tests -> `git commit` -> `git push`.
3.  Notify user to look in 5 minutes for a new page in https://portfolio-app-272932496670.europe-west1.run.app/ (better if you say which page)

## Instructions for My sessions and Bio

I also have a github repo with a list of my articles and event to which I go.

* go to `~/git/my-sessions-and-bio/`
* Select the most pertinent file: `code-projects.md`, `oss-contributions.md`, `talks.md` , or `workshops.md`.
* Add the info to that file in proper datetime order, English language, and with the right.
* If important info is missing, prompt user for it.

**Note**. Consider also Googling for "Riccardo Carlesso <other info>". You might find some youtube video about a presentation, would be nice to attach it.

## Gcloud troubleshooting

If the repo online doesn't show data, ensure user has:

* auth: `gcloud auth login --update-adc`
* test it works: `gcloud auth application-default print-access-token`
* Ask user to check builds on Cloud Build Dashboard: https://console.cloud.google.com/cloud-build/builds?project=PROJECT_ID


## Resources
- `~/git/vibecoding/apps-portfolio/`
- `~/git/my-sessions-and-bio/`
