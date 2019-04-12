# Profanity Filter

A simple filter that checks for profanity in a message and then deletes it. Many profanity detection libraries use a hard-coded list of bad words to detect and filter profanity, however this plugin utilises a library that uses a linear support vector machine (SVM) model trained on 200k human-labeled samples of clean and profane text strings. ([`profanity-check`](https://github.com/vzhou842/profanity-check)).

Artificial intelligence in a discord bot? Heck yeah!

## Installation

`?plugins add kyb3r/modmail-plugins/profanity-filter`