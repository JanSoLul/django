from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from catalog.models import Book, Author, Language, Bookinstance, Genre
from catalog.forms import RenewBookForm
from django.contrib.auth.mixins import PermissionRequiredMixin
import datetime

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

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
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


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    # Generic class-based view listing books on load to current user.
    model = Bookinstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginated_by = 10

    def get_queryset(self):
        return Bookinstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = Bookinstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return Bookinstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    # 도서관 사서에 의해 특정 BookInstance를 갱신하는 view 함수
    book_instance = get_object_or_404(Bookinstance, pk=pk)

    # POST 요청이면 form 데이터를 처리한다.
    if request.method == 'POST':

        # Form Instance를 생성하고 요청에 의한 데이터로 채운다 (binding):
        book_renewal_form = RenewBookForm(request.POST)

        # Form이 유효한지 체크한다:
        if book_renewal_form.is_valid():
            # book_renewal_form.cleaned_data 데이터를 요청 받는대로 처리한다(여기선 그냥 모델 due_back 필드에 써넣는다.)
            book_instance.due_back = book_renewal_form.cleaned_data['renewal_date']
            book_instance.save()

            # 새로운 URL로 보낸다:
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        # GET 요청(혹은 다른 메소드)이면 기본 Form을 생성한다.
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author, Book

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}


class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
