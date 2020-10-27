from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, Language, Bookinstance, Genre
from django.views import generic

# Create your views here.
def index(request):
    # View function for home page of site

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = Bookinstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = Bookinstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    #context_object_name = 'my_book_list'    # your own name for the list as a template variable
    #queryset = Book.objects.filter(title__icontains='war')[:5]  # Get 5 books containing title war
    #template_name = 'books/my_arbitrary_template_name_list.html'    # Specify your own template name/location

    def get_queryset(self):
        return Book.objects.all()[:5]

    def get_context_date(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, primary_key):
        '''
        try:
            book = Book.objects.get(pk=primary_key)
        except Book.DoesNotExist:
            raise Http404('Book does not exist')
        '''
        book = get_object_or_404(Book, pk=primary_key)

        return render(request, 'catalog/book_detail.html', context={'book': book})

class AuthorListView(generic.ListView):
    model = Author

    def get_queryset(self):
        return Author.objects.all()[:5]

class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, primary_key):
        author = get_object_or_404(Author, pk=primary_key)
        return render(request, 'catalog/author_detail.html', context={'author': author})
