:: Need Run As Admin
::>Add rule
netsh interface portproxy add v4tov4 listenport=5555 connectaddress=localhost connectport=%1
::>Delete rule
:: netsh interface portproxy delete v4tov4 listenport=5555
::>Check rule
:: netsh interface portproxy show v4tov4
