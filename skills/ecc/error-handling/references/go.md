---
skill_id: 34d1f91fb2e5
usage_count: 1
last_used: 2026-06-16
---
## Go

### Sentinel Errors and Error Wrapping

```go
package domain

import "errors"

// Sentinel errors for type-checking
var (
    ErrNotFound    = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrConflict     = errors.New("conflict")
)

// Wrap errors with context — never lose the original
func (r *UserRepository) FindByID(ctx context.Context, id string) (*User, error) {
    user, err := r.db.QueryRow(ctx, "SELECT * FROM users WHERE id = $1", id)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, fmt.Errorf("user %s: %w", id, ErrNotFound)
    }
    if err != nil {
        return nil, fmt.Errorf("querying user %s: %w", id, err)
    }
    return user, nil
}

// At the handler level, unwrap to determine response
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.GetUser(r.Context(), chi.URLParam(r, "id"))
    if err != nil {
        switch {
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "not_found", err.Error())
        case errors.Is(err, domain.ErrUnauthorized):
            writeError(w, http.StatusForbidden, "forbidden", "Access denied")
        default:
            slog.Error("unexpected error", "err", err)
            writeError(w, http.StatusInternalServerError, "internal_error", "An unexpected error occurred")
        }
        return
    }
    writeJSON(w, http.StatusOK, user)
}
```