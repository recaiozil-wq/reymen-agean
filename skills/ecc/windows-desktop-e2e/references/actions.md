---
skill_id: ebb67a4271ab
usage_count: 1
last_used: 2026-06-16
---
# --- Actions ---

    def click(self, spec):
        self.wait_visible(spec)
        spec.click_input()

    def type_text(self, spec, text):
        self.wait_visible(spec)
        ctrl = spec.wrapper_object()
        try:
            ctrl.set_edit_text(text)
        except Exception as e: