from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
import random
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
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

        for i in range(1, 5):
            cls.post = Post.objects.create(
                group=StaticURLTests.group,
                text="Какой-то там текст",
                author=User.objects.get(username='authorForPosts')
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='testfortest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_list(self):
        """
        Тестирование по списку, для анонимного пользователя,
        список URL, где ответ должен быть равен 200
        """

        url_list = ['/', '/group/tolstoy']
        for test_url in url_list:
            response = self.guest_client.get(test_url)
            self.assertEqual(response.status_code, 200)

    def test_response_anon_username_url(self):
        """
        Проверка доступности анонимным пользователем,
        страницы профиля пользователя
        """

        url = reverse('profile', args=[self.user.username])
        response = self.guest_client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_response_anon_username_post_url(self):
        """
        Проверка доступности анонимным пользователем,
        страницы с постом автора
        """

        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post', args=[self.user.username,
                                    random.randint(1, total_number_of_id)])
        response = self.guest_client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_redirect_anon_username_edit_post_url(self):
        """
        Проверка редиректа анонимного пользователя, при обращении
        к странице редактирования поста
        """

        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post_edit',
                      args=[self.user.username, total_number_of_id])
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_redirect_author_username_edit_post_url(self):
        """
        Проверка доступности страницы редактирования поста, при обращении
        автора
        """

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post_edit',
                      args=[self.user.username, total_number_of_id])
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_redirect_not_author_username_edit_post_url(self):
        """
        Проверка редиректа при обращении к странице редактирования поста,
        авторизированным пользователем, не автором
        """

        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post_edit',
                      args=[self.user.username, total_number_of_id])
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_new_page_not_login_user(self):
        """Страница доступна авторизированному пользователю"""

        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug_response_not_login_user(self):
        """Проверка доступности созданной группы для всех пользователей"""

        response = self.guest_client.get('/group/tolstoy')
        self.assertEqual(response.status_code, 200)

    def test_new_page_not_login_user(self):
        """
        Страница создания нового поста,
        перенаправляет анонимного пользователя
        """

        response = self.guest_client.get('/new')
        self.assertEqual(response.status_code, 302)

    def test_new_page_login_user(self):
        """Главная страница доступна авторизированному пользователю"""

        response = self.authorized_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug_response_login_user(self):
        """
        Проверка доступности созданной группы
        для авторизированных пользователей
        """

        response = self.authorized_client.get('/group/tolstoy')
        self.assertEqual(response.status_code, 200)

    def test_new_page_login_user(self):
        """Страница доступна авторизированному пользователю"""

        response = self.authorized_client.get('/new')
        self.assertEqual(response.status_code, 200)

    def test_new_page_not_login_user_redirect(self):
        """Страница перенаправляет анонимного пользователя"""

        response = self.guest_client.get('/new', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""

        template_url_names = {
            'index.html': '/',
            'group.html': '/group/tolstoy',
            'newpost.html': '/new',
        }
        for template, reverse_name in template_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_edit_post(self):
        """
        Проверка. Какой шаблон вызывается при обращении к странице
        редактирования поста
        """

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post_edit',
                      args=[self.user.username, total_number_of_id])
        template_url_names = {'newpost.html': url}

        for template, reverse_name in template_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_about_and_tech_exist_all_users(self):
        """
        URL-адреса (/about/author/ и /about/tech/)
        доступны любому пользователю
        """
        urls_exist = [reverse('about:author'), reverse('about:tech')]

        for exist in urls_exist:
            with self.subTest():
                response = self.authorized_client.get(exist)
                self.assertEqual(response.status_code, 200)
