---
skill_id: 35b592084cbf
usage_count: 1
last_used: 2026-06-16
---
## Focus Management

Focus must move logically when UI state changes — especially for modals and route transitions.

### Modal Focus Restoration

> This example covers initial focus and restoration. For a full focus trap (Tab/Shift+Tab cycling within the modal), use a library like [`focus-trap-react`](https://github.com/focus-trap/focus-trap-react) which handles edge cases like dynamic content and nested portals.

```tsx
export function Modal({ isOpen, onClose, title, children }: { isOpen: boolean; onClose: () => void; title: string; children: React.ReactNode }) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Save currently focused element and move focus into modal
      previousFocusRef.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      // Restore focus to the element that opened the modal
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div ref={modalRef} role="dialog" aria-modal="true" aria-labelledby="modal-title" tabIndex={-1} onKeyDown={e => e.key === 'Escape' && onClose()}>
      <h2 id="modal-title">{title}</h2>
      {children}
      <button onClick={onClose}>Close</button>
    </div>
  );
}
```