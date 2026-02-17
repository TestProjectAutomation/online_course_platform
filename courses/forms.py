from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Course, Category, CourseModule, Lesson, Review, Enrollment

# ==================== Tailwind CSS Classes ====================
TAILWIND_INPUT = 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition'
TAILWIND_SELECT = 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition'
TAILWIND_TEXTAREA = 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition'
TAILWIND_CHECKBOX = 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
TAILWIND_FILE = 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 dark:file:bg-primary-900 dark:file:text-primary-300'

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'البريد الإلكتروني'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'الاسم الأول'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'الاسم الأخير'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'اسم المستخدم'}),
            'phone_number': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'رقم الهاتف'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': TAILWIND_INPUT, 'placeholder': 'كلمة المرور'})
        self.fields['password2'].widget.attrs.update({'class': TAILWIND_INPUT, 'placeholder': 'تأكيد كلمة المرور'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'user'
        if commit:
            user.save()
        return user



class UserProfileForm(UserChangeForm):
    password = None  # إخفاء حقل كلمة المرور
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'bio', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full pr-10 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'placeholder': 'اسم المستخدم'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full pr-10 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'placeholder': 'الاسم الأول'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full pr-10 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'placeholder': 'الاسم الأخير'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full pr-10 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'placeholder': 'البريد الإلكتروني'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full pr-10 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'placeholder': 'رقم الهاتف'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'rows': 4,
                'placeholder': 'نبذة عن المستخدم...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full pr-10 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 dark:file:bg-primary-900 dark:file:text-primary-300'
            }),
        }


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full pr-10 px-4 py-3 bg-gray-50 dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:text-white transition group-hover:border-primary-300',
            'placeholder': 'أدخل اسم المستخدم أو البريد الإلكتروني'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pr-10 px-4 py-3 bg-gray-50 dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:text-white transition group-hover:border-primary-300',
            'placeholder': 'أدخل كلمة المرور'
        })
    )
    
    

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'category', 'description', 'short_description', 'image', 
                 'video_url', 'video_file', 'price', 'discount_percent', 
                 'discount_start_date', 'discount_end_date', 'level', 
                 'duration_hours', 'is_featured', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'عنوان الدورة'}),
            'category': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'description': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 6, 'placeholder': 'وصف مفصل للدورة'}),
            'short_description': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'وصف مختصر'}),
            'image': forms.FileInput(attrs={'class': TAILWIND_FILE}),
            'price': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'step': '0.01', 'placeholder': '0.00'}),
            'level': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'duration_hours': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'عدد الساعات'}),
            'is_featured': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'is_active': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'video_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'min': '0',
                'max': '100',
                'placeholder': '0'
            }),
            'discount_start_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'type': 'datetime-local'
            }),
            'discount_end_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'type': 'datetime-local'
            }),

        }
    def clean(self):
        cleaned_data = super().clean()
        video_url = cleaned_data.get('video_url')
        video_file = cleaned_data.get('video_file')
        cleaned_data = super().clean()
        discount_percent = cleaned_data.get('discount_percent')
        start_date = cleaned_data.get('discount_start_date')
        end_date = cleaned_data.get('discount_end_date')
        
        if discount_percent and discount_percent > 0:
            if not start_date or not end_date:
                raise forms.ValidationError("يجب تحديد تاريخ بداية ونهاية الخصم")
            if start_date >= end_date:
                raise forms.ValidationError("تاريخ النهاية يجب أن يكون بعد تاريخ البداية")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and not self.user.is_admin_user():
            self.fields['is_featured'].disabled = True
            self.fields['is_active'].disabled = True




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'img_gat', 'parent']  # تأكد من وجود img_gat هنا
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'placeholder': 'اسم التصنيف'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'rows': 3,
                'placeholder': 'وصف التصنيف'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition',
                'placeholder': 'fa-code, fa-chart-line, ...'
            }),
            'img_gat': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 dark:file:bg-primary-900 dark:file:text-primary-300'
            }),
            'parent': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition'
            }),
        }

                

class CourseModuleForm(forms.ModelForm):
    class Meta:
        model = CourseModule
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'عنوان الوحدة'}),
            'description': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 3, 'placeholder': 'وصف الوحدة'}),
            'order': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'الترتيب'}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'video_url', 'video_file', 'duration_minutes', 'content', 'order', 'is_free']
        widgets = {
            'title': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'عنوان الدرس'}),
            'video_url': forms.URLInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'https://www.youtube.com/...'}),
            'video_file': forms.FileInput(attrs={'class': TAILWIND_FILE}),
            'duration_minutes': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'المدة بالدقائق'}),
            'content': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 6, 'placeholder': 'محتوى الدرس النصي'}),
            'order': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'الترتيب'}),
            'is_free': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        video_url = cleaned_data.get('video_url')
        video_file = cleaned_data.get('video_file')
        
        if not video_url and not video_file:
            raise forms.ValidationError('يجب إما إضافة رابط فيديو أو رفع ملف فيديو')
        
        return cleaned_data

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f'{i} نجوم') for i in range(1, 6)],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': TAILWIND_TEXTAREA, 
                'rows': 4, 
                'placeholder': 'اكتب تقييمك هنا...'
            }),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': TAILWIND_TEXTAREA, 
                'rows': 3, 
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
        }


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ابحث عن دورات...',
            'aria-label': 'بحث'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )
    level = forms.ChoiceField(
        choices=[('', 'جميع المستويات')] + list(Course.LEVEL_CHOICES), 
        required=False, 
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )
    min_price = forms.DecimalField(
        required=False, 
        widget=forms.NumberInput(attrs={
            'class': TAILWIND_INPUT, 
            'placeholder': 'أقل سعر'
        })
    )
    max_price = forms.DecimalField(
        required=False, 
        widget=forms.NumberInput(attrs={
            'class': TAILWIND_INPUT, 
            'placeholder': 'أعلى سعر'
        })
    )