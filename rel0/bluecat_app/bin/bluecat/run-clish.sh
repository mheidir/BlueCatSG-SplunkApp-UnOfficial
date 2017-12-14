#!/bin/bash
CLISH_PATH='/usr/local/cli/debug;/usr/local/cli/adonis;/usr/local/cli/adonis_configure;/usr/local/cli/adonis_show;/usr/local/cli/common;/usr/local/cli/configure;/usr/local/cli/show'
export CLISH_PATH
clish $1
