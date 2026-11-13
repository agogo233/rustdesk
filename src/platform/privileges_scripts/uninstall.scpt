set sh1 to "launchctl unload /Library/LaunchDaemons/com.mydesk.MyDesk_service.plist;"
set sh2 to "launchctl unload /Library/LaunchAgents/com.mydesk.MyDesk_server.plist;"
set sh3 to "/bin/rm -f /Library/LaunchDaemons/com.mydesk.MyDesk_service.plist /Library/LaunchAgents/com.mydesk.MyDesk_server.plist;"
set sh to sh1 & sh2 & sh3
do shell script sh with prompt "MyDesk wants to uninstall daemon and agent" with administrator privileges