from notion.client import NotionClient
from notion.block import TodoBlock
from notion.block import PageBlock
import json


class TodoManager:
    token_v2=None
    page_url=None
    client=None
    page=None

    def __init__(self):
        self.read_json()
        self.client = NotionClient(token_v2=self.token_v2)
        self.page = self.client.get_block(self.page_url)
        print("page=>",self.page)

    def read_json(self,file_path="../../../simple_notion_todo_env.json"):
        with open(file_path) as file:
            data = json.load(file)

        self.token_v2 = data["token_v2"]
        self.page_url= data["page_url"]

    def get_members(self):
        cur_todos=[child.title for child in self.page.children]
        print(cur_todos)

    def add_new_todo(self,title):
        print("add called=>",title)
        self.page.children.add_new(TodoBlock,title=title)

    def delete_todo(self,idx):
        child = self.page.children[idx]
        child.remove()

    def toggle_checked(self,idx):
        child = self.page.children[idx]
        child.checked = not child.checked




C = TodoManager()
C.add_new_todo("add from class")
C.get_members()
C.toggle_checked(0)
C.delete_todo(0)

