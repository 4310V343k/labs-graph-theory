from pathlib import Path

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import ValidationError, Validator
from rapidfuzz import process


class IntValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text:
            return

        try:
            int(text)
        except ValueError:
            i = 0

            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message="Ввод должен быть целым числом", cursor_position=i)


class FloatValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text:
            return

        try:
            float(text)
        except ValueError:
            i = 0

            found_dot = False
            for i, c in enumerate(text):
                if c.isdigit():
                    continue
                if c == "." and not found_dot:
                    found_dot = True
                    continue
                break

            raise ValidationError(message="Ввод должен быть вещественным числом", cursor_position=i)


class FileNameValidator(Validator):
    def validate(self, document):
        text = document.text

        if text and not Path(text).is_file():
            raise ValidationError(message="Ввод должен быть названием существующего файла")


class FuzzyFileCompletion(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        if text.endswith("/"):
            base = Path(text)
            # prefix = text
            partial_name = ""
        else:
            p = Path(text)
            parent = p.parent if str(p.parent) not in (".", "") else Path(".")

            base = parent if p.is_absolute() else (Path(".") / parent)
            # prefix = "" if str(parent) in (".", "") else str(parent) + "/"
            partial_name = p.name

        candidates = list(base.iterdir())

        matches = process.extract(
            partial_name,
            [c.name + ("/" if c.is_dir() else "") for c in candidates],
            limit=None,
            score_cutoff=40,
        )

        for match, _, _ in matches:
            yield Completion(match, start_position=-len(partial_name))
