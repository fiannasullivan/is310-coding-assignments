# Hide all dotfiles and dotfolders recursively from the current directory

Get-ChildItem -Recurse -Force |
Where-Object { $_.Name.StartsWith('.') } |
ForEach-Object {
    attrib +h $_.FullName
}