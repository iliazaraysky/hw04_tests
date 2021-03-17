from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
import random

from posts.models import Group, Post

User = get_user_model()


class ProjectViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Лев Толстой',
            slug='tolstoy',
            description='Группа Льва Толстого',
        )

        cls.author = User.objects.create_user(
            username='authorForPosts',
            first_name='Тестов',
            last_name='Теcтовский',
            email='testuser@yatube.ru'
        )

        for i in range(1, 14):
            cls.post = Post.objects.create(
                group=ProjectViewsTests.group,
                text="Какой-то там текст",
                author=User.objects.get(username='authorForPosts'),
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestForTest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""

        templates_page_names = {
            'index.html': reverse('index'),
            'newpost.html': reverse('new_post'),
            'group.html': (reverse('group', kwargs={'slug': 'tolstoy'})),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context(self):
        """Форма добавления материала сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_context_in_profile(self):
        """Проверка содержимого словаря context для /<username>/"""
        url = reverse('profile', args=[self.author.username])
        response = self.authorized_client.get(url)
        post = response.context['page'][0]
        author = response.context['author']
        post_text_0 = post.text
        post_author_0 = author.first_name
        self.assertEqual(post_author_0, 'Тестов')
        self.assertEqual(post_text_0, 'Какой-то там текст')

    def test_context_in_post_edit(self):
        """
        Проверка содержимого словаря context
        для /<username>/<post_id>/edit/
        """
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

        lst_id = Post.objects.filter(author=self.author).values_list('id',
                                                                     flat=True)
        url = reverse('post_edit', args=[self.author.username,
                                         random.choice(lst_id)])
        response = self.authorized_client.get(url)
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_id_correct_context(self):
        """Проверка содержимого context отдельного поста"""
        lst_id = Post.objects.filter(author=self.author).values_list('id',
                                                                     flat=True)
        url = reverse('post', args=[self.author.username,
                                    random.choice(lst_id)])
        response = self.authorized_client.get(url)
        post = response.context['full_post']
        author = response.context['author']
        post_text_0 = post.text
        post_author_0 = author.first_name
        self.assertEqual(post_author_0, 'Тестов')
        self.assertEqual(post_text_0, 'Какой-то там текст')

    def test_home_page_show_correct_context(self):
        """Пост отображается на главной странице"""
        response = self.authorized_client.get('/')
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Какой-то там текст')
        self.assertEqual(post_group_0, 'Лев Толстой')

    def test_group_page_show_correct_context(self):
        """Пост отображается на странице группы"""

        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'tolstoy'}))
        first_object = response.context['posts'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Какой-то там текст')
        self.assertEqual(post_group_0, 'Лев Толстой')

    def test_first_page_containse_ten_records(self):
        """Колличество постов на первой странице равно 10"""

        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.guest_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_about_uses_correct_template(self):
        """
        URL-адреса (/about/author/ и /about/tech/)
        использует соответствующий шаблон
        """
        templates_page_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
