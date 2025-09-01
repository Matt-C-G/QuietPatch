# QuietPatch macOS (offline agent)

## Install (90 seconds)
1) Extract:
   sudo tar -C / -xzf quietpatch-0.2.1-macos-pex.tar.gz
2) Install files and service:
   sudo /bin/bash -c 'set -e
     install -d -m 0755 /usr/local/quietpatch /var/lib/quietpatch /var/log/quietpatch
     install -m 0755 macos/quietpatch.pex             /usr/local/quietpatch/
     install -m 0755 macos/run_quietpatch.sh          /usr/local/quietpatch/
     install -m 0644 macos/com.quietpatch.agent.plist /Library/LaunchDaemons/
     launchctl bootout system /Library/LaunchDaemons/com.quietpatch.agent.plist 2>/dev/null || true
     launchctl bootstrap system /Library/LaunchDaemons/com.quietpatch.agent.plist
     launchctl enable system/com.quietpatch.agent
     launchctl kickstart -k system/com.quietpatch.agent'
3) Set your AGE recipient (optional but recommended):
   export QP_AGE_RECIPIENT=age1... ; # add to /etc/launchd.conf env or wrapper as needed

## Use
- Service runs on schedule and writes to /var/lib/quietpatch/.
- Report: open /var/lib/quietpatch/report.html

## Uninstall
sudo launchctl bootout system /Library/LaunchDaemons/com.quietpatch.agent.plist
sudo rm -f /Library/LaunchDaemons/com.quietpatch.agent.plist
sudo rm -rf /usr/local/quietpatch /var/lib/quietpatch /var/log/quietpatch
