---
skill_id: 0b0d979ef5ab
usage_count: 1
last_used: 2026-06-16
---
## Golden Files

Testing against expected output files stored in `testdata/`.

```go
var update = flag.Bool("update", false, "update golden files")

func TestRender(t *testing.T) {
    tests := []struct {
        name  string
        input Template
    }{
        {"simple", Template{Name: "test"}},
        {"complex", Template{Name: "test", Items: []string{"a", "b"}}},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Render(tt.input)

            golden := filepath.Join("testdata", tt.name+".golden")

            if *update {
                // Update golden file: go test -update
                err := os.WriteFile(golden, got, 0644)
                if err != nil {
                    t.Fatalf("failed to update golden file: %v", err)
                }
            }

            want, err := os.ReadFile(golden)
            if err != nil {
                t.Fatalf("failed to read golden file: %v", err)
            }

            if !bytes.Equal(got, want) {
                t.Errorf("output mismatch:\ngot:\n%s\nwant:\n%s", got, want)
            }
        })
    }
}
```