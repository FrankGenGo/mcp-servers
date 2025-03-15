#!/bin/bash

# Script to manage the MCP Docker Network

set -e

# Directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NETWORK_DIR="$(dirname "$SCRIPT_DIR")"
MCP_SERVERS_DIR="$(dirname "$NETWORK_DIR")"

# Colors for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Network name
NETWORK_NAME="mcp-docker-network"

# Function to show usage
function show_usage {
    echo -e "${YELLOW}Usage:${NC} $0 [create|remove|status|list-containers]"
    echo ""
    echo "Commands:"
    echo "  create             Create the Docker network"
    echo "  remove             Remove the Docker network"
    echo "  status             Show network status"
    echo "  list-containers    List containers connected to the network"
    echo ""
}

# Check if we have at least one argument
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

# Process commands
case "$1" in
    create)
        echo -e "${GREEN}Creating MCP Docker network...${NC}"
        # Check if network already exists
        if docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
            echo -e "${YELLOW}Network '$NETWORK_NAME' already exists.${NC}"
        else
            docker network create $NETWORK_NAME
            echo -e "${GREEN}Network '$NETWORK_NAME' created successfully.${NC}"
        fi
        ;;
    remove)
        echo -e "${RED}Removing MCP Docker network...${NC}"
        # Check if network exists before trying to remove
        if docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
            echo -e "${YELLOW}Warning: This will disconnect all containers from the network.${NC}"
            read -p "Are you sure you want to continue? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker network rm $NETWORK_NAME
                echo -e "${GREEN}Network '$NETWORK_NAME' removed successfully.${NC}"
            else
                echo -e "${YELLOW}Operation canceled.${NC}"
            fi
        else
            echo -e "${YELLOW}Network '$NETWORK_NAME' does not exist.${NC}"
        fi
        ;;
    status)
        echo -e "${GREEN}MCP Docker Network Status:${NC}"
        if docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
            echo -e "${BLUE}Network:${NC} $NETWORK_NAME"
            echo -e "${BLUE}Details:${NC}"
            docker network inspect $NETWORK_NAME | grep -A 4 "Name\|Driver\|IPAM\|Subnet\|Gateway"
        else
            echo -e "${YELLOW}Network '$NETWORK_NAME' does not exist.${NC}"
        fi
        ;;
    list-containers)
        echo -e "${GREEN}Containers connected to MCP Docker Network:${NC}"
        if docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
            # Extract container names from network inspect
            CONTAINERS=$(docker network inspect $NETWORK_NAME --format='{{range $k, $v := .Containers}}{{$k}} {{$v.Name}}
{{end}}')
            if [ -z "$CONTAINERS" ]; then
                echo -e "${YELLOW}No containers connected to the network.${NC}"
            else
                echo -e "${BLUE}Container ID\tName${NC}"
                echo "$CONTAINERS"
            fi
        else
            echo -e "${YELLOW}Network '$NETWORK_NAME' does not exist.${NC}"
        fi
        ;;
    *)
        show_usage
        ;;
esac