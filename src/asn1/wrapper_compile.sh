#!/bin/bash
gcc -o wrapper -Isrc/ -DPDU src/*.c wrapper.c -lm
