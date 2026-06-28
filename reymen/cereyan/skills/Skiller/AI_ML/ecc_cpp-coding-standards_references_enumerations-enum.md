
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Cpp Coding Standards_References_Enumerations Enum |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Enumerations (Enum.*)

### Key Rules

| Rule | Summary |
|------|---------|
| **Enum.1** | Prefer enumerations over macros |
| **Enum.3** | Prefer `enum class` over plain `enum` |
| **Enum.5** | Don't use ALL_CAPS for enumerators |
| **Enum.6** | Avoid unnamed enumerations |

```cpp
// Enum.3 + Enum.5: Scoped enum, no ALL_CAPS
enum class Color { red, green, blue };
enum class LogLevel { debug, info, warning, error };

// BAD: plain enum leaks names, ALL_CAPS clashes with macros
enum { RED, GREEN, BLUE };           // Enum.3 + Enum.5 + Enum.6 violation
#define MAX_SIZE 100                  // Enum.1 violation -- use constexpr
```