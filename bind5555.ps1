#Requires -RunAsAdministrator

Set-Location $PSScriptRoot
$port = python -m bluestacksv
./forward_adb.cmd $port