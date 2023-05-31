#!/bin/bash
source /opt/fts-lsmt/scripts/chisel/.env
chisel server --reverse --port 443 --tls-domain "$TLS_DOMAIN"