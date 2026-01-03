#!/bin/bash
# Setup aliases for easy JDownloader control
# Source this file in your ~/.bashrc: source /home/ght/project/jd2-controller/aliases.sh

# JDownloader control aliases
alias jd-start='cd /home/ght/project/jd2-controller && ./start_headless.sh'
alias jd-stop='cd /home/ght/project/jd2-controller && ./jdctl stop'
alias jd-restart='cd /home/ght/project/jd2-controller && ./jdctl restart'
alias jd-status='cd /home/ght/project/jd2-controller && ./jdctl status'
alias jd-verify='cd /home/ght/project/jd2-controller && ./jdctl verify'
alias jd-logs='cd /home/ght/project/jd2-controller && ./jdctl logs'
alias jd-follow='cd /home/ght/project/jd2-controller && ./jdctl logs --follow'

# Quick access
alias jd='cd /home/ght/project/jd2-controller && ./jdctl'

echo "✅ JDownloader aliases loaded:"
echo "   jd-start    - Start JDownloader with verification"
echo "   jd-stop     - Stop JDownloader"
echo "   jd-restart  - Restart JDownloader"
echo "   jd-status   - Show status"
echo "   jd-verify   - Verify cloud connection"
echo "   jd-logs     - View logs"
echo "   jd-follow   - Follow logs in real-time"
echo "   jd <cmd>    - Run jdctl command"
