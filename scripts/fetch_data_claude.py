#!/usr/bin/env python3
"""
fetch_data_claude.py - Fetches data using Claude Code's MCP integration

This script fetches data and saves it for processing by other scripts.
"""

import json
import os
from datetime import datetime

print("Fetching student data from Google Sheets via Zapier MCP...")

# This will be executed by Claude Code with MCP access
# Fetch all student data