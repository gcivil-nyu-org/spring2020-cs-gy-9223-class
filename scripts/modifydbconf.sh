#!/bin/bash

RED='\033[0;31m'          # Red
GREEN='\033[0;32m'        # Green
RESET='\033[0m'       # Text Reset
function __system {
    echo -e $GREEN$*$RESET
}
function __error {
    echo -e $RED$*$RESET
}
function __success {
    echo -e $GREEN"[OK] "$*$RESET
}
function __assert_exist {
    if command --help $1 > /dev/null; then
        __success $1
    else
        __error "[ERR] "$1
        echo ""
        __system "Please install "$1" first"
        __system $2
        exit 1
    fi
}

platform="unknown"

case "$OSTYPE" in
	darwin*) platform="OSX" ;;
	msys*)   platform="WINDOWS" ;;
	linux*)  platform="LINUX" ;;
	*)       ;;
esac

# Windows solution not provided 
if [[ "$platform" != "WINDOWS" ]]; then
    if [[ "$platform" == "OSX" ]]; then
        __assert_exist brew "https://docs.brew.sh/Installation"
        brew install gnu-sed --with-default-names | exit 1
        __success "brew install gnu-sed --with-default-names"
    fi

    if [[ -f ".env" ]]; then
        db_user=`cat .env | grep DB_USER= | grep -v '^#' | cut -d '=' -f2`    
        if [[ "$db_user" == "" ]]; then
            db_user="postgres"
        fi

        db_name='mercury'

        PGFILE=`pg_conftool -s 12 main show hba_file`
        sudo sed -i '1s/^/local\t '$db_name'\t '$db_user'\t trust\n /' $PGFILE || exit 1

        service postgresql restart
    else
        __error "[ERR]" "check your .env file!" 
    fi

fi