#!/bin/bash

convert spritesheet.png -crop 16x16 parts-%02d.png
node rename.js
rm parts*.png
