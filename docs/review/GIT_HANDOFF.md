# Передача Git-ветки

Ветка с выполненной работой: `review/student`.

В ZIP-архиве исходного проекта не было каталога `.git/`, поэтому история GitHub не могла быть продолжена. Для практики создан локальный репозиторий с базовым импортным коммитом, веткой ревью и отдельными коммитами по дням/исправлениям.

## Перед отправкой на GitHub

1. При необходимости переименовать ветку под фамилию:
   `git branch -m review/<фамилия>`
2. Настроить имя и email автора для следующих коммитов:
   `git config user.name "Ваше имя"`
   `git config user.email "ваш-email"`
3. Создать fork репозитория `Malenikajkat/Demo27` в своём аккаунте (если у вас нет права записи в исходный репозиторий) и добавить его как `origin`:
   `git remote add origin https://github.com/<ваш-логин>/Demo27.git`
4. Отправить ветку:
   `git push -u origin review/<фамилия>`
5. На GitHub создать Pull Request из своей ветки в `Malenikajkat/Demo27:master`. Если преподаватель выдал право записи в исходный репозиторий, вместо URL fork можно использовать исходный URL.

## Импорт Git-истории из bundle

Если передаётся файл `Demo27_review.bundle`, историю можно восстановить командой:

`git clone --branch review/student Demo27_review.bundle Demo27`

После клонирования добавить `origin` и отправить ветку на GitHub.

**Важно:** в созданных коммитах использован технический автор `Review Student <review@student.local>`. При необходимости авторство следует заменить согласно требованиям преподавателя. Push и Pull Request в рамках этой сессии не выполнялись.


## Important note about the imported source snapshot

The supplied ZIP already contained several code fixes and regression tests, but it did not contain `.git/`. Their original commit boundaries and authors cannot be reconstructed honestly. The local history therefore starts with an explicitly named import commit, then records the five practice-day review artifacts and the additional changes made during this preparation. Do not present the import commit as the original upstream history.

Before pushing, use your own name and email for any new commits. The existing local commits use the technical author `Review Student <review@student.local>`. If your instructor requires personal authorship for every commit, rewrite the local commit authors before the first push.
