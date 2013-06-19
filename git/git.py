import os

from datetime import datetime

from osv import osv
from osv import fields

import openerp

from pygit2 import GIT_SORT_TIME
from pygit2 import Repository


class git_commit(osv.osv):

    _name = 'git.commit'
    _description = 'Git commit.'
    _columns = {
        'author': fields.char('Author', size=64, required=True),
        'email': fields.char('Email', size=64, required=True),
        'date': fields.datetime('Date', required=True),
        'description': fields.char('Description', size=64, required=True),
        'repo_id': fields.many2one('git.repository', 'Repository',
                                   ondelete='cascade')
    }


git_commit()


class git_repository(osv.osv):

    _name = 'git.repository'
    _description = 'Git repository.'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
    }

    @property
    def root(self):
        _root = openerp.tools.config.get('git_root')
        if not _root:
            raise osv.except_osv('Root Config', 'Not set.')
        if not os.path.exists(_root):
            raise osv.except_osv('Root Path not Exist', _root)
        return _root

    def get_repo_path(self, repo_name):
        path = os.path.join(self.root, repo_name, '.git')
        if not os.path.exists(path):
            raise osv.except_osv('Repo Path not Exist', path)
        return path

    def get_repo(self, repo_name):
        return Repository(self.get_repo_path(repo_name)) 

    def get_commits(self, repo_name):
        repo = self.get_repo(repo_name)
        for commit in repo.walk(repo.head.oid, GIT_SORT_TIME):
            yield commit

    def update_commits(self, cr, uid, repo):
        # get commit pool
        _git_commit = self.pool.get('git.commit')
        # iter and add commits
        for commit in self.get_commits(repo.name):
            # insert new commit in db
            values = {
                'author': commit.author.name,
                'email': commit.author.email,
                'date': datetime.fromtimestamp(commit.commit_time),
                'description': commit.message.strip(),
                'repo_id': repo.id
            }
            # insert or quit if failed
            if not _git_commit.create(cr, uid, values):
                return False

    def delete_commits(self, cr, uid, ids):
        # little check
        if not ids:
            return True
        # delete all
        _git_commit = self.pool.get('git.commit')
        ids = _git_commit.search(cr, uid, [('repo_id', 'in', ids)])
        return _git_commit.unlink(cr, uid, ids)

    def create(self, cr, uid, values, context=None):
        _id = super(git_repository, self).create(cr, uid, values,
                                                   context=context)
        repo = self.browse(cr, uid, _id)
        self.update_commits(cr, uid, repo)
        return _id

    def write(self, cr, uid, ids, values, context=None):
        # update repo first
        if not super(git_repository, self).write(cr, uid, ids, values,
                                                 context=context):
            return False
        # removes previous
        if not self.delete_commits(cr, uid, ids):
            return False
        # update commits for the given repositories
        for repo in self.browse(cr, uid, ids):
            if not self.update_commits(cr, uid, repo):
                return False
        # common result
        return ids


git_repository()
