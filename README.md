# go_call_graph
### Author: Justin Salsbery
Generate a gv formatted call graph for Golang.
## Install/Uninstall:
- make install
- make uninstall
## Use:
- flow {--paths [path] | --source path} (--filter [function])
## Examples:
- flow --paths main.go > out.gv
- flow --paths $(find . -name "*.go") --filter GLOBAL main > out.gv
- flow --source out.gv --filter new > out.gv
