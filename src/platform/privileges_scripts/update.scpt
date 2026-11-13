set sh1 to "launchctl unload /Library/LaunchDaemons/com.mydesk.MyDesk_service.plist;"
set sh2 to "launchctl unload /Library/LaunchAgents/com.mydesk.MyDesk_server.plist;"
set sh3 to "killall mydesk 2>/dev/null;"
set sh4 to "killall service 2>/dev/null;"
set sh5 to "sleep 1;"
set sh6 to "launchctl load -w /Library/LaunchDaemons/com.mydesk.MyDesk_service.plist;"
set sh7 to "launchctl load -w /Library/LaunchAgents/com.mydesk.MyDesk_server.plist;"
set sh to sh1 & sh2 & sh3 & sh4 & sh5 & sh6 & sh7
do shell script sh with prompt "MyDesk wants to update daemon and agent" with administrator privileges