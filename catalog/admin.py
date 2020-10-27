from django.contrib import admin
from catalog.models import Author, Genre, Book, Bookinstance, Language

# Register your models here.
#admin.site.register(Book)
admin.site.register(Genre)
#admin.site.register(Author)
#admin.site.register(Bookinstance)
admin.site.register(Language)


class BooksInstanceInline(admin.TabularInline):
    model = Bookinstance

class BookInline(admin.StackedInline):
    model = Book
    extra = 1

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


@admin.register(Bookinstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

    list_display = ('book', 'status', 'borrower', 'due_back', 'id')


#Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)
