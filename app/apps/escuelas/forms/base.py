INPUT_CLASS = "block w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"

def aplicar_estilos_campos(fields):
    for field in fields.values():
        field.widget.attrs.setdefault("class", INPUT_CLASS)
