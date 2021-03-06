import StringIO

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

from euscan_accounts.helpers import get_profile

from djeuscan.tests import SystemTestCase
from djeuscan.tests.euscan_factory import PackageFactory, setup_maintainers, \
    setup_herds, setup_categories, setup_overlays


class PagesTest(SystemTestCase):
    """
    Test main pages
    """

    def test_index(self):
        response = self.get("index")
        self.assertEqual(response.status_code, 200)

    def test_world(self):
        response = self.get("world")
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.get("about")
        self.assertEqual(response.status_code, 200)

    def test_global_feed(self):
        response = self.get("global_feed")
        self.assertEqual(response.status_code, 200)

    def test_api(self):
        response = self.get("api")
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        response = self.get("accounts_index")
        self.assertEqual(response.status_code, 302)

        with self.login():
            response = self.get("accounts_index")
            self.assertEqual(response.status_code, 200)


class PackageTests(SystemTestCase):
    def setUp(self):
        super(PackageTests, self).setUp()
        self.package = PackageFactory.create()

    def test_package(self):
        response = self.get("package", category=self.package.category,
                            package=self.package.name)
        self.assertEqual(response.status_code, 200)

    def test_favourite(self):
        response = self.get("package", category=self.package.category,
                            package=self.package.name)
        self.assertEqual(response.status_code, 200)

        self.assertNotIn("Watch", response.content)

        with self.login():
            response = self.get("package", category=self.package.category,
                                package=self.package.name)
            self.assertEqual(response.status_code, 200)

            user = response.context["user"]
            self.assertEquals(get_profile(user).categories.count(), 0)

            self.assertIn("Watch", response.content)
            self.post("favourite_package", category=self.package.category,
                      package=self.package.name)

            self.assertEquals(get_profile(user).packages.count(), 1)

            response = self.get("accounts_packages")
            self.assertEqual(response.status_code, 200)

            self.assertIn(self.package.name, response.content)

            self.post("unfavourite_package", category=self.package.category,
                      package=self.package.name)
            self.assertEquals(get_profile(user).packages.count(), 0)


class SectionTests(SystemTestCase):
    def _check_table(self, response, items, attr=None):
        soup = BeautifulSoup(response.content)
        rows = soup.findAll("tr")

        # the -1 is for the table heading
        self.assertEqual(len(rows) - 1, len(items))

        for item in items:
            if attr:
                item_str = getattr(item, attr)
            else:
                item_str = item
            self.assertTrue(item_str in response.content)


class CategoriesTests(SectionTests):
    def setUp(self):
        super(CategoriesTests, self).setUp()
        self.categories, self.packages = setup_categories()

    def test_categories(self):
        response = self.get("categories")
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.categories)

    def test_category(self):
        category = self.categories[0]
        response = self.get("category", category=category)
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.packages[:1], attr="name")

    def test_category_feed(self):
        category = self.categories[0]
        response = self.get("category_feed", category=category)
        self.assertEqual(response.status_code, 200)

    def test_favourite(self):
        category = self.categories[0]

        response = self.get("category", category=category)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Watch", response.content)

        with self.login():
            response = self.get("category", category=category)
            self.assertEqual(response.status_code, 200)

            user = response.context["user"]
            self.assertEquals(get_profile(user).categories.count(), 0)

            self.assertIn("Watch", response.content)
            self.post("favourite_category", category=category)

            self.assertEquals(get_profile(user).categories.count(), 1)

            response = self.get("accounts_categories")
            self.assertEqual(response.status_code, 200)

            self._check_table(response, [category])

            self.post("unfavourite_category", category=category)

            self.assertEquals(get_profile(user).categories.count(), 0)


class HerdsTests(SectionTests):
    def setUp(self):
        super(HerdsTests, self).setUp()
        self.herds, self.packages = setup_herds()

    def test_herds(self):
        response = self.get("herds")
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.herds, attr="herd")

    def test_herd(self):
        herd = self.herds[0]
        response = self.get("herd", herd=herd.herd)
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.packages[:1], attr="name")

    def test_herd_feed(self):
        herd = self.herds[0]
        response = self.get("herd_feed", herd=herd.herd)
        self.assertEqual(response.status_code, 200)

    def test_favourite(self):
        herd = self.herds[0]

        response = self.get("herd", herd=herd.herd)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Watch", response.content)

        with self.login():
            response = self.get("herd", herd=herd.herd)
            self.assertEqual(response.status_code, 200)

            user = response.context["user"]
            self.assertEquals(get_profile(user).herds.count(), 0)

            self.assertIn("Watch", response.content)
            self.post("favourite_herd", herd=herd.herd)

            self.assertEquals(get_profile(user).herds.count(), 1)

            response = self.get("accounts_herds")
            self.assertEqual(response.status_code, 200)

            self._check_table(response, [herd], attr="herd")

            self.post("unfavourite_herd", herd=herd.herd)
            self.assertEquals(get_profile(user).herds.count(), 0)


class MaintainersTests(SectionTests):
    def setUp(self):
        super(MaintainersTests, self).setUp()
        self.maintainers, self.packages = setup_maintainers()

    def test_maintainers(self):
        response = self.get("maintainers")
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.maintainers, attr="name")

    def test_maintainer(self):
        maintainer = self.maintainers[0]
        response = self.get("maintainer", maintainer_id=maintainer.pk)
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.packages[:1], attr="name")

    def test_maintainer_feed(self):
        maintainer = self.maintainers[0]
        response = self.get("maintainer_feed", maintainer_id=maintainer.pk)
        self.assertEqual(response.status_code, 200)

    def test_favourite(self):
        maintainer = self.maintainers[0]

        response = self.get("maintainer", maintainer_id=maintainer.pk)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Watch", response.content)

        with self.login():
            response = self.get("maintainer", maintainer_id=maintainer.pk)
            self.assertEqual(response.status_code, 200)

            user = response.context["user"]
            self.assertEquals(get_profile(user).maintainers.count(), 0)

            self.assertIn("Watch", response.content)
            self.post("favourite_maintainer", maintainer_id=maintainer.pk)

            self.assertEquals(get_profile(user).maintainers.count(), 1)

            response = self.get("accounts_maintainers")
            self.assertEqual(response.status_code, 200)

            self._check_table(response, [maintainer], attr="name")

            self.post("unfavourite_maintainer", maintainer_id=maintainer.pk)

            self.assertEquals(get_profile(user).maintainers.count(), 0)


class OverlayTests(SectionTests):
    def setUp(self):
        super(OverlayTests, self).setUp()
        self.overlays, self.packages = setup_overlays()

    def test_overlays(self):
        response = self.get("overlays")
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.overlays)

    def test_overlay(self):
        overlay = self.overlays[0]
        response = self.get("overlay", overlay=overlay)
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.packages[overlay], attr="name")


class WorldScanTests(SectionTests):
    def setUp(self):
        super(WorldScanTests, self).setUp()
        for _ in range(3):
            PackageFactory.create()
        self.packages = [PackageFactory.create().name for _ in range(3)]

    def test_world_scan_packages(self):
        response = self.post("world_scan",
                             data={"packages": "\n".join(self.packages)})
        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.packages)

    def test_world_scan_world(self):
        world_file = StringIO.StringIO()
        world_file.write("\n".join(self.packages))
        world_file.name = "world"
        world_file.read = world_file.getvalue

        response = self.post("world_scan", data={"world": world_file})

        self.assertEqual(response.status_code, 200)

        self._check_table(response, self.packages)
