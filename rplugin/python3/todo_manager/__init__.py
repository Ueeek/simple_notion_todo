from notion.client import NotionClient
from notion.block import TodoBlock
from notion.block import PageBlock
import json
import pynvim
import os
from typing import List,Dict,Any


_command_prefix="NotionTodo"

@pynvim.plugin
class TodoAPI:
    keys:Dict=dict()
    nvim:pynvim.Nvim
    client:NotionClient
    page:Any
    todo_list:List
    view_window_id:int

    def __init__(self,nvim:pynvim.Nvim):
        self.nvim=nvim
        self.set_api_key()
        self.client = NotionClient(token_v2=self.keys["TOKEN_V2"])
        self.page = self.client.get_block(self.keys["PAGE_URL"])
        self.update_list()

        self.view_window_id=-1


    def echo(self,msg:str):
        self.nvim.command('echo "{}"'.format(msg))

    def update_list(self):
        self.page = self.client.get_block(self.keys["PAGE_URL"])
        self.todo_list=self.get_members()


    def set_api_key(self):
        keys=["TOKEN_V2","PAGE_URL"]
        for key in keys:
            if os.getenv("NOTION_TODO_{}".format(key)) is None:
                raise Exception("Required Environment variables are missing")
            else:
                self.keys[key]=os.getenv("NOTION_TODO_{}".format(key))

    def get_members(self)->List:
        cur_todos=[(child.title,child.checked) for child in self.page.children if isinstance(child,TodoBlock)]
        
        return cur_todos

    def show_list(self):
        self.echo("show_list called")
        self.nvim.command('setlocal modifiable')
        self.nvim.current.buffer[:]=[]
        for todo,checked in self.todo_list:
            if checked:
                preseq="[x]:"
            else:
                preseq="[ ]:"
            self.nvim.current.buffer.append(preseq+todo)
        self.nvim.current.window.cursor=(1,1)
        self.nvim.command('setlocal nomodifiable')

    @pynvim.command(_command_prefix+"AddTodo",nargs=1,sync=True)
    def add_new_todo(self,title):
        if len(title)==0:
            raise Exception("tilte is required")
        else:
            self.page.children.add_new(TodoBlock,title=title[0])
        self.echo("add {}".format(title[0]))
        self.update_list()
        #self.show_list()
        self.todoList()

    def get_ith_todo(self,idx):
        find_idx=-1
        for child in self.page.children:
            if isinstance(child,TodoBlock):
                find_idx+=1
            if find_idx==idx:
                return child
        return None

    @pynvim.command(_command_prefix+"DeleteTodo",nargs=1,sync=True)
    def delete_todo(self,idx):
        idx=int(idx[0])
        child = self.get_ith_todo(idx)
        if child is None:
            raise Exception("{}-th todo-item is not found".format(str(idx)))
        removing_title=child.title
        child.remove()
        self.echo("remove {}".format(removing_title))
        self.update_list()
        #self.show_list()
        self.todoList()


    @pynvim.command(_command_prefix+"ToggleTodo",nargs=1,sync=True)
    def toggle_checked(self,idx):
        idx=int(idx[0])
        child = self.get_ith_todo(idx)
        if child is None:
            raise Exception("{}-th todo-item is not found".format(str(idx)))
        child.checked = not child.checked
        self.update_list()
        #self.show_list()
        self.todoList()
        self.echo("Toggle {}".format(child.title))

    @pynvim.command(_command_prefix+"TodoList",sync=True)
    def todoList(self):
        cur_win_id = self.nvim.call('win_getid')
        if cur_win_id==self.view_window_id:
            self.echo("you already todolist")
        elif self.nvim.call('win_gotoid',self.view_window_id):#fail=>ret False
            self.echo("move to todolist id:{}".format(self.view_window_id))
            #move to already-opened window
        else:
            self.nvim.command('setlocal splitright')
            self.nvim.command('vnew')
            self.nvim.command('vertical resize 30')
            self.nvim.command('setlocal buftype=nofile bufhidden=hide nolist nonumber nomodifiable wrap')
            self.view_window_id = self.nvim.call('win_getid')
            self.echo("create todolist win_id={}".format(self.view_window_id))
        self.show_list()
