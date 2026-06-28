---
skill_id: 2ec04844fe79
usage_count: 1
last_used: 2026-06-16
---
## Input Validation

### Form Request Validation

```php
final class StorePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()?->can('create', Post::class) ?? false;
    }

    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255', 'sanitize_html'],
            'content' => ['required', 'string', 'max:10000'],
            'image' => [
                'required',
                'image',
                'mimes:jpg,jpeg,png,gif,webp', // Whitelist specific types
                'max:2048', // 2MB max
            ],
            'tags' => ['array'],
            'tags.*' => ['integer', 'exists:tags,id'],
        ];
    }

    public function messages(): array
    {
        return [
            'title.max' => 'Post title must not exceed 255 characters.',
            'image.max' => 'Image must be under 2MB.',
        ];
    }

    // Sanitize input after validation
    public function validated($key = null, $default = null): mixed
    {
        $validated = parent::validated();
        $validated['title'] = strip_tags($validated['title']);
        return $key ? ($validated[$key] ?? $default) : $validated;
    }
}
```

### Custom Validation Rules

```php
// app/Rules/StrongPassword.php
class StrongPassword implements Rule
{
    public function passes($attribute, $value): bool
    {
        return preg_match('/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()_\-+=])[A-Za-z\d@$!%*?&#^()_\-+=]{12,}$/', $value);
    }

    public function message(): string
    {
        return 'The :attribute must be at least 12 characters with uppercase, lowercase, number, and symbol.';
    }
}

// app/Rules/NotBlacklistedDomain.php
class NotBlacklistedDomain implements Rule
{
    private array $blacklisted = ['mailinator.com', 'guerrillamail.com'];

    public function passes($attribute, $value): bool
    {
        $domain = substr(strrchr($value, '@'), 1);
        return !in_array(strtolower($domain), $this->blacklisted);
    }

    public function message(): string
    {
        return 'Email from disposable domains is not allowed.';
    }
}
```