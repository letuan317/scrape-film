import argparse
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from alive_progress import alive_bar
from termcolor import colored, cprint
import time
import json
import os

PATH_RESOURCE = "movies"


def create_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)


def format_class(class_name):
    return class_name.replace(" ", ".")


class Film:
    def __init__(self,url_link):
        create_directory(PATH_RESOURCE)
        self.url_link = url_link

    def run(self):
        options = webdriver.FirefoxOptions()
        # options.add_argument('-headless')
        options.add_argument('--mute-audio')
        options.set_capability('moz:firefoxOptions', {
                               'prefs': {'media.volume_scale': '0.0'}})
        options.add_argument(f"--app={self.url_link}")
        options.add_argument("--incognito")

        self.driver = webdriver.Firefox(options=options)
        self.driver.set_window_size(600, 800)

        self.driver.get(self.url_link)

        info_json = self.get_info()
        if not self.btn_watch():
            return False
        if not self.select_TM():
            return False

        data_movies = []
        path_data_file = "movie.json"

        episodelist = self.get_episodelist()
        with alive_bar(len(episodelist)) as bar:
            for episode_link in episodelist:
                bar()
                print(colored("Checking on", "blue"),
                      colored(episode_link, "yellow"))
                self.driver.get(episode_link)
                self.driver.implicitly_wait(5)
                movie_src = None
                if self.select_server_list():
                    movie_src = self.get_movie_link()
                data_movies.append({
                    "link": episode_link,
                    "movie": movie_src
                })

        if info_json != None:
            if "name" in info_json:
                print(info_json["name"])
                path_folder = os.path.join(
                    PATH_RESOURCE, info_json["name"].replace(" ", ""))
                create_directory(path_folder)
                path_data_file = os.path.join(
                    path_folder, info_json["name"].replace(" ", "")+".json")

        with open(path_data_file, "w") as fw:
            json.dump({"info": info_json, "movies": data_movies}, fw)
        self.driver.quit()
        if os.path.exists(path_folder):
            convert2fie(path_data_file, os.path.join(path_folder, "links.txt"))

    def get_info(self):
        cprint("Getting Information...", "blue")
        try:
            title = self.driver.find_element(
                By.CLASS_NAME, format_class("title fr")).text
            year = self.driver.find_element(
                By.CLASS_NAME, format_class("year")).text
            name = self.driver.find_element(
                By.CLASS_NAME, format_class("name2 fr")).text.replace(year, "")

            return {
                "title": title,
                "name": name,
                "year": year
            }
        except Exception as e:
            cprint(e)
            return None

    def btn_watch(self):
        cprint("Clicking on 'Xem phim'...", "blue")
        try:
            self.driver.find_element(
                By.CLASS_NAME, format_class("btn-watch")).click()
            time.sleep(10)
            return True
        except Exception as e:
            cprint(e, "red")
            return False

    def select_TM(self):
        cprint("Select Thuyet Minh...", "blue")
        content = self.driver.find_element(By.ID, "content")
        servers = content.find_elements(By.CLASS_NAME, "server")
        for server in servers:
            label = server.find_element(By.CLASS_NAME, "label").text
            if label == "Thuyết Minh":
                cprint("Found container Thuyet Minh")
                return server
        cprint("Can't find container Thuyet Minh", "red")
        return None

    def get_episodelist(self):
        cprint("Getting episode list", "blue")
        content = self.driver.find_element(By.ID, "content")
        episodelist_lis = content.find_element(
            By.CLASS_NAME, "episodelist").find_elements(By.TAG_NAME, "li")

        episodelist = []
        for li in episodelist_lis:
            episodelist.append(li.find_element(
                By.TAG_NAME, "a").get_attribute("href"))
        print(colored("Found", "green"), colored(
            len(episodelist_lis), "yellow"), colored("movies", "green"))

        return episodelist

    def select_server_list(self):
        cprint("Selecting Server R.PRO", "blue")
        server_list_id = self.driver.find_element(By.ID, "list-server")
        try:
            rpro_server = server_list_id.find_element(
                By.XPATH, "//span[@title='R.PRO']")
            rpro_server.click()
            time.sleep(5)
            return True
        except:
            cprint("Could not find server R.PRO", "red")
            return False

    def get_movie_link(self):
        cprint("Getting movie link", "blue")
        movie_src = None
        try:
            media = self.driver.find_element(By.ID, "media")
            iframe = media.find_element(By.TAG_NAME, "iframe")
            movie_src = iframe.get_attribute("src")
            print(colored("Found movie:", "green"),
                  colored(movie_src, "yellow"))
        except:
            cprint("Can't find movie src", "red")
        return movie_src


def convert2fie(filepath_load, filepath_write):
    with open(filepath_load, "r") as f:
        data = json.load(f)
    movies = data["movies"]
    with open(filepath_write, "w") as fw:
        for item in movies:
            print(item)
            if item["movie"] != None:
                fw.write(item["movie"]+"\n")


if __name__ == "__main__":
    Film(sys.argv[1])
    