from django import forms

INPUT_CLASS = ("block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm "
               "text-slate-900 shadow-sm outline-none transition focus:border-blue-500 "
               "focus:ring-2 focus:ring-blue-500/20")
CHECK_CLASS = "h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"


class TailwindModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = CHECK_CLASS if isinstance(field.widget, forms.CheckboxInput) else INPUT_CLASS
            field.widget.attrs.setdefault("class", css)
