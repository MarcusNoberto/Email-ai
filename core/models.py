from django.db import models

class EmailAnalysis(models.Model):
    CATEGORY_CHOICES = [
        ('produtivo', 'Produtivo'),
        ('improdutivo', 'Improdutivo'),
    ]

    original_text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    suggested_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email ({self.get_category_display()}) - {self.created_at:%d/%m/%Y %H:%M}"
