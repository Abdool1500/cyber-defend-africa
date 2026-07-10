class BootstrapFormMixin:
    """Adds Bootstrap 5 form-control/form-check classes to every field
    widget so forms don't render with raw default browser styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get("class", "")
            input_type = getattr(widget, "input_type", None)
            if input_type in ("checkbox", "radio"):
                css_class = "form-check-input"
            elif widget.__class__.__name__ == "Select":
                css_class = "form-select"
            else:
                css_class = "form-control"
            widget.attrs["class"] = (existing + " " + css_class).strip()
