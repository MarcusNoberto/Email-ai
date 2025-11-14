from django import forms

class EmailUploadForm(forms.Form):
    email_file = forms.FileField(
        required=False,
        label="Arquivo (.txt ou .pdf)"
    )
    email_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8, 'placeholder': 'Cole aqui o conteúdo do email...'}),
        required=False,
        label="Texto do email"
    )

    def clean(self):
        cleaned_data = super().clean()
        email_file = cleaned_data.get('email_file')
        email_text = cleaned_data.get('email_text')

        if not email_file and not email_text:
            raise forms.ValidationError("Envie um arquivo ou cole o texto do email.")

        if email_file:
            ext = email_file.name.split('.')[-1].lower()
            if ext not in ['txt', 'pdf']:
                raise forms.ValidationError("Apenas arquivos .txt ou .pdf são permitidos.")

        return cleaned_data
