#!/usr/bin/env bash

# Generate a .env.dist file from an existing .env file by removing the values.
# Lines starting with a '#' are kept.

sed -r 's/([A-Z]+=).+/\1/g' < .env > .env.dist
