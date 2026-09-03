from django import forms

INPUT_CLASS = "block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
CHOICE_CLASS = "h-4 w-4 border-slate-300 text-blue-700 focus:ring-blue-500"


class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                CHOICE_CLASS if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)) else INPUT_CLASS,
            )
