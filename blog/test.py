from django.test import TestCase, Client
from bs4 import BeautifulSoup as bs
from .models import Post, Category, Tag
from django.contrib.auth.models import User


class TestView(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.test_user1 = User.objects.create_user(
            username='tester1',
            password='passwd',
        )
        self.test_user2 = User.objects.create_user(
            username='tester2',
            password='passwd',
        )
        self.test_user2.is_staff = True
        self.test_user2.save()

        self.category_programming = Category.objects.create(
            name='programming', slug='programming'
        )
        self.category_music = Category.objects.create(
            name='music', slug='music'
        )

        self.tag_python_kr = Tag.objects.create(
            name='파이썬 공부',
            slug='파이썬-공부'
        )

        self.tag_python = Tag.objects.create(
            name='python',
            slug='python'
        )

        self.tag_hello = Tag.objects.create(
            name='hello',
            slug='hello'
        )

        self.post_001 = Post.objects.create(
            title='test_001',
            content='qwerty',
            author=self.test_user1,
            category=self.category_programming
        )

        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='test_002',
            content='ㅁㄴㅇㄹ',
            author=self.test_user2,
            category=self.category_music
        )

        self.post_003 = Post.objects.create(
            title='test_003',
            content='뭐쓰징',
            author=self.test_user2
        )

        self.post_003.tags.add(self.tag_python)
        self.post_003.tags.add(self.tag_python_kr)

    def nav_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo = navbar.find('a', text='인태의 뻘로그')
        self.assertEqual(logo.attrs['href'], '/')

        home = navbar.find('a', text='Home')
        self.assertEqual(home.attrs['href'], '/')

        blog = navbar.find('a', text='Blog')
        self.assertEqual(blog.attrs['href'], '/blog/')

        about_me = navbar.find('a', text='About Me')
        self.assertEqual(about_me.attrs['href'], '/about_me/')

    def category_area_test(self, soup):
        categories_area = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_area.text)
        self.assertIn(f'{self.category_programming} ({self.category_programming.post_set.count()})',
                      categories_area.text)
        self.assertIn(f'{self.category_music} ({self.category_music.post_set.count()})',
                      categories_area.text)
        self.assertIn(f'미분류 ({Post.objects.filter(category=None).count()})', categories_area.text)

    def test_no_post(self):
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = bs(response.content, 'html.parser')
        self.nav_test(soup)
        self.assertIn('Blog', soup.title.text)

        # 2.2 "아직 게시물이 없습니다" 출력
        main_area = soup.find('div', id="main-area")
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_index(self):
        self.assertEqual(Post.objects.count(), 3)
        # 1.1 포스트 목록을 연다
        response = self.client.get('/blog/')
        # 1.2 정상적으로 로드
        self.assertEqual(response.status_code, 200)
        # 1.3 페이지 타이틀이 Blog다
        soup = bs(response.content, 'html.parser')
        self.assertIn('Blog', soup.title.text)

        self.nav_test(soup)
        self.category_area_test(soup)

        main_area = soup.find('div', id="main-area")
        # 3.4 "아직 게시물이 없습니다" 없음
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        show_post_001 = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, show_post_001.text)
        self.assertIn(self.post_001.category.name, show_post_001.text)
        self.assertIn(self.tag_hello.name, show_post_001.text)
        self.assertNotIn(self.tag_python_kr.name, show_post_001.text)
        self.assertNotIn(self.tag_python_kr.name, show_post_001.text)

        show_post_002 = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, show_post_002.text)
        self.assertIn(self.post_002.category.name, show_post_002.text)
        self.assertNotIn(self.tag_hello.name, show_post_002.text)
        self.assertNotIn(self.tag_python_kr.name, show_post_002.text)
        self.assertNotIn(self.tag_python_kr.name, show_post_002.text)

        show_post_003 = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, show_post_003.text)
        self.assertIn('미분류', show_post_003.text)
        self.assertIn(self.tag_hello.name, show_post_001.text)
        self.assertNotIn(self.tag_python_kr.name, show_post_001.text)
        self.assertNotIn(self.tag_python_kr.name, show_post_001.text)
        self.assertNotIn(self.tag_hello.name, show_post_001.text)
        self.assertIn(self.tag_python_kr.name, show_post_001.text)
        self.assertIn(self.tag_python_kr.name, show_post_001.text)

        self.assertIn(self.post_001.author.username, main_area.text)
        self.assertIn(self.post_002.author.username, main_area.text)

    def test_post(self):
        self.assertEqual(Post.objects.count(), 3)
        # 1.2 url이 /blog/1/'이다
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2 첫 포스트 상세 페이지
        # 2.1 로 갔을 때 정상
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = bs(response.content, 'html.parser')
        # 2.2 인덱스 페이지와 똑같은 네비바
        self.nav_test(soup)
        header_area = soup.find('div', id='header-area')
        self.assertIn(f'ㆍ {self.category_programming}',
                      header_area.text)
        # 2.3 첫 포스트 제목이 타이틀에 있음
        # self.assertIn(post_001.title, soup.title)
        # 2.4 첫 포스트 제목이 헤더 영역에 있음
        header_area = soup.find('div', id="header-area")
        self.assertIn(self.post_001.title, header_area.text)
        self.assertIn(self.post_001.category.name, header_area.text)
        # 2.5 첫 포스트 작성자가 포스트 영역에 있음
        self.assertIn(self.test_user1.username, header_area.text)
        # 2.6 첫 포스트 글이 포스트 영역에 있음
        post_area = soup.find('div', id="post-area")
        self.assertIn(self.post_001.content, post_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url(), {}, True)
        self.assertEqual(response.status_code, 200)

        soup = bs(response.content, 'html.parser')
        self.nav_test(soup)
        self.category_area_test(soup)

        header_area = soup.find('div', id="header-area")

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = bs(response.content, 'html.parser')
        self.nav_test(soup)
        self.category_area_test(soup)

        self.assertIn(self.tag_hello.name, soup.span)
        main_area = soup.find('div', id="main-area")
        self.assertIn(f'#{self.tag_hello.name}', main_area.text)
        self.assertIn()

    def test_create_post_logout(self):
        response = self.client.get('blog/create_post')
        self.assertNotEqual(response.status_code, 200)

    def test_create_post(self):
        self.client.login(username='tester1', password='passwd')
        response = self.client.get('blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='tester2', password='passwd')
        soup = bs(response.content, 'html.parser')
        response = self.client.get('blog/create_post/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual('Create Post | Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('새 글 등록하기', main_area.text)

        tags_str_input=main_area.find('input',id='id_tags_str')
        self.assertTrue(tags_str_input)


        self.client.post(
            'blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': 'Post From 페이지를 만듭시다',
                'tags_str':'new tag; 한글 태그, '
            }
        )

        last_post = Post.objects.last()
        self.assertEqual(last_post.title, 'Post Form 만들기')
        self.assertEqual(last_post.username, 'tester2')
        self.assertEqual(last_post.content, 'Post Form 페이지를 만듭시다')

        self.assertEqual(last_post.tags.count(),3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertTrue(Tag.objects.get(name='python'))
        self.assertEqual(Tag.objects.count(),5)

    def test_modify_post(self):
        edit_post_url = f'blog/modify_post/{self.post_003.pk}/'
        # 로그인 안돼있을 때 접근
        response=self.client.get(edit_post_url)
        self.assertNotEqual(response.status_code, 200)
        # 로그인 했지만 작성자 아님
        self.assertNotEqual(self.post_003, self.test_user1)
        self.client.login(username='tester01',password='passwd')
        response = self.client.get(edit_post_url)
        self.assertNotEqual(response.status_code, 200)
        # 작성자가 접근
        self.assertEqual(self.post_003.username, self.test_user2)
        self.client.login(username='tester02', password='passwd')
        response = self.client.get(edit_post_url)
        self.assertEqual(response.status_code, 200)
        soup = bs(response.content, 'html.parser')

        self.assertEqual('글 수정하기 | Blog',soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('글 수정하기',main_area.text)

        tag_str_input=main_area.find('input',id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부; python',tag_str_input.attrs['value'])

        response=self.client.post(
            edit_post_url,
            {
                'title':'글 수정',
                'content':'뭐',
                'category':self.category_music.pk,
                'tags_str':'파이썬 공부; 한글 태그, something'
            },
            follow=True
        )
        soup=bs(response.content,'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('글 수정',main_area.text)
        self.assertIn('뭐',main_area.text)
        self.assertIn(self.category_music.name, main_area.text)

        self.assertIn('파이썬 공부',main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('something', main_area.text)
        self.assertNotIn('python', main_area.text)