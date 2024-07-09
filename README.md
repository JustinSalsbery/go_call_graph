# go_call_graph
### Author: Justin Salsbery
Basic call graph for Golang using static analysis. Call graph output to "out.gz" in Graphviz dot format.
## Use:
- python3 main.py <files.go>
## Example:
- python3 main.py main.go
- python3 main.py $(find ../example -name "*.go" -not -path "*vendor*" -not -name "_test.go")
    - cat out.gv | grep -v -e Println -e Printf > out.gv
