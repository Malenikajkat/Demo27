# Документация: app/blueprints/puzzle_captcha.py

## Назначение

Файл `app/blueprints/puzzle_captcha.py` реализует **API для пазл-капчи**. Предоставляет эндпоинты для генерации, получения фрагментов, получения образца и проверки сборки пазла.

## Blueprint

```python
puzzle_captcha_bp = Blueprint("puzzle_captcha", __name__)
```

Регистрируется с префиксом `/api/captcha` (предполагаемо, хотя url_prefix не указан явно).

## Зависимости

```python
from PIL import Image
import io
from app.puzzle_captcha import puzzle_captcha
```

Использует глобальный экземпляр `PuzzleCaptcha` из `app/puzzle_captcha.py`.

## Маршруты (Endpoints)

### 1. `GET /api/captcha/generate` — Генерация капчи

**Функция**: `generate()`

**Ответ 200**:
```json
{
    "token": "abc123...",
    "fragments": ["data:image/png;base64,...", ...],
    "grid_size": 2,
    "correct_order": [0, 1, 2, 3],
    "num_pieces": 4,
    "reference_image": "data:image/png;base64,..."
}
```

**Ответ 500**:
```json
{
    "error": "Internal Server Error",
    "message": "Ошибка генерации: ..."
}
```

### 2. `GET /api/captcha/fragment/<token>/<index>` — Фрагмент изображения

**Функция**: `get_fragment(token, index)`

**Параметры**:
| Параметр | Тип | Описание |
|----------|-----|----------|
| `token` | str | Токен капчи |
| `index` | int | Индекс фрагмента |

**Ответ**: Изображение PNG (`Content-Type: image/png`)

**Заголовки**:
- `Cache-Control: no-cache, no-store, must-revalidate`
- `Access-Control-Allow-Origin: *`

**Ответ 404**:
```json
{
    "error": "Fragment not found"
}
```

### 3. `GET /api/captcha/reference/<token>` — Образец пазла

**Функция**: `get_reference(token)`

**Параметры**:
| Параметр | Тип | Описание |
|----------|-----|----------|
| `token` | str | Токен капчи |

**Ответ**: Изображение PNG (собранный пазл)

**Ответ 404**:
```json
{
    "error": "Reference not found"
}
```

### 4. `POST /api/captcha/verify` — Проверка сборки

**Функция**: `verify()`

**Тело запроса**:
```json
{
    "token": "abc123...",
    "fragment_order": [0, 1, 2, 3]
}
```

**Ответ 200**:
```json
{
    "valid": true,
    "message": "Пазл собран верно"
}
```

или

```json
{
    "valid": false,
    "message": "Пазл собран неверно"
}
```

**Ответ 400**:
```json
{
    "error": "Bad Request",
    "message": "Укажите token и fragment_order"
}
```

## Ключевая логика

### Обработка изображений
Все эндпоинты, возвращающие изображения:
1. Конвертируют RGBA в RGB с белым фоном
2. Сохраняют в BytesIO как PNG
3. Возвращают через `Response` с `mimetype="image/png"`

### Одноразовое использование
После проверки капча удаляется из `puzzle_captcha.challenges`.

### CORS
Эндпоинт фрагмента разрешает cross-origin запросы (`Access-Control-Allow-Origin: *`).

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/puzzle_captcha.py` | Использует | `PuzzleCaptcha` класс |
| `PIL.Image` | Зависимость | Обработка изображений |
| `web/login.html` | Использует | Фронтенд капчи |
| `app/blueprints/web.py` | Использует | Проверка капчи при входе |

## Важные замечания

1. **Два формата ответа**: JSON для generate/verify, PNG для fragment/reference.
2. **Кэширование**: Запрещено для изображений (`no-cache, no-store`).
3. **CORS**: Разрешены cross-origin запросы для фрагментов.
4. **Обработка ошибок**: try/except для всех эндпоинтов.
